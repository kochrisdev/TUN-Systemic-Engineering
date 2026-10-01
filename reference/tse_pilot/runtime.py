"""Local-only publication experiment. Trusted fixture callers, not authentication."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from .contracts import (
    ContractError, SCHEMA_VERSION, canonical, decode, fingerprint, moment,
    validate, validate_binding, validate_proposal,
)


class Denied(ValueError):
    pass


class Conflict(ValueError):
    pass


class SimulatedCrash(BaseException):
    """Fault injection deliberately bypasses ordinary transport-error handling."""


@dataclass(frozen=True)
class Principal:
    name: str
    scope: str


def utcnow():
    return datetime.now(timezone.utc)


def stamp(value):
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def record(kind, scope, now, identifier=None, version="1", **fields):
    return dict(kind=kind, schemaVersion=SCHEMA_VERSION, id=identifier or str(uuid4()),
                version=version, scope=scope, createdAt=stamp(now), **fields)


@contextmanager
def connection(path):
    db = sqlite3.connect(str(path), isolation_level=None, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA synchronous=FULL")
    try:
        db.execute("BEGIN IMMEDIATE")
        yield db
        db.commit()
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()


class Provider:
    """Separate SQLite store; atomic effect + lifetime idempotency key."""
    def __init__(self, path):
        self.path = Path(path)
        self.lookup_available = True
        with connection(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS effects (
                scope TEXT NOT NULL, operation_id TEXT NOT NULL, payload TEXT NOT NULL,
                PRIMARY KEY (scope, operation_id))""")
            for row in db.execute("SELECT payload FROM effects"):
                if decode(row["payload"])["schemaVersion"] != SCHEMA_VERSION:
                    raise ContractError("legacy provider store requires explicit migration; use new fixture stores")
            db.execute("""CREATE TABLE IF NOT EXISTS resources (
                scope TEXT NOT NULL, root_id TEXT NOT NULL, target TEXT NOT NULL,
                content TEXT NOT NULL, revision INTEGER NOT NULL, withdrawn INTEGER NOT NULL,
                PRIMARY KEY(scope,root_id))""")

    def publish(self, request, *, lose_response=False):
        validate(request, "ProviderEffect")
        if request["schemaVersion"] != SCHEMA_VERSION:
            raise ContractError("provider requires current schema")
        with connection(self.path) as db:
            row = db.execute("SELECT payload FROM effects WHERE scope=? AND operation_id=?",
                             (request["scope"], request["operationId"])).fetchone()
            if row:
                effect = decode(row["payload"])
                validate(effect, "ProviderEffect")
                # IDs and timestamps are generated only on the first application.
                fields = ("scope", "operationId", "target", "content", "binding", "actionType",
                          "recoveryFor", "expectedResourceVersion")
                if any(effect[key] != request[key] for key in fields):
                    raise Conflict("idempotency key has different material parameters")
            else:
                action = request["actionType"]
                effect = {**request, "result": "applied", "resultResourceVersion": 1}
                if action == "publish":
                    if request["recoveryFor"] is not None or request["expectedResourceVersion"] is not None:
                        raise ContractError("publication cannot contain recovery preconditions")
                    db.execute("INSERT INTO resources VALUES(?,?,?,?,1,0)",
                               (request["scope"], request["operationId"], request["target"], request["content"]))
                else:
                    current = db.execute("SELECT * FROM resources WHERE scope=? AND root_id=?",
                                         (request["scope"], request["recoveryFor"])).fetchone()
                    eligible = (current is not None and current["target"] == request["target"]
                                and current["revision"] == request["expectedResourceVersion"]
                                and not current["withdrawn"]
                                and (action != "withdraw" or current["content"] == request["content"]))
                    if eligible:
                        next_revision = current["revision"] + 1
                        db.execute("UPDATE resources SET content=?,revision=?,withdrawn=? WHERE scope=? AND root_id=?",
                                   (request["content"], next_revision, int(action == "withdraw"),
                                    request["scope"], request["recoveryFor"]))
                        effect["resultResourceVersion"] = next_revision
                    else:
                        # Persist a correlated, no-effect rejection, not a transport-failure guess.
                        effect.update(result="rejected", resultResourceVersion=None)
                db.execute("INSERT INTO effects VALUES (?,?,?)",
                           (effect["scope"], effect["operationId"], canonical(effect)))
        if lose_response:
            raise TimeoutError("response lost after provider commit")
        return effect

    def resource(self, scope, root_id):
        if not self.lookup_available:
            raise TimeoutError("fixture readback unavailable")
        with connection(self.path) as db:
            row = db.execute("SELECT * FROM resources WHERE scope=? AND root_id=?", (scope, root_id)).fetchone()
            return dict(row) if row else None

    def lookup(self, scope, operation_id):
        if not self.lookup_available:
            raise TimeoutError("fixture readback unavailable")
        with connection(self.path) as db:
            row = db.execute("SELECT payload FROM effects WHERE scope=? AND operation_id=?",
                             (scope, operation_id)).fetchone()
            return decode(row["payload"]) if row else None

    def count(self):
        # Fixture diagnostics, not a user-facing query.
        with connection(self.path) as db:
            return db.execute("SELECT COUNT(*) FROM effects").fetchone()[0]


