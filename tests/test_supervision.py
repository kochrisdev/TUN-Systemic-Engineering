"""Focused queued cancellation and durable dispatch-budget checks, not full conformance."""
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor

import test_pilot
from reference.tse_pilot.contracts import ContractError, canonical
from reference.tse_pilot.runtime import Denied, Host, Principal, Provider, SimulatedCrash, connection


class SupervisionCase(unittest.TestCase):
    setUp = test_pilot.PilotCase.setUp
    prepare = test_pilot.PilotCase.prepare
    reserve = test_pilot.PilotCase.reserve
    stored = test_pilot.PilotCase.stored

    def test_cancelled_queue_never_dispatches_or_spends(self):
        _, op = self.reserve()
        control = self.host.cancel(self.alice, op, "1")
        self.assertEqual(control["outcome"], "effective")
        self.assertEqual(self.host.dispatch(self.alice, op)["status"], "cancelled")
        self.assertEqual(self.host.reconcile(self.alice, op)["status"], "cancelled")
        self.assertEqual(self.host.budget(self.alice)["used"], 0)
        self.assertEqual((self.provider.calls, self.provider.count()), (0, 0))

    def test_duplicate_cancellation_survives_restart_and_permission_revocation(self):
        _, op = self.reserve()
        first = self.host.cancel(self.alice, op, "1")
        self.host.set_permission(self.alice, "board", False)
        restarted = Host(self.host_path, self.provider)
        self.assertEqual(restarted.cancel(self.alice, op, "1"), first)
        self.assertEqual(len(self.stored("CancellationRecord")), 1)

    def test_stale_control_records_no_effect_and_leaves_queue(self):
        _, op = self.reserve()
        control = self.host.cancel(self.alice, op, "999")
        self.assertEqual(control["outcome"], "stale")
        self.assertEqual(self.host.receipt(self.alice, op)["status"], "queued")
        self.assertEqual(self.host.cancel(self.alice, op, "1")["outcome"], "effective")

    def test_other_actor_and_scope_cannot_cancel(self):
        _, op = self.reserve()
        for principal in (Principal("bob", self.alice.scope), Principal(self.alice.name, "other-scope")):
            with self.subTest(principal=principal), self.assertRaises(Denied):
                self.host.cancel(principal, op, "1")
        self.assertEqual(self.stored("CancellationRecord"), [])

    def test_late_cancel_during_provider_call_cannot_claim_success(self):
        _, op = self.reserve()
        entered, release = threading.Event(), threading.Event()
        original = self.provider.publish
        def held(*args, **kwargs):
            entered.set()
            if not release.wait(5):
                raise RuntimeError("test dispatch was not released")
            return original(*args, **kwargs)
        self.provider.publish = held
        with ThreadPoolExecutor(max_workers=1) as pool:
            dispatch = pool.submit(self.host.dispatch, self.alice, op)
            try:
                self.assertTrue(entered.wait(5))
                control = self.host.cancel(self.alice, op, "1")
                self.assertEqual(control["outcome"], "too-late")
                self.assertEqual(control["observedState"], "attempted")
            finally:
                release.set()
            dispatch.result(timeout=5)
        self.assertEqual(self.host.reconcile(self.alice, op)["status"], "completed")
        self.assertEqual((self.provider.calls, self.host.budget(self.alice)["used"]), (1, 1))

    def test_cancel_dispatch_race_has_one_atomic_winner(self):
        _, op = self.reserve()
        barrier = threading.Barrier(2)
        def cancel():
            barrier.wait(timeout=5)
            return self.host.cancel(self.alice, op, "1")
        def dispatch():
            barrier.wait(timeout=5)
            return self.host.dispatch(self.alice, op)
        with ThreadPoolExecutor(max_workers=2) as pool:
            cancellation, dispatching = pool.submit(cancel), pool.submit(dispatch)
            result, receipt = cancellation.result(timeout=10), dispatching.result(timeout=10)
        if result["outcome"] == "effective":
            self.assertEqual((self.provider.calls, receipt["status"]), (0, "cancelled"))
            self.assertEqual(self.host.budget(self.alice)["used"], 0)
        else:
            self.assertEqual(result["outcome"], "too-late")
            self.assertEqual((self.provider.calls, self.host.budget(self.alice)["used"]), (1, 1))

    def test_cancelled_original_does_not_block_fresh_reviewed_occurrence(self):
        _, op = self.reserve()
        self.host.cancel(self.alice, op, "1")
        _, fresh = self.reserve()
        self.assertNotEqual(op, fresh)
        self.host.dispatch(self.alice, fresh)
        self.assertEqual(self.provider.calls, 1)

    def test_missing_and_zero_budget_fail_closed(self):
        _, op = self.reserve()
        with connection(self.host_path) as db:
            db.execute("DELETE FROM budget_heads")
        with self.assertRaises(Denied):
            self.host.dispatch(self.alice, op)
        self.assertEqual(self.host.receipt(self.alice, op)["status"], "blocked")
        self.host.set_dispatch_budget(self.alice, 0)
        _, other = self.reserve()
        with self.assertRaises(Denied):
            self.host.dispatch(self.alice, other)
        self.assertEqual(self.provider.calls, 0)

    def test_two_workers_cannot_overspend_shared_budget(self):
        self.host.set_dispatch_budget(self.alice, 1)
        _, first = self.reserve()
        _, ref, decision = self.prepare("Different bounded operation")
        second = self.host.reserve(self.alice, ref, decision["id"])
        barrier = threading.Barrier(2)
        def invoke(op):
            worker = Host(self.host_path, self.provider)
            barrier.wait(timeout=5)
            try:
                worker.dispatch(self.alice, op)
                return "invoked"
            except Denied:
                return "blocked"
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(invoke, (first, second)))
        self.assertCountEqual(results, ["invoked", "blocked"])
        self.assertEqual(self.provider.calls, 1)
        self.assertEqual(self.host.budget(self.alice), {"configured": True, "limit": 1, "used": 1, "remaining": 0})

    def test_repeated_dispatch_and_readback_do_not_spend_again(self):
        _, op = self.reserve()
        self.host.dispatch(self.alice, op, fault="lost-response")
        restarted = Host(self.host_path, self.provider)
        restarted.dispatch(self.alice, op)
        restarted.reconcile(self.alice, op)
        restarted.reconcile(self.alice, op)
        self.assertEqual((self.provider.calls, restarted.budget(self.alice)["used"]), (1, 1))

    def test_attempt_claim_crash_remains_charged_without_provider_call(self):
        _, op = self.reserve()
        with self.assertRaises(SimulatedCrash):
            self.host.dispatch(self.alice, op, fault="before-provider")
        reopened = Host(self.host_path, self.provider)
        self.assertEqual(reopened.budget(self.alice)["used"], 1)
        reopened.dispatch(self.alice, op)
        self.assertEqual(self.provider.calls, 0)
        self.assertEqual(reopened.reconcile(self.alice, op)["status"], "pending-verification")

    def test_budget_write_failure_rolls_back_dispatch_ownership(self):
        _, op = self.reserve()
        original = self.host._put
        def fail_budget(db, value):
            if value["kind"] == "DispatchBudget" and value["used"] > 0:
                raise OSError("injected durable-budget failure")
            return original(db, value)
        self.host._put = fail_budget
        with self.assertRaises(OSError):
            self.host.dispatch(self.alice, op)
        self.assertEqual(self.host.receipt(self.alice, op)["status"], "queued")
        self.assertEqual((self.provider.calls, self.host.budget(self.alice)["used"]), (0, 0))

    def test_control_evidence_write_failure_rolls_back_cancellation(self):
        _, op = self.reserve()
        original = self.host._put
        def fail_control(db, value):
            if value["kind"] == "CancellationRecord":
                raise OSError("injected control-evidence failure")
            return original(db, value)
        self.host._put = fail_control
        with self.assertRaises(OSError):
            self.host.cancel(self.alice, op, "1")
        self.assertEqual(self.host.receipt(self.alice, op)["status"], "queued")
        self.assertEqual(self.stored("CancellationRecord"), [])
        self.assertEqual(self.host.budget(self.alice)["used"], 0)

    def test_permission_denial_does_not_spend(self):
        _, op = self.reserve()
        self.host.set_permission(self.alice, "board", False)
        with self.assertRaises(Denied):
            self.host.dispatch(self.alice, op)
        self.assertEqual(self.host.budget(self.alice)["used"], 0)

    def test_cap_changes_and_restart_never_reset_consumption(self):
        _, op = self.reserve()
        self.host.dispatch(self.alice, op)
        self.host.set_dispatch_budget(self.alice, 0)
        self.assertEqual(self.host.budget(self.alice)["remaining"], 0)
        self.host.set_dispatch_budget(self.alice, 2)
        reopened = Host(self.host_path, self.provider)
        self.assertEqual(reopened.budget(self.alice)["remaining"], 1)
        self.assertEqual(reopened.budget(Principal("bob", self.alice.scope))["configured"], False)

    def test_recovery_uses_same_budget_and_readback_remains_available(self):
        self.host.set_dispatch_budget(self.alice, 1)
        _, op = self.reserve()
        self.host.dispatch(self.alice, op, fault="lost-response")
        self.assertEqual(self.host.reconcile(self.alice, op)["status"], "completed")
        self.host.set_permission(self.alice, "board", True, action="withdraw")
        proposal = self.host.propose_recovery(self.alice, op, "withdraw")
        ref = {"id": proposal["id"], "version": proposal["version"]}
        decision = self.host.decide(self.alice, ref, "approve", "recover-decision")
        recovery = self.host.reserve(self.alice, ref, decision["id"])
        with self.assertRaises(Denied):
            self.host.dispatch(self.alice, recovery)
        self.assertEqual(self.provider.resource(self.alice.scope, op)["withdrawn"], 0)

    def test_uninvoked_readback_never_changes_queue_or_terminal_state(self):
        _, op = self.reserve()
        self.provider.lookup = lambda *args: self.fail("uninvoked operation queried provider")
        self.assertEqual(self.host.reconcile(self.alice, op)["status"], "queued")
        self.host.cancel(self.alice, op, "1")
        self.assertEqual(self.host.reconcile(self.alice, op)["effectKnowledge"], "none")

    def test_invalid_caps_and_control_revisions_are_rejected(self):
        for cap in (-1, 1001, True, "3", 1.5):
            with self.subTest(cap=cap), self.assertRaises(ValueError):
                self.host.set_dispatch_budget(self.alice, cap)
        _, op = self.reserve()
        for revision in ("", "x", 1, "1"*11):
            with self.subTest(revision=revision), self.assertRaises(ContractError):
                self.host.cancel(self.alice, op, revision)

    def test_nonempty_v02_stores_require_explicit_migration(self):
        _, op = self.reserve()
        self.host.dispatch(self.alice, op)
        with connection(self.provider.path) as db:
            row = db.execute("SELECT payload FROM effects").fetchone()
            import json
            value = json.loads(row["payload"])
            value["schemaVersion"] = "tse-pilot/0.2"
            db.execute("UPDATE effects SET payload=?", (canonical(value),))
        with self.assertRaises(ContractError):
            Provider(self.provider.path)
