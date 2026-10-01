"""Scoped local-pilot checks; these are not full specification assessments."""
from __future__ import annotations

import copy
import json
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

from reference.tse_pilot.contracts import (
    ContractError, SCHEMA, canonical, decode, validate, validate_binding, validate_proposal,
)
from reference.tse_pilot.runtime import (
    Conflict, Denied, Host, Principal, Provider, SimulatedCrash, connection, record,
)

ROOT = Path(__file__).resolve().parents[1]


class CountingProvider(Provider):
    def __init__(self, path):
        super().__init__(path)
        self.calls = 0
        self.lock = threading.Lock()

    def publish(self, *args, **kwargs):
        with self.lock:
            self.calls += 1
        return super().publish(*args, **kwargs)


class PilotCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="tse-pilot-test-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.now = datetime.now(timezone.utc)
        self.provider = CountingProvider(self.directory / "provider.sqlite3")
        self.host_path = self.directory / "host.sqlite3"
        self.host = Host(self.host_path, self.provider, clock=lambda: self.now)
        self.alice = Principal("alice", "tenant-a")
        self.host.set_permission(self.alice, "board", True)

    def prepare(self, content="Synthetic update"):
        proposal = self.host.propose(self.alice, "board", content)
        ref = {"id": proposal["id"], "version": proposal["version"]}
        decision = self.host.decide(self.alice, ref, "approve", "decision-" + proposal["id"])
        return proposal, ref, decision

    def reserve(self):
        proposal, ref, decision = self.prepare()
        return proposal, self.host.reserve(self.alice, ref, decision["id"])

    def stored(self, kind):
        with connection(self.host_path) as db:
            return [decode(row["payload"]) for row in db.execute(
                "SELECT payload FROM records WHERE kind=? ORDER BY sequence", (kind,))]

    def tamper(self, kind, transform):
        with connection(self.host_path) as db:
            row = db.execute("SELECT sequence,payload FROM records WHERE kind=? ORDER BY sequence DESC LIMIT 1", (kind,)).fetchone()
            value = json.loads(row["payload"])
            transform(value)
            db.execute("UPDATE records SET payload=? WHERE sequence=?", (canonical(value), row["sequence"]))

    def test_happy_path_requires_separate_readback(self):
        _, op = self.reserve()
        pending = self.host.dispatch(self.alice, op)
        self.assertEqual(pending["status"], "pending-verification")
        done = self.host.reconcile(self.alice, op)
        self.assertEqual(done["status"], "completed")
        self.assertEqual(self.provider.count(), 1)
        self.assertIn("No delivery or content-truth", done["limitations"])

    def test_generated_records_cover_every_schema_family(self):
        _, op = self.reserve()
        self.host.dispatch(self.alice, op)
        self.host.reconcile(self.alice, op)
        seen = set()
        with connection(self.host_path) as db:
            for row in db.execute("SELECT payload FROM records"):
                value = decode(row["payload"])
                seen.add(value["kind"])
        value = self.provider.lookup(self.alice.scope, op)
        validate(value)
        seen.add(value["kind"])
        self.assertEqual(seen, set(SCHEMA["$defs"]))

    def test_stale_approval_does_not_transfer_to_revision(self):
        _, ref, decision = self.prepare()
        newer = self.host.propose(self.alice, "board", "Changed content", previous=ref)
        with self.assertRaises(Denied):
            self.host.reserve(self.alice, ref, decision["id"])
        new_ref = {"id": newer["id"], "version": newer["version"]}
        with self.assertRaises(ContractError):
            self.host.reserve(self.alice, new_ref, decision["id"])
        self.assertEqual(self.provider.calls, 0)

    def test_rejected_proposal_cannot_dispatch(self):
        proposal = self.host.propose(self.alice, "board", "Rejected")
        ref = {"id": proposal["id"], "version": proposal["version"]}
        decision = self.host.decide(self.alice, ref, "reject", "reject-1")
        with self.assertRaises(Denied):
            self.host.reserve(self.alice, ref, decision["id"])

    def test_decision_redelivery_is_idempotent(self):
        _, ref, decision = self.prepare()
        repeated = self.host.decide(self.alice, ref, "approve", decision["id"])
        self.assertEqual(repeated, decision)
        self.assertEqual(len(self.stored("ApprovalDecision")), 1)
        with self.assertRaises(Conflict):
            self.host.decide(self.alice, ref, "reject", decision["id"])

    def test_expired_proposal_cannot_receive_new_decision(self):
        proposal = self.host.propose(self.alice, "board", "Expires", lifetime=1)
        self.now += timedelta(seconds=2)
        with self.assertRaises(Denied):
            self.host.decide(self.alice, {"id": proposal["id"], "version": "1"}, "approve", "expired")

    def test_denial_is_persisted_without_grant(self):
        _, ref, decision = self.prepare()
        self.host.set_permission(self.alice, "board", False)
        with self.assertRaises(Denied):
            self.host.reserve(self.alice, ref, decision["id"])
        self.assertEqual(self.stored("AuthorizationDecision")[-1]["result"], "deny")
        self.assertEqual(self.stored("ExecutionGrant"), [])

    def test_revocation_after_queue_blocks_dispatch(self):
        _, op = self.reserve()
        self.host.set_permission(self.alice, "board", False)
        with self.assertRaises(Denied):
            self.host.dispatch(self.alice, op)
        self.assertEqual(self.provider.calls, 0)
        self.assertEqual(self.host.receipt(self.alice, op)["status"], "blocked")

    def test_expired_grant_blocks_dispatch_but_not_historical_read(self):
        _, op = self.reserve()
        self.now += timedelta(hours=1)
        with self.assertRaises(Denied):
            self.host.dispatch(self.alice, op)
        self.assertEqual(self.host.receipt(self.alice, op)["effectKnowledge"], "none")
        self.assertEqual(self.provider.calls, 0)

    def test_lost_response_reopens_and_reconciles_one_effect(self):
        _, op = self.reserve()
        self.assertEqual(self.host.dispatch(self.alice, op, fault="lost-response")["effectKnowledge"], "unknown")
        reopened = Host(self.host_path, Provider(self.provider.path))
        self.assertEqual(reopened.receipt(self.alice, op)["status"], "pending-verification")
        self.assertEqual(reopened.reconcile(self.alice, op)["status"], "completed")
        reopened.dispatch(self.alice, op)
        self.assertEqual(self.provider.count(), 1)

    def test_unavailable_lookup_preserves_unknown(self):
        _, op = self.reserve()
        self.host.dispatch(self.alice, op, fault="lost-response")
        self.provider.lookup_available = False
        receipt = self.host.reconcile(self.alice, op)
        self.assertEqual(receipt["verificationState"], "unavailable")
        self.assertEqual(receipt["effectKnowledge"], "unknown")
        self.host.dispatch(self.alice, op)
        self.assertEqual(self.provider.calls, 1)

    def test_new_unavailability_preserves_prior_observation(self):
        _, op = self.reserve()
        self.host.dispatch(self.alice, op)
        self.host.reconcile(self.alice, op)
        self.provider.lookup_available = False
        receipt = self.host.reconcile(self.alice, op)
        self.assertEqual(receipt["effectKnowledge"], "observed")
        self.assertEqual(receipt["verificationState"], "unavailable")
        self.assertEqual(len(self.stored("VerificationRecord")), 2)

    def test_wrong_readback_cannot_verify(self):
        _, op = self.reserve()
        self.host.dispatch(self.alice, op)
        effect = self.provider.lookup(self.alice.scope, op)
        effect["target"] = "different-board"
        self.provider.lookup = lambda scope, operation: effect
        receipt = self.host.reconcile(self.alice, op)
        self.assertEqual(receipt["status"], "contradicted")
        self.assertEqual(self.stored("VerificationRecord")[-1]["effectId"], None)

    def test_cross_scope_paths_are_denied(self):
        _, op = self.reserve()
        for caller in (Principal("alice", "tenant-b"), Principal("bob", "tenant-a")):
            for method in (self.host.receipt, self.host.dispatch, self.host.reconcile):
                with self.subTest(caller=caller, method=method.__name__), self.assertRaises(Denied):
                    method(caller, op)
        self.assertEqual(self.provider.calls, 0)

    def test_two_workers_dispatch_only_once(self):
        _, op = self.reserve()
        def dispatch(_):
            return Host(self.host_path, self.provider).dispatch(self.alice, op)
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(dispatch, range(2)))
        self.assertEqual(self.provider.calls, 1)
        self.assertEqual(self.provider.count(), 1)

    def test_two_workers_reserve_same_operation(self):
        _, ref, decision = self.prepare()
        def reserve(_):
            return Host(self.host_path, self.provider).reserve(self.alice, ref, decision["id"])
        with ThreadPoolExecutor(max_workers=2) as pool:
            operations = list(pool.map(reserve, range(2)))
        self.assertEqual(operations[0], operations[1])
        self.assertEqual(len(self.stored("OperationRecord")), 1)

    def test_unknown_equivalent_replacement_is_blocked(self):
        _, op = self.reserve()
        self.host.dispatch(self.alice, op, fault="lost-response")
        _, ref, decision = self.prepare()
        with self.assertRaises(Conflict):
            self.host.reserve(self.alice, ref, decision["id"])
        self.assertEqual(self.provider.calls, 1)

    def test_completed_publication_allows_explicit_new_occurrence(self):
        _, op = self.reserve()
        self.host.dispatch(self.alice, op)
        self.host.reconcile(self.alice, op)
        _, ref, decision = self.prepare()
        next_op = self.host.reserve(self.alice, ref, decision["id"])
        self.host.dispatch(self.alice, next_op)
        self.assertNotEqual(op, next_op)
        self.assertEqual(self.provider.count(), 2)

    def test_provider_repeated_key_checks_parameters(self):
        _, op = self.reserve()
        self.host.dispatch(self.alice, op)
        effect = self.provider.lookup(self.alice.scope, op)
        self.provider.publish(effect)
        changed = {**effect, "content": "Different content"}
        with self.assertRaises(Conflict):
            self.provider.publish(changed)
        self.assertEqual(self.provider.count(), 1)

    def test_crash_before_provider_blocks_blind_replay(self):
        _, op = self.reserve()
        with self.assertRaises(SimulatedCrash):
            self.host.dispatch(self.alice, op, fault="before-provider")
        restarted = Host(self.host_path, self.provider)
        restarted.dispatch(self.alice, op)
        self.assertEqual(self.provider.calls, 0)
        receipt = restarted.reconcile(self.alice, op)
        self.assertEqual(receipt["effectKnowledge"], "unknown")
        self.assertEqual(receipt["status"], "pending-verification")

    def test_child_process_exits_after_provider_commit(self):
        _, op = self.reserve()
        program = """
import sys
from reference.tse_pilot.runtime import Host, Provider, Principal
h = Host(sys.argv[1], Provider(sys.argv[2]))
h.dispatch(Principal("alice", "tenant-a"), sys.argv[3], fault="after-provider")
"""
        child = subprocess.run([sys.executable, "-B", "-c", program, str(self.host_path),
                                str(self.provider.path), op], cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertNotEqual(child.returncode, 0)
        self.assertIn("SimulatedCrash", child.stderr)
        self.assertEqual(self.provider.count(), 1)
        restarted = Host(self.host_path, self.provider)
        restarted.dispatch(self.alice, op)
        self.assertEqual(self.provider.calls, 0)
        self.assertEqual(restarted.reconcile(self.alice, op)["status"], "completed")

    def test_failed_reservation_transaction_never_invokes_provider(self):
        _, ref, decision = self.prepare()
        with connection(self.host_path) as db:
            db.execute("""CREATE TRIGGER fail_reservation BEFORE INSERT ON records
                WHEN NEW.kind='OperationRecord' BEGIN SELECT RAISE(ABORT,'fixture fault'); END""")
        with self.assertRaises(sqlite3.IntegrityError):
            self.host.reserve(self.alice, ref, decision["id"])
        self.assertEqual(self.provider.calls, 0)
        self.assertEqual(self.stored("ExecutionGrant"), [])

    def test_outcome_persistence_failure_leaves_reconcilable_reservation(self):
        _, op = self.reserve()
        with connection(self.host_path) as db:
            db.execute("""CREATE TRIGGER fail_outcome BEFORE INSERT ON records
                WHEN NEW.kind='ExecutionAttempt' AND NEW.version='3'
                BEGIN SELECT RAISE(ABORT,'fixture fault'); END""")
        with self.assertRaises(sqlite3.IntegrityError):
            self.host.dispatch(self.alice, op)
        self.assertEqual(self.provider.count(), 1)
        restarted = Host(self.host_path, self.provider)
        restarted.dispatch(self.alice, op)
        self.assertEqual(self.provider.calls, 1)
        self.assertEqual(restarted.reconcile(self.alice, op)["status"], "completed")

    def test_corrupt_stored_proposal_blocks_dispatch(self):
        _, op = self.reserve()
        self.tamper("ActionProposal", lambda value: value.update(content="Mutated"))
        with self.assertRaises(ContractError):
            self.host.dispatch(self.alice, op)
        self.assertEqual(self.provider.calls, 0)

    def test_grant_operation_substitution_blocks_dispatch(self):
        _, op = self.reserve()
        self.tamper("ExecutionGrant", lambda value: value.update(operationId="different"))
        with self.assertRaises(ContractError):
            self.host.dispatch(self.alice, op)
        self.assertEqual(self.provider.calls, 0)

    def test_stored_unknown_schema_blocks_dispatch(self):
        _, op = self.reserve()
        self.tamper("OperationRecord", lambda value: value.update(schemaVersion="future"))
        with self.assertRaises(ContractError):
            self.host.dispatch(self.alice, op)

    def test_separate_stores_required(self):
        with self.assertRaises(ValueError):
            Host(self.provider.path, self.provider)

    def test_receipt_cannot_invent_verified_completion(self):
        _, op = self.reserve()
        self.tamper("ActionRecord", lambda value: value.update(status="completed", verificationState="verified"))
        with self.assertRaises(ContractError):
            self.host.receipt(self.alice, op)

    def test_wrong_operation_verification_is_rejected(self):
        _, op = self.reserve()
        self.host.dispatch(self.alice, op)
        self.host.reconcile(self.alice, op)
        self.tamper("VerificationRecord", lambda value: value.update(operationId="unrelated"))
        with self.assertRaises(ContractError):
            self.host.receipt(self.alice, op)

    def test_stored_revision_mismatch_is_rejected(self):
        _, op = self.reserve()
        self.tamper("OperationRecord", lambda value: value.update(version="999"))
        with self.assertRaises(ContractError):
            self.host.dispatch(self.alice, op)

    def test_revoked_write_permission_still_allows_owned_readback(self):
        _, op = self.reserve()
        self.host.dispatch(self.alice, op, fault="lost-response")
        self.host.set_permission(self.alice, "board", False)
        self.now += timedelta(hours=1)
        self.assertEqual(self.host.reconcile(self.alice, op)["status"], "completed")

    def test_structural_and_semantic_validation_are_separate(self):
        proposal, _, decision = self.prepare()
        forged = {**decision, "binding": "sha256:" + "0" * 64}
        validate(forged)
        with self.assertRaises(ContractError):
            validate_binding(forged, proposal)

    def test_unknown_fields_versions_types_and_bad_dates(self):
        proposal, _, _ = self.prepare()
        for changes in ({"extra": True}, {"schemaVersion": "future"}, {"version": 1},
                        {"createdAt": "2026-02-30T00:00:00Z"}, {"content": "x" * 4097},
                        {"createdAt": "2026-10-01T00:00:00"}, {"scope": ""}):
            with self.subTest(changes=changes), self.assertRaises(ContractError):
                validate({**proposal, **changes})

    def test_duplicate_keys_constants_and_oversize_json(self):
        for raw in ('{"kind":1,"kind":2}', '{"value":NaN}', '{"value":Infinity}', 'x' * 65537):
            with self.subTest(raw=raw[:40]), self.assertRaises(ContractError):
                decode(raw)

    def test_material_change_requires_rebinding(self):
        proposal, _, _ = self.prepare()
        changed = copy.deepcopy(proposal)
        changed["content"] += " altered"
        validate(changed)
        with self.assertRaises(ContractError):
            validate_proposal(changed)

    def test_explicit_fixture_files(self):
        for case in json.loads((ROOT / "schemas/fixtures/cases.json").read_text(encoding="utf-8")):
            raw = (ROOT / "schemas/fixtures" / case["file"]).read_text(encoding="utf-8")
            with self.subTest(case=case["file"]):
                if case["valid"]:
                    value = decode(raw)
                    validate_proposal(value)
                else:
                    with self.assertRaises(ContractError):
                        value = decode(raw)
                        if value["kind"] == "ActionProposal":
                            validate_proposal(value)


if __name__ == "__main__":
    unittest.main()
