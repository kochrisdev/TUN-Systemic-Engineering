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

    def execute(self, ref, lose_response=False):
        status, view = self.request("/api/reserve", ref)
        if status != 200:
            return status, view
        op = next(item for item in view["operations"] if item["id"] == next(
            p["operationId"] for p in view["proposals"] if p["proposal"]["id"] == ref["proposalId"]))
        return self.request("/api/dispatch", {"operationId": op["id"], "loseResponse": lose_response})

    def test_review_execute_readback_and_withdrawal_flow(self):
        ref = self.prepare()
        status, view = self.request("/api/decision", {**ref, "decision": "approve"})
        self.assertEqual(view["operations"], [])
        status, view = self.execute(ref, True)
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
        _, view = self.execute(ref)
        _, view = self.request("/api/reconcile", {"operationId": view["operations"][-1]["id"]})
        self.assertEqual(view["resources"][0]["status"], "withdrawn")
        self.assertEqual(view["operations"][0]["receipt"]["status"], "completed")
        self.assertEqual(view["operations"][-1]["originalId"], root)
        self.assertEqual(view["operations"][-1]["receipt"]["status"], "completed")

    def test_execute_requires_existing_exact_decision(self):
        ref = self.prepare()
        status, _ = self.execute(ref)
        self.assertEqual(status, 403)
        self.assertEqual(self.controller.host.provider.count(), 0)

    def test_queue_cancel_redelivery_and_attempted_dispatch(self):
        ref = self.prepare()
        self.request("/api/decision", {**ref, "decision": "approve"})
        status, view = self.request("/api/reserve", ref)
        self.assertEqual(status, 200)
        operation = view["operations"][0]
        self.assertIsNone(operation["receipt"])
        self.assertEqual(view["budget"]["used"], 0)
        control = {"operationId": operation["id"], "operationVersion": operation["version"]}
        self.request("/api/cancel", control)
        status, view = self.request("/api/cancel", control)
        self.assertEqual(view["controls"][0]["outcome"], "effective")
        self.assertEqual(len(view["controls"]), 1)
        status, view = self.request("/api/dispatch", {"operationId": operation["id"], "loseResponse": False})
        self.assertEqual(status, 200)
        self.assertEqual(view["operations"][0]["hostStatus"], "cancelled")
        self.assertEqual(view["budget"]["used"], 0)
        self.assertEqual(view["resources"], [])

    def test_http_dispatch_enforces_zero_budget(self):
        self.controller.host.set_dispatch_budget(self.controller.principal, 0)
        ref = self.prepare()
        self.request("/api/decision", {**ref, "decision": "approve"})
        status, _ = self.execute(ref)
        self.assertEqual(status, 403)
        status, view = self.request("/api/state")
        self.assertEqual(view["operations"][0]["dispatchObservation"], "budget-exhausted")
        self.assertEqual(view["operations"][0]["hostStatus"], "blocked")
        self.assertEqual(self.controller.host.provider.count(), 0)

    def test_late_control_does_not_change_verified_receipt(self):
        ref = self.prepare()
        self.request("/api/decision", {**ref, "decision": "approve"})
        _, view = self.execute(ref, True)
        op = view["operations"][0]
        _, view = self.request("/api/cancel", {"operationId": op["id"], "operationVersion": "1"})
        self.assertEqual(view["controls"][0]["outcome"], "too-late")
        _, view = self.request("/api/reconcile", {"operationId": op["id"]})
        self.assertEqual(view["operations"][0]["receipt"]["status"], "completed")
        self.assertEqual(view["budget"]["used"], 1)

    def test_existing_fixture_restart_never_refills_budget(self):
        ref = self.prepare()
        self.request("/api/decision", {**ref, "decision": "approve"})
        self.execute(ref)
        reopened = Controller(Path(self.temp.name))
        self.assertEqual(reopened.state()["budget"]["used"], 1)
        self.assertEqual(reopened.state()["budget"]["remaining"], 2)

    def test_legacy_execute_route_and_client_budget_override_are_rejected(self):
        status, _ = self.request("/api/execute", {"proposalId": "old", "proposalVersion": "1", "loseResponse": False})
        self.assertEqual(status, 409)
        for route, payload in (
                ("/api/reserve", {"proposalId": "x", "proposalVersion": "1", "budget": 999}),
                ("/api/dispatch", {"operationId": "x", "loseResponse": False, "budget": 999}),
                ("/api/cancel", {"operationId": "x", "operationVersion": "1", "actor": "other"})):
            status, _ = self.request(route, payload)
            self.assertEqual(status, 409)

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
        _, view = self.execute(ref)
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
