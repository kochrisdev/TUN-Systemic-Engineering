"""Recovery tests exercise a new action, current authority, and provider preconditions."""
import json
import unittest

import test_pilot
from reference.tse_pilot.runtime import Conflict, Denied, Host, Principal, Provider, SimulatedCrash, connection
from reference.tse_pilot.contracts import ContractError, canonical, fingerprint, validate_proposal


class RecoveryCase(unittest.TestCase):
    setUp = test_pilot.PilotCase.setUp
    prepare = test_pilot.PilotCase.prepare
    reserve = test_pilot.PilotCase.reserve
    stored = test_pilot.PilotCase.stored

    def published(self):
        proposal, op = self.reserve()
        self.host.dispatch(self.alice, op)
        self.host.reconcile(self.alice, op)
        return proposal, op

    def approve_recovery(self, original, action="correct", content="Corrected synthetic update"):
        proposal = self.host.propose_recovery(self.alice, original, action, content)
        ref = {"id": proposal["id"], "version": proposal["version"]}
        decision = self.host.decide(self.alice, ref, "approve", "recovery-" + proposal["id"])
        return proposal, ref, decision

    def execute(self, ref, decision, fault=None):
        op = self.host.reserve(self.alice, ref, decision["id"])
        self.host.dispatch(self.alice, op, fault=fault)
        return op, self.host.reconcile(self.alice, op)

    def test_correction_and_withdrawal_preserve_original_history(self):
        _, root = self.published()
        self.host.set_permission(self.alice, "board", True, action="correct")
        p, ref, decision = self.approve_recovery(root)
        correction, receipt = self.execute(ref, decision)
        self.assertEqual(receipt["status"], "completed")
        resource = self.provider.resource(self.alice.scope, root)
        self.assertEqual((resource["content"], resource["revision"]), (p["content"], 2))
        self.host.set_permission(self.alice, "board", True, action="withdraw")
        _, ref, decision = self.approve_recovery(root, "withdraw")
        withdrawal, receipt = self.execute(ref, decision)
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(self.provider.resource(self.alice.scope, root)["withdrawn"], 1)
        self.assertEqual(self.host.receipt(self.alice, root)["status"], "completed")
        self.assertEqual(self.provider.lookup(self.alice.scope, root)["content"], "Synthetic update")
        self.assertEqual(len({root, correction, withdrawal}), 3)

    def test_publish_permission_does_not_grant_recovery(self):
        _, root = self.published()
        _, ref, decision = self.approve_recovery(root)
        with self.assertRaises(Denied):
            self.host.reserve(self.alice, ref, decision["id"])
        self.assertEqual(self.provider.resource(self.alice.scope, root)["revision"], 1)

    def test_original_approval_cannot_approve_recovery(self):
        original, root = self.published()
        self.host.set_permission(self.alice, "board", True, action="withdraw")
        p = self.host.propose_recovery(self.alice, root, "withdraw")
        with self.assertRaises(ContractError):
            self.host.reserve(self.alice, {"id": p["id"], "version": p["version"]}, "decision-" + original["id"])

    def test_queued_recovery_revocation_blocks_provider(self):
        _, root = self.published()
        self.host.set_permission(self.alice, "board", True, action="correct")
        _, ref, decision = self.approve_recovery(root)
        op = self.host.reserve(self.alice, ref, decision["id"])
        self.host.set_permission(self.alice, "board", False, action="correct")
        with self.assertRaises(Denied):
            self.host.dispatch(self.alice, op)
        self.assertEqual(self.provider.resource(self.alice.scope, root)["revision"], 1)

    def test_intervening_resource_change_is_verified_no_effect_failure(self):
        _, root = self.published()
        self.host.set_permission(self.alice, "board", True, action="correct")
        _, stale_ref, stale_decision = self.approve_recovery(root, content="Stale proposed correction")
        _, fresh_ref, fresh_decision = self.approve_recovery(root, content="First committed correction")
        self.execute(fresh_ref, fresh_decision)
        rejected_op, receipt = self.execute(stale_ref, stale_decision)
        self.assertEqual(receipt["status"], "failed")
        self.assertEqual(receipt["effectKnowledge"], "none")
        self.assertEqual(receipt["verificationState"], "verified")
        self.assertEqual(self.provider.lookup(self.alice.scope, rejected_op)["result"], "rejected")
        self.assertEqual(self.provider.resource(self.alice.scope, root)["content"], "First committed correction")

    def test_lost_recovery_response_and_repeated_dispatch_have_one_effect(self):
        _, root = self.published()
        self.host.set_permission(self.alice, "board", True, action="correct")
        _, ref, decision = self.approve_recovery(root)
        op = self.host.reserve(self.alice, ref, decision["id"])
        self.host.dispatch(self.alice, op, fault="lost-response")
        restarted = Host(self.host_path, self.provider)
        restarted.dispatch(self.alice, op)
        self.assertEqual(restarted.reconcile(self.alice, op)["status"], "completed")
        self.assertEqual(self.provider.resource(self.alice.scope, root)["revision"], 2)
        self.assertEqual(self.provider.calls, 2)

    def test_unknown_original_requires_reconciliation(self):
        _, root = self.reserve()
        self.host.dispatch(self.alice, root, fault="lost-response")
        with self.assertRaises(Denied):
            self.host.propose_recovery(self.alice, root, "withdraw")

    def test_pending_recovery_prevents_equivalent_replacement(self):
        _, root = self.published()
        self.host.set_permission(self.alice, "board", True, action="correct")
        _, ref, decision = self.approve_recovery(root)
        op = self.host.reserve(self.alice, ref, decision["id"])
        self.host.dispatch(self.alice, op, fault="lost-response")
        _, second_ref, second_decision = self.approve_recovery(root, content="Different second correction")
        with self.assertRaises(Conflict):
            self.host.reserve(self.alice, second_ref, second_decision["id"])

    def test_another_actor_cannot_recover_original(self):
        _, root = self.published()
        with self.assertRaises(Denied):
            self.host.propose_recovery(Principal("bob", self.alice.scope), root, "withdraw")

    def test_withdrawn_resource_cannot_be_silently_restored(self):
        _, root = self.published()
        self.host.set_permission(self.alice, "board", True, action="withdraw")
        _, ref, decision = self.approve_recovery(root, "withdraw")
        self.execute(ref, decision)
        with self.assertRaises(Conflict):
            self.host.propose_recovery(self.alice, root, "correct", "Restore without authority")

    def test_legacy_nonempty_store_requires_explicit_migration(self):
        with connection(self.host_path) as db:
            fixture = json.loads((test_pilot.ROOT / "schemas/fixtures/valid-proposal.json").read_text())
            db.execute("INSERT INTO records(kind,id,version,payload) VALUES(?,?,?,?)",
                       (fixture["kind"], fixture["id"], fixture["version"], canonical(fixture)))
        with self.assertRaises(ContractError):
            Host(self.host_path, self.provider)

    def test_recovery_fields_require_complete_semantic_binding(self):
        _, root = self.published()
        p = self.host.propose_recovery(self.alice, root, "correct", "Candidate correction")
        for changes in ({"recoveryFor": None}, {"expectedResourceVersion": None}, {"actionType": "publish"}):
            with self.subTest(changes=changes):
                changed = {**p, **changes}
                changed["binding"] = fingerprint(changed)
                with self.assertRaises(ContractError):
                    validate_proposal(changed)

    def test_recovery_grant_cannot_substitute_publication_authority(self):
        _, root = self.published()
        self.host.set_permission(self.alice, "board", True, action="correct")
        _, ref, decision = self.approve_recovery(root)
        op = self.host.reserve(self.alice, ref, decision["id"])
        with connection(self.host_path) as db:
            operation = self.host._load(db, "OperationRecord", op)
            grant = self.host._load(db, "ExecutionGrant", operation["grantId"])
            grant["actionType"] = "publish"
            db.execute("UPDATE records SET payload=? WHERE kind='ExecutionGrant' AND id=?",
                       (canonical(grant), grant["id"]))
        with self.assertRaises(ContractError):
            self.host.dispatch(self.alice, op)
        self.assertEqual(self.provider.resource(self.alice.scope, root)["revision"], 1)

    def test_verified_record_cannot_omit_its_outcome(self):
        _, root = self.published()
        with connection(self.host_path) as db:
            verification = self.host._load(db, "VerificationRecord", root)
            verification["outcome"] = None
            db.execute("UPDATE records SET payload=? WHERE kind='VerificationRecord' AND id=?",
                       (canonical(verification), root))
        with self.assertRaises(ContractError):
            self.host.receipt(self.alice, root)
