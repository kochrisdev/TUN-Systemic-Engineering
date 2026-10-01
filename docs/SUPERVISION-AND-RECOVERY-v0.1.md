# TUN Systemic Engineering — Supervision and Recovery v0.1

Status: proposed control and recovery contracts; no worker-control service is implemented here.

[Documentation index](README.md) · [Specification](SPECIFICATION-v0.1.md) · [Lifecycles](LIFECYCLES-v0.1.md) · [Design integration](DESIGN-INTEGRATION-v0.1.md)

## Describe the intervention before offering it

A control names the intended run, the requested effect, where it takes effect, and what it cannot stop.

| Control | Possible engineering behavior | Essential limit to disclose |
|---|---|---|
| Pause | Stop at the next supported checkpoint | Work before the checkpoint can finish |
| Stop | Prevent additional dispatch and end the worker when possible | Provider-accepted effects may continue |
| Cancel | Withdraw undispatched work or request provider cancellation | Provider acceptance and cancellation can race |
| Revoke | Invalidate further authority | Does not undo earlier effects |
| Take over | Transfer responsibility and disable conflicting automation | Existing provider actions need separate reconciliation |
| Escalate | Assign the unresolved decision to an authorized responder | Assignment is not resolution |

Availability depends on the executor and provider. The first local pilot can support cancellation before dispatch without claiming cancellation of an accepted remote write.

## Control lifecycle

The host prepares a canonical control description tied to a run identity and revision. The requester authenticates and submits the control identity/revision and run identity/revision.

The host validates current access, the control's permitted scope, expiry, and run binding, then records acknowledgement. The worker or provider performs the supported intervention. A later assessment records which promised effect occurred, when, and with what evidence.

A stale control cannot act on a different run or silently broaden its target. Revising the run or remounting the UI cannot remove a still-unresolved control result.

If the request response is lost, inspect the original control record before sending an equivalent command. Duplicate requests need consistent identities and semantics.

## Race example: stop during publication

The host can stop new dispatches while one publication request is already accepted. The control result should say that future dispatches stopped and one effect is still unresolved.

When provider readback later confirms publication, preserve both facts: the intervention took effect within its stated boundary, and the earlier publication completed. Do not overwrite the publication with a generic “cancelled” outcome.

Control completion is evidence of the control's specified effect, not of restoration of the whole workflow.

## Recovery decision path

1. Inspect known and unresolved effects, including later edits to affected resources.
2. If the original effect is unknown, reconcile it through authorized reads.
3. Determine whether a supported retry, restoration, correction, compensation, or escalation is available.
4. Prepare any new effectful recovery as a linked action with material consequences and current preconditions.
5. Apply required approval and host authorization.
6. Execute, verify, and record the recovery's own effects.

A retry adds an attempt to the same logical operation and retains its applicable duplicate identity. A correction, withdrawal, restoration, or compensation is a new logical operation linked to the original. Both require current authority.

Unknown outcomes remain blocked from automatic reissue unless a documented safeguard supports repeating that same operation. The design library's recovery UI permits only reconciliation while the original outcome is unknown; retain that restriction in the presentation adapter.

## Recovery limits

| Situation | Supported response | Misleading claim to avoid |
|---|---|---|
| Publication response lost | Read original provider operation | “Nothing was published” |
| Duplicate protection expired | Escalate or establish another safe path | “Retry is always safe” |
| Shared record has newer edits | Conditional correction/restoration with review | “Restore” that silently overwrites newer work |
| Message delivered externally | Correction or follow-up if authorized | “Undo” that implies recipient copies vanished |
| Partial batch completed | Reconcile each effect, then targeted recovery | Whole batch presented as having no effect |
| Compensation fails partway | Preserve both sets of effects and reassess | Original history erased because recovery began |

A successful local reset changes local state. It does not reverse external effects.

## Authority, budgets, and escalation

Recovery uses the same permissions and consequence classification as any other action. C4 recovery still needs approval of the particular proposal. A revoked writer may retain read authority for reconciliation, if policy permits.

Bound reconciliation polling, retries, control response time, and recovery cost. When those limits are reached, record the unresolved state and route the decision to a named role. Additional budget or authority is an explicit change, not a side effect of persistence.

## Evidence to collect

For each control, retain the requested effect, run/control references, requester, acknowledgement, actual observation, residual effects, and next step. For each recovery, retain the original operation, why the recovery was chosen, its authority, effects, and verification.

Exercise budget and intervention scenarios in [V-23 through V-27](VALIDATION-PLAN-v0.1.md#v-23), including stale control requests and recovery failure. The host's own “stop requested” log is insufficient evidence that the worker stopped.