class Host:
    def __init__(self, path, provider, clock=utcnow):
        self.path, self.provider, self.clock = Path(path), provider, clock
        if self.path.resolve() == provider.path.resolve():
            raise ValueError("host and provider must use separate stores")
        with connection(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS records (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL, id TEXT NOT NULL, version TEXT NOT NULL,
                payload TEXT NOT NULL, UNIQUE(kind,id,version))""")
            for row in db.execute("SELECT payload FROM records"):
                if decode(row["payload"])["schemaVersion"] != SCHEMA_VERSION:
                    raise ContractError("legacy host store requires explicit migration; use new fixture stores")
            db.execute("""CREATE TABLE IF NOT EXISTS heads (
                scope TEXT NOT NULL, id TEXT NOT NULL, version TEXT NOT NULL,
                PRIMARY KEY(scope,id))""")
            db.execute("""CREATE TABLE IF NOT EXISTS policy (
                scope TEXT NOT NULL, principal TEXT NOT NULL, target TEXT NOT NULL,
                allowed INTEGER NOT NULL, revision INTEGER NOT NULL,
                PRIMARY KEY(scope,principal,target))""")
            db.execute("""CREATE TABLE IF NOT EXISTS action_policy (
                scope TEXT NOT NULL, principal TEXT NOT NULL, target TEXT NOT NULL, action TEXT NOT NULL,
                allowed INTEGER NOT NULL, revision INTEGER NOT NULL,
                PRIMARY KEY(scope,principal,target,action))""")
            db.execute("""CREATE TABLE IF NOT EXISTS operation_keys (
                scope TEXT NOT NULL, proposal_id TEXT NOT NULL, proposal_version TEXT NOT NULL,
                operation_id TEXT UNIQUE NOT NULL,
                PRIMARY KEY(scope,proposal_id,proposal_version))""")

    def set_permission(self, principal, target, allowed, *, action="publish"):
        """Trusted fixture administration; deliberately not an exposed endpoint."""
        with connection(self.path) as db:
            if action in ("correct", "withdraw"):
                db.execute("""INSERT INTO action_policy VALUES (?,?,?,?,?,1)
                    ON CONFLICT(scope,principal,target,action) DO UPDATE
                    SET allowed=excluded.allowed, revision=action_policy.revision+1""",
                           (principal.scope, principal.name, target, action, int(allowed)))
                return
            if action != "publish":
                raise ValueError("unsupported permission action")
            db.execute("""INSERT INTO policy VALUES (?,?,?,?,1)
                ON CONFLICT(scope,principal,target) DO UPDATE
                SET allowed=excluded.allowed, revision=policy.revision+1""",
                       (principal.scope, principal.name, target, int(allowed)))

    @staticmethod
    def _load(db, kind, identifier, version=None):
        sql = "SELECT kind,id,version,payload FROM records WHERE kind=? AND id=?"
        args = [kind, identifier]
        if version is not None:
            sql += " AND version=?"
            args.append(version)
        row = db.execute(sql + " ORDER BY sequence DESC LIMIT 1", args).fetchone()
        if row is None:
            raise Denied("record unavailable")
        result = decode(row["payload"])
        validate(result, kind)
        if any(result[key] != row[key] for key in ("kind", "id", "version")):
            raise ContractError("stored record identity mismatch")
        return result

    @staticmethod
    def _put(db, value):
        validate(value)
        db.execute("INSERT INTO records(kind,id,version,payload) VALUES(?,?,?,?)",
                   (value["kind"], value["id"], value["version"], canonical(value)))
        return value

    def _advance(self, db, value, **fields):
        return self._put(db, {**value, **fields, "version": str(int(value["version"]) + 1),
                              "createdAt": stamp(self.clock())})

    def _proposal(self, db, principal, ref, *, active=False):
        if (not isinstance(ref, dict) or set(ref) != {"id", "version"}
                or any(type(ref[k]) is not str or not ref[k] or len(ref[k]) > 128 for k in ref)):
            raise ContractError("invalid proposal reference")
        proposal = self._load(db, "ActionProposal", ref["id"], ref["version"])
        if proposal["scope"] != principal.scope or proposal["actor"] != principal.name:
            raise Denied("record unavailable")
        validate_proposal(proposal)
        if active:
            head = db.execute("SELECT version FROM heads WHERE scope=? AND id=?",
                              (principal.scope, proposal["id"])).fetchone()
            if not head or head["version"] != proposal["version"]:
                raise Denied("proposal superseded")
            if moment(proposal["expiresAt"]) <= self.clock():
                raise Denied("proposal expired")
        return proposal

    def propose(self, principal, target, content, *, previous=None, lifetime=300):
        with connection(self.path) as db:
            old = self._proposal(db, principal, previous, active=True) if previous else None
            if old and old["actionType"] != "publish":
                raise Conflict("prepare a new recovery proposal instead")
            if old and db.execute("SELECT 1 FROM operation_keys WHERE scope=? AND proposal_id=?",
                                  (principal.scope, old["id"])).fetchone():
                raise Conflict("cannot revise an already reserved proposal in this pilot")
            now = self.clock()
            proposal = record("ActionProposal", principal.scope, now,
                              identifier=old["id"] if old else None,
                              version=str(int(old["version"]) + 1) if old else "1",
                              actor=principal.name, target=target, content=content, consequence="C3",
                              expectedEffect="one sandbox publication", precondition="new publication",
                              recoveryLimit="separate approved correction or withdrawal; history and external copies are not erased",
                              actionType="publish", recoveryFor=None, expectedResourceVersion=None,
                              expiresAt=stamp(now + timedelta(seconds=lifetime)), binding="")
            proposal["binding"] = fingerprint(proposal)
            validate_proposal(proposal)
            self._put(db, proposal)
            db.execute("INSERT INTO heads VALUES(?,?,?) ON CONFLICT(scope,id) DO UPDATE SET version=excluded.version",
                       (principal.scope, proposal["id"], proposal["version"]))
            return proposal

    def propose_recovery(self, principal, original_id, action, content=None, *, lifetime=300):
        if action not in ("correct", "withdraw"):
            raise ValueError("unsupported recovery action")
        with connection(self.path) as db:
            original, source = self._operation(db, principal, original_id)
            if source["actionType"] != "publish" or self._receipt(db, original, source)["status"] != "completed":
                raise Denied("reconcile the original publication before recovery")
        current = self.provider.resource(principal.scope, original_id)
        if not current or current["withdrawn"] or current["target"] != source["target"]:
            raise Conflict("publication is unavailable for recovery")
        now = self.clock()
        proposal = record("ActionProposal", principal.scope, now, actor=principal.name,
                          target=source["target"], content=current["content"] if action == "withdraw" else content,
                          consequence="C3", expectedEffect=f"{action} one existing sandbox publication",
                          precondition=f"active publication at resource revision {current['revision']}",
                          recoveryLimit="history and external copies remain; no undo or restoration is promised",
                          actionType=action, recoveryFor=original_id, expectedResourceVersion=current["revision"],
                          expiresAt=stamp(now + timedelta(seconds=lifetime)), binding="")
        proposal["binding"] = fingerprint(proposal)
        validate_proposal(proposal)
        with connection(self.path) as db:
            self._put(db, proposal)
            db.execute("INSERT INTO heads VALUES(?,?,?)", (principal.scope, proposal["id"], proposal["version"]))
        return proposal

    def decide(self, principal, ref, choice, submission_id):
        with connection(self.path) as db:
            proposal = self._proposal(db, principal, ref)
            existing = db.execute("SELECT 1 FROM records WHERE kind='ApprovalDecision' AND id=?",
                                  (submission_id,)).fetchone()
            if existing:
                decision = self._load(db, "ApprovalDecision", submission_id)
                validate_binding(decision, proposal)
                if decision["principal"] != principal.name or decision["decision"] != choice:
                    raise Conflict("decision submission identity reused")
                return decision
            self._proposal(db, principal, ref, active=True)
            # This pilot allows one terminal human decision per revision.
            for row in db.execute("SELECT payload FROM records WHERE kind='ApprovalDecision'"):
                prior = decode(row["payload"])
                if prior["scope"] == principal.scope and prior["proposalRef"] == ref:
                    raise Conflict("proposal already has a decision")
            return self._put(db, record("ApprovalDecision", principal.scope, self.clock(),
                             identifier=submission_id, proposalRef=ref, binding=proposal["binding"],
                             principal=principal.name, decision=choice))

    def _authorization(self, db, principal, proposal, decision_id, operation_id):
        policy = db.execute("SELECT allowed,revision FROM policy WHERE scope=? AND principal=? AND target=?",
                            (principal.scope, principal.name, proposal["target"])).fetchone()
        if proposal["actionType"] != "publish":
            policy = db.execute("SELECT allowed,revision FROM action_policy WHERE scope=? AND principal=? AND target=? AND action=?",
                                (principal.scope, principal.name, proposal["target"], proposal["actionType"])).fetchone()
        allowed = bool(policy and policy["allowed"])
        return self._put(db, record("AuthorizationDecision", principal.scope, self.clock(),
                         proposalRef={"id": proposal["id"], "version": proposal["version"]},
                         binding=proposal["binding"], operationId=operation_id, principal=principal.name,
                         decisionId=decision_id, policyVersion=str(policy["revision"] if policy else 0),
                         actionType=proposal["actionType"], result="allow" if allowed else "deny",
                         reason="permitted" if allowed else "permission-denied"))

    def reserve(self, principal, ref, decision_id):
        denied = False
        with connection(self.path) as db:
            proposal = self._proposal(db, principal, ref, active=True)
            decision = self._load(db, "ApprovalDecision", decision_id)
            validate_binding(decision, proposal)
            if decision["principal"] != principal.name or decision["decision"] != "approve":
                raise Denied("particular approval required")
            row = db.execute("SELECT operation_id FROM operation_keys WHERE scope=? AND proposal_id=? AND proposal_version=?",
                             (principal.scope, ref["id"], ref["version"])).fetchone()
            if row:
                return row["operation_id"]
            # Exact-content replacement protection, not semantic similarity detection.
            for row in db.execute("SELECT operation_id FROM operation_keys WHERE scope=?", (principal.scope,)):
                other = self._load(db, "OperationRecord", row["operation_id"])
                old = self._load(db, "ActionProposal", other["proposalRef"]["id"], other["proposalRef"]["version"])
                validate_binding(other, old)
                equivalent = (old["actionType"] == proposal["actionType"] == "publish"
                              and old["target"] == proposal["target"] and old["content"] == proposal["content"])
                same_recovery_target = (old["recoveryFor"] is not None and old["recoveryFor"] == proposal["recoveryFor"])
                if other["state"] not in ("verified", "blocked", "failed") and (equivalent or same_recovery_target):
                    raise Conflict("equivalent original operation remains unresolved")
            op_id = str(uuid4())
            auth = self._authorization(db, principal, proposal, decision_id, op_id)
            denied = auth["result"] == "deny"
            if not denied:
                grant = record("ExecutionGrant", principal.scope, self.clock(), proposalRef=ref,
                               binding=proposal["binding"], operationId=op_id, principal=principal.name,
                               target=proposal["target"], actionType=proposal["actionType"],
                               authorizationId=auth["id"], expiresAt=proposal["expiresAt"])
                self._put(db, grant)
                attempt = record("ExecutionAttempt", principal.scope, self.clock(), operationId=op_id,
                                 grantId=grant["id"], state="reserved", observation="pending")
                self._put(db, attempt)
                op = record("OperationRecord", principal.scope, self.clock(), identifier=op_id,
                            proposalRef=ref, binding=proposal["binding"], principal=principal.name,
                            target=proposal["target"], grantId=grant["id"], attemptId=attempt["id"], state="reserved")
                self._put(db, op)
                db.execute("INSERT INTO operation_keys VALUES(?,?,?,?)",
                           (principal.scope, ref["id"], ref["version"], op_id))
                self._project(db, op, proposal)
        if denied:
            raise Denied("dispatch permission denied")
        return op_id

    def _operation(self, db, principal, op_id):
        op = self._load(db, "OperationRecord", op_id)
        if op["scope"] != principal.scope or op["principal"] != principal.name:
            raise Denied("record unavailable")
        proposal = self._proposal(db, principal, op["proposalRef"])
        validate_binding(op, proposal)
        if op["target"] != proposal["target"]:
            raise ContractError("operation target mismatch")
        return op, proposal

    def dispatch(self, principal, op_id, *, fault=None):
        if fault not in (None, "before-provider", "after-provider", "lost-response"):
            raise ValueError("unknown fixture fault")
        denied = False
        with connection(self.path) as db:
            op, proposal = self._operation(db, principal, op_id)
            if op["state"] != "reserved":
                return self._receipt(db, op, proposal)
            grant = self._load(db, "ExecutionGrant", op["grantId"])
            validate_binding(grant, proposal)
            auth = self._load(db, "AuthorizationDecision", grant["authorizationId"])
            validate_binding(auth, proposal)
            if (grant["operationId"] != op_id or grant["principal"] != principal.name
                    or grant["target"] != proposal["target"] or auth["operationId"] != op_id
                    or grant["actionType"] != proposal["actionType"] or auth["actionType"] != proposal["actionType"]
                    or auth["principal"] != principal.name or auth["result"] != "allow"):
                raise ContractError("grant authority mismatch")
            decision = self._load(db, "ApprovalDecision", auth["decisionId"])
            validate_binding(decision, proposal)
            if decision["principal"] != principal.name or decision["decision"] != "approve":
                raise Denied("particular approval required")
            attempt = self._load(db, "ExecutionAttempt", op["attemptId"])
            if (attempt["operationId"] != op_id or attempt["grantId"] != grant["id"]
                    or attempt["scope"] != principal.scope):
                raise ContractError("attempt binding mismatch")
            try:
                self._proposal(db, principal, op["proposalRef"], active=True)
                if moment(grant["expiresAt"]) <= self.clock():
                    raise Denied("grant expired")
            except Denied:
                denied = True
            current = self._authorization(db, principal, proposal, decision["id"], op_id)
            denied = denied or current["result"] == "deny"
            op = self._advance(db, op, state="blocked" if denied else "attempted")
            self._advance(db, attempt, state="ended" if denied else "dispatching",
                          observation="dispatch-denied" if denied else "pending")
            self._project(db, op, proposal)
        if denied:
            raise Denied("dispatch checks failed")
        if fault == "before-provider":
            raise SimulatedCrash("crash after reservation, before provider")
        request = record("ProviderEffect", principal.scope, self.clock(), operationId=op_id,
                         target=proposal["target"], content=proposal["content"], binding=proposal["binding"],
                         actionType=proposal["actionType"], recoveryFor=proposal["recoveryFor"],
                         expectedResourceVersion=proposal["expectedResourceVersion"],
                         result="applied", resultResourceVersion=None)
        observation = "acknowledged"
        try:
            self.provider.publish(request, lose_response=fault == "lost-response")
            if fault == "after-provider":
                raise SimulatedCrash("crash after provider commit, before host result")
        except Exception:
            # Even an unexpected adapter error cannot prove no effect.
            observation = "response-lost"
        with connection(self.path) as db:
            op, proposal = self._operation(db, principal, op_id)
            attempt = self._load(db, "ExecutionAttempt", op["attemptId"])
            self._advance(db, attempt, state="ended", observation=observation)
            # A concurrently completed readback must not be erased by a late acknowledgement.
            if op["state"] == "attempted":
                op = self._advance(db, op, state="unknown")
            self._project(db, op, proposal)
        return self.receipt(principal, op_id)

    def reconcile(self, principal, op_id):
        with connection(self.path) as db:
            op, proposal = self._operation(db, principal, op_id)
        result, effect_id, outcome = "pending", None, None
        try:
            effect = self.provider.lookup(principal.scope, op_id)
            if effect is not None:
                validate(effect, "ProviderEffect")
                matches = (effect["scope"] == principal.scope and effect["operationId"] == op_id
                           and effect["target"] == proposal["target"] and effect["content"] == proposal["content"]
                           and effect["binding"] == proposal["binding"]
                           and effect["actionType"] == proposal["actionType"] and effect["recoveryFor"] == proposal["recoveryFor"]
                           and effect["expectedResourceVersion"] == proposal["expectedResourceVersion"])
                expected_revision = (proposal["expectedResourceVersion"] or 0) + 1
                matches = matches and ((effect["result"] == "applied" and effect["resultResourceVersion"] == expected_revision)
                                       or (effect["result"] == "rejected" and effect["resultResourceVersion"] is None))
                result = "verified" if matches else "contradicted"
                effect_id = effect["id"] if matches else None
                outcome = effect["result"] if matches else None
        except ContractError:
            result = "contradicted"
        except Exception:
            result = "unavailable"
        with connection(self.path) as db:
            op, proposal = self._operation(db, principal, op_id)
            count = db.execute("SELECT COUNT(*) FROM records WHERE kind='VerificationRecord' AND id=?", (op_id,)).fetchone()[0]
            verification = record("VerificationRecord", principal.scope, self.clock(), identifier=op_id,
                                  version=str(count + 1), proposalRef=op["proposalRef"], binding=op["binding"],
                                  operationId=op_id, target=proposal["target"], result=result, effectId=effect_id,
                                  observedAt=stamp(self.clock()), outcome=outcome,
                                  claim="bound local provider outcome recorded in operation history")
            self._put(db, verification)
            next_state = "failed" if result == "verified" and outcome == "rejected" else result
            op = self._advance(db, op, state=next_state if next_state in ("verified", "contradicted", "failed") else "unknown")
            self._project(db, op, proposal)
        return self.receipt(principal, op_id)

    def _projection_fields(self, db, op, proposal):
        rows = db.execute("SELECT version FROM records WHERE kind='VerificationRecord' AND id=? ORDER BY sequence", (op["id"],)).fetchall()
        assessments = [self._load(db, "VerificationRecord", op["id"], row["version"]) for row in rows]
        for assessment in assessments:
            validate_binding(assessment, proposal)
            if (assessment["operationId"] != op["id"] or assessment["target"] != proposal["target"]
                    or (assessment["result"] == "verified" and
                        (not assessment["effectId"] or assessment["outcome"] not in ("applied", "rejected")))
                    or (assessment["result"] != "verified" and
                        (assessment["effectId"] is not None or assessment["outcome"] is not None))):
                raise ContractError("verification operation binding mismatch")
        latest = assessments[-1] if assessments else None
        state = latest["result"] if latest else "pending"
        known = any(item["result"] == "verified" and item["outcome"] == "applied" for item in assessments)
        status = "completed" if state == "verified" else ("contradicted" if state == "contradicted" else "pending-verification")
        if latest and state == "verified" and latest["outcome"] == "rejected":
            status = "failed"
        if op["state"] == "blocked" and not assessments:
            status = "blocked"
        return dict(proposalRef=op["proposalRef"], binding=op["binding"],
                         operationId=op["id"], target=op["target"],
                         effectKnowledge="observed" if known else ("none" if status in ("blocked", "failed") else "unknown"),
                         verificationState=state, status=status,
                         verificationRef={"id": latest["id"], "version": latest["version"]} if latest else None,
                         limitations="Local-store observation only. No delivery or content-truth claim. Prior observations do not establish current state.")

    def _project(self, db, op, proposal):
        count = db.execute("SELECT COUNT(*) FROM records WHERE kind='ActionRecord' AND id=?", (op["id"],)).fetchone()[0]
        return self._put(db, record("ActionRecord", op["scope"], self.clock(), identifier=op["id"],
                         version=str(count + 1), **self._projection_fields(db, op, proposal)))

    def _receipt(self, db, op, proposal):
        result = self._load(db, "ActionRecord", op["id"])
        validate_binding(result, proposal)
        expected = self._projection_fields(db, op, proposal)
        if any(result[key] != value for key, value in expected.items()):
            raise ContractError("receipt does not match authoritative records")
        return result

    def receipt(self, principal, op_id):
        with connection(self.path) as db:
            op, proposal = self._operation(db, principal, op_id)
            return self._receipt(db, op, proposal)
