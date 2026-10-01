"""Access-filtered projections for the two pinned TUN design components."""
from .runtime import Denied, connection, moment


def proposal_view(p):
    action = {"publish": "Publish update", "correct": "Correct publication", "withdraw": "Withdraw publication"}[p["actionType"]]
    return {
        "id": p["id"], "version": p["version"], "action": action,
        "target": p["target"] + (f" / publication {p['recoveryFor']}" if p["recoveryFor"] else ""),
        "actor": {"id": p["actor"], "name": p["actor"], "type": "human"},
        "consequence": p["consequence"],
        "effect": p["expectedEffect"] + ". " + p["precondition"],
        "authority": f"Current {p['actionType']} permission is checked separately at dispatch.",
        "recovery": {"kind": "compensatable", "description": p["recoveryLimit"]},
        "expiresAt": p["expiresAt"], "contentPreview": p["content"],
    }


def receipt_view(receipt, proposal):
    status = receipt["status"]
    descriptions = {
        "completed": "The bound operation was verified in provider history; this is not a claim about current resource state.",
        "failed": "The provider recorded a precondition rejection. This operation made no resource change.",
        "blocked": "Host checks blocked dispatch. This operation made no provider call.",
        "contradicted": "Evidence contradicts the proposed effect. Completion is not confirmed.",
        "pending-verification": "Outcome unknown or unverified. Reconcile the original operation; do not create a replacement.",
    }
    verification = receipt["verificationState"]
    if verification == "contradicted":
        verification = "pending"  # Design enum lacks contradicted; preserve it explicitly in the text.
    return {
        "id": f"{receipt['id']}:{receipt['version']}",
        "action": proposal_view(proposal)["action"],
        "actor": proposal_view(proposal)["actor"], "target": proposal_view(proposal)["target"],
        "timestamp": receipt["createdAt"],
        "status": {"blocked": "failed", "contradicted": "pending-verification"}.get(status, status),
        "summary": descriptions[status],
        "verification": {"state": verification, "detail": descriptions[status] + " " + receipt["limitations"]},
        "recovery": {"kind": "compensatable", "description": proposal["recoveryLimit"]},
    }


def snapshot(host, principal):
    proposals, operations, roots = [], [], []
    with connection(host.path) as db:
        rows = db.execute("SELECT id,version FROM heads WHERE scope=? ORDER BY rowid", (principal.scope,)).fetchall()
        for row in rows:
            try:
                p = host._proposal(db, principal, dict(row))
            except Denied:
                continue
            decisions = [host._load(db, "ApprovalDecision", row["id"]) for row in db.execute(
                "SELECT id FROM records WHERE kind='ApprovalDecision'")]
            matching = [d for d in decisions if d["scope"] == principal.scope and d["principal"] == principal.name
                        and d["proposalRef"] == {"id": p["id"], "version": p["version"]}]
            status = "awaiting"
            if matching:
                status = "approved" if matching[-1]["decision"] == "approve" else "rejected"
            if status == "awaiting" and moment(p["expiresAt"]) <= host.clock():
                status = "expired"
            row = db.execute("SELECT operation_id FROM operation_keys WHERE scope=? AND proposal_id=? AND proposal_version=?",
                             (principal.scope, p["id"], p["version"])).fetchone()
            proposals.append({"proposal": proposal_view(p), "status": status,
                              "operationId": row["operation_id"] if row else None})
        for row in db.execute("SELECT operation_id FROM operation_keys WHERE scope=? ORDER BY rowid", (principal.scope,)):
            try:
                op, p = host._operation(db, principal, row["operation_id"])
            except Denied:
                continue
            receipt = host._receipt(db, op, p)
            operations.append({"id": op["id"], "actionType": p["actionType"], "originalId": p["recoveryFor"],
                               "hostStatus": receipt["status"], "receipt": receipt_view(receipt, p)})
            if p["actionType"] == "publish":
                roots.append(op["id"])
    resources = []
    for root in roots:
        current = host.provider.resource(principal.scope, root)
        if current:
            resources.append({"rootId": root, "target": current["target"], "revision": current["revision"],
                              "status": "withdrawn" if current["withdrawn"] else "active",
                              "content": "" if current["withdrawn"] else current["content"]})
    return {"viewVersion": "tse-design-view/0.1", "proposals": proposals,
            "operations": operations, "resources": resources}
