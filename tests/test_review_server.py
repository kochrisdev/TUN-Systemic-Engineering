"""Loopback boundary and host-to-design projection checks."""
import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from reference.tse_pilot.presentation import receipt_view
from reference.tse_pilot.server import Controller, make_server


class ReviewServerCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="tse-server-test-")
        self.controller = Controller(Path(self.temp.name))
        self.server = make_server(self.controller, port=0, build=Path(self.temp.name) / "no-build")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        self.temp.cleanup()

    def request(self, path, data=None, headers=None, raw=None):
        client = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        actual = {"Origin": f"http://127.0.0.1:{self.server.server_port}",
                  "X-TUN-CSRF": self.controller.token, "Content-Type": "application/json"}
        actual.update(headers or {})
        method = "GET" if data is None and raw is None else "POST"
        client.request(method, path, body=raw if raw is not None else json.dumps(data) if data is not None else None,
                       headers=actual)
        response = client.getresponse()
        status, payload = response.status, json.loads(response.read())
        client.close()
        return status, payload

    def prepare(self):
        status, view = self.request("/api/proposals", {"content": "HTTP synthetic update"})
        self.assertEqual(status, 200)
        p = view["proposals"][-1]["proposal"]
        return {"proposalId": p["id"], "proposalVersion": p["version"]}

    def test_review_execute_readback_and_withdrawal_flow(self):
        ref = self.prepare()
        status, view = self.request("/api/decision", {**ref, "decision": "approve"})
        self.assertEqual(view["operations"], [])
        status, view = self.request("/api/execute", {**ref, "loseResponse": True})
        self.assertEqual(status, 200)
        self.assertEqual(view["operations"][0]["receipt"]["status"], "pending-verification")
        root = view["operations"][0]["id"]
        status, view = self.request("/api/reconcile", {"operationId": root})
        self.assertEqual(view["operations"][0]["receipt"]["status"], "completed")
        status, view = self.request("/api/recovery", {"originalId": root, "action": "withdraw", "content": None})
        p = view["proposals"][-1]["proposal"]
        self.assertIn(root, p["target"])
        self.assertIn("resource revision 1", p["effect"])
        ref = {"proposalId": p["id"], "proposalVersion": p["version"]}
        self.request("/api/decision", {**ref, "decision": "approve"})
        _, view = self.request("/api/execute", {**ref, "loseResponse": False})
        _, view = self.request("/api/reconcile", {"operationId": view["operations"][-1]["id"]})
        self.assertEqual(view["resources"][0]["status"], "withdrawn")
        self.assertEqual(view["operations"][0]["receipt"]["status"], "completed")
        self.assertEqual(view["operations"][-1]["originalId"], root)
        self.assertEqual(view["operations"][-1]["receipt"]["status"], "completed")

    def test_execute_requires_existing_exact_decision(self):
        ref = self.prepare()
        status, _ = self.request("/api/execute", {**ref, "loseResponse": False})
        self.assertEqual(status, 403)
        self.assertEqual(self.controller.host.provider.count(), 0)

    def test_origin_token_host_and_fetch_site_boundaries(self):
        for headers in ({"Origin": "https://unrelated.invalid"}, {"X-TUN-CSRF": "wrong"},
                        {"Host": "unrelated.invalid"}, {"Sec-Fetch-Site": "cross-site"}):
            with self.subTest(headers=headers):
                status, _ = self.request("/api/proposals", {"content": "Rejected"}, headers=headers)
                self.assertEqual(status, 403)
        self.assertEqual(self.controller.state()["proposals"], [])

    def test_client_cannot_supply_actor_target_or_replacement_parameters(self):
        for extra in ("actor", "scope", "target", "permissionGranted"):
            with self.subTest(extra=extra):
                status, _ = self.request("/api/proposals", {"content": "Candidate", extra: "untrusted"})
                self.assertEqual(status, 409)
        self.assertEqual(self.controller.state()["proposals"], [])

    def test_duplicate_json_and_oversize_bodies_are_rejected(self):
        for raw in ('{"content":"one","content":"two"}', '{"content":NaN}', "x" * 32769):
            status, _ = self.request("/api/proposals", raw=raw)
            self.assertEqual(status, 409)

    def test_static_path_cannot_escape_build(self):
        status, _ = self.request("/assets/../../host.sqlite3")
        self.assertEqual(status, 404)

    def test_rejection_does_not_execute(self):
        ref = self.prepare()
        _, view = self.request("/api/decision", {**ref, "decision": "reject"})
        self.assertEqual(view["proposals"][-1]["status"], "rejected")
        self.assertEqual(view["operations"], [])

    def test_contradiction_mapping_preserves_explicit_meaning(self):
        ref = self.prepare()
        self.request("/api/decision", {**ref, "decision": "approve"})
        _, view = self.request("/api/execute", {**ref, "loseResponse": False})
        root = view["operations"][0]["id"]
        effect = self.controller.host.provider.lookup("sandbox", root)
        effect["target"] = "wrong"
        self.controller.host.provider.lookup = lambda *args: effect
        _, view = self.request("/api/reconcile", {"operationId": root})
        projected = view["operations"][0]
        self.assertEqual(projected["hostStatus"], "contradicted")
        self.assertEqual(projected["receipt"]["status"], "pending-verification")
        self.assertIn("contradicts", projected["receipt"]["summary"])


if __name__ == "__main__":
    unittest.main()
