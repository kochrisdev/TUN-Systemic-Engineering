# Local Supervision Pilot

Status: experimental v0.3, synthetic local data only. This is a bounded host-control slice, not a general worker-control service.

[Documentation index](README.md) · [Run the review interface](REVIEW-AND-RECOVERY-PILOT.md) · [Supervision model](SUPERVISION-AND-RECOVERY-v0.1.md) · [Schemas](../schemas/README.md)

## The engineering question

Can a person stop queued work without claiming that an accepted action was undone? Can two workers respect one shared limit even when they race or restart?

The local pilot answers those two narrow questions. It separates reservation from dispatch, persists cancellation outcomes, and consumes a dispatch allowance atomically with host ownership of the attempt.

## What is implemented

| Capability | Enforced boundary |
|---|---|
| Queue an approved proposal | Canonical proposal, approval, permission, and durable operation; no provider write |
| Cancel queued work | Exact operation ID/revision and owning fixture principal/scope; only reserved state can change |
| Reject stale or late cancellation | Persist stale or too-late evidence; leave operation and effects unchanged |
| Bound dispatch attempts | A configured total cap per principal/scope, shared across targets and publish/correct/withdraw actions |
| Preserve spent allowance | Durable budget revisions; no automatic refill or refund |
| Read history at zero budget | Receipts and reconciliation remain available under existing record access rules |

Fixture identity is trusted input, not authentication. The local server seeds three dispatch slots when creating a new store. It does not reseed a compatible existing store.

## Try cancellation

Follow the [build and server instructions](REVIEW-AND-RECOVERY-PILOT.md#start-the-interface), using a new v0.3 fixture directory.

1. Prepare and approve a synthetic publication.
2. Select Queue approved action. The operation card says Queued — not dispatched; budget consumption remains zero.
3. Select Cancel queued action. The host status becomes Cancelled before dispatch, and a separate cancellation-evidence card records effective.
4. Refresh or reopen the compatible store. The cancellation remains effective. A duplicate request returns the same control record; a later dispatch request cannot invoke the provider for that operation.
5. A new occurrence requires a fresh proposal and approval. Cancellation does not erase the old decision, operation, or evidence.

Cancellation is allowed even after write permission is revoked or the proposal expires, provided the caller still has this pilot's owner/scope access. It reduces queued authority and cannot create a provider effect. Production systems need an explicit authenticated control-access policy.

## Try the dispatch cap

The normal publication → correction → withdrawal walkthrough uses all three slots in a fresh store. Each action still requires its own approval, queue, dispatch, and readback.

At zero remaining slots, the interface disables dispatch but permits cancellation and readback. The host independently enforces the cap; changing client fields or calling the endpoint directly cannot bypass it.

The total cap is not a daily rate limit, monetary limit, model-token allowance, timeout, or maximum number of successful effects. It counts committed host dispatch claims. Preparing, approving, reserving, cancelling, and reading do not consume this particular allowance and are not themselves rate-limited here.

A provider rejection still consumes a slot. A response timeout still consumes a slot. A crash after the dispatch claim but before the provider call also consumes a slot: the host does not reclaim an allowance based on uncertainty.

## The shared transaction boundary

The host uses the same SQLite write transaction for cancellation, dispatch ownership, and budget consumption.

| Winner or failure | Durable facts | Effectful provider invocation |
|---|---|---|
| Cancellation wins while reserved | Cancelled operation, ended attempt, effective control evidence, unchanged budget | None for that operation |
| Dispatch wins with authority and budget | Attempted operation, dispatching attempt, one new budget revision and its reference | At most one host invocation |
| Cancellation arrives after dispatch claim | Too-late control evidence; action state remains intact | Earlier call may be in flight or completed |
| Wrong queued revision | Stale control evidence; queue unchanged | None caused by cancellation |
| Permission/expiry check fails | Blocked operation, dispatch-denied observation, no budget charge | None |
| Missing/exhausted budget | Blocked operation, budget-exhausted observation, no charge | None |
| Host transaction fails | No committed dispatch claim or charge | None |
| Crash after committed dispatch claim | Spent slot retained; action may remain unresolved | May or may not have happened; reconcile |

Two workers cannot both spend the last slot because checking and incrementing the budget occur inside this transaction. This is evidence about the single local database model, not distributed exactly-once execution or hardware durability.

A cancelled or blocked operation is terminal in this pilot. Increasing a cap does not resume blocked work or silently reuse an old decision for a new operation. Prepare and approve a new proposal if further work is needed.

## Records and command shapes

Storage records use tse-pilot/0.3. DispatchBudget records preserve total cap, cumulative usage, and the operation that consumed the latest slot; administrative cap changes have no last charged operation. ExecutionAttempt.budgetRef identifies the exact charged budget revision, or null when no charge occurred.

CancellationRecord contains the owning principal, proposal binding, requested operation ID/revision, observed operation revision/state, and effective/too-late/stale result. Request identity is deterministically derived by the host from that operation/revision, so repeat submission returns the same historical response. Refresh history for current state.

The loopback commands are:

- POST /api/reserve: proposalId and proposalVersion.
- POST /api/dispatch: operationId and loseResponse, a fixture-only fault flag.
- POST /api/cancel: operationId and operationVersion.
- POST /api/reconcile: operationId.

These routes retain exact Host/Origin, request-token, bounded-body, and unexpected-field checks. The former /api/execute shortcut is removed. No HTTP budget-management endpoint is provided.

The fixture-only set_dispatch_budget helper accepts a total cap from 0 to 1,000. Changing that cap appends a revision without resetting used. Lowering the cap below usage leaves remaining at zero. This helper is not an authenticated administration service and must not be exposed as one.

## Honest presentation

Presentation version tse-design-view/0.2 adds budget, controls, and operation revision/state. For queued, blocked, and cancelled operations, receipt is null: the UI renders a host status card instead of forcing these facts into the pinned design library's receipt enum.

Provider-dispatched work continues to use ActionReceipt. Cancellation evidence is separate from action history; a late control cannot turn a completed publication into cancelled or reversed.

Only ApprovalGate and ActionReceipt are integrated from the pinned design library. HumanOverride and RecoveryControl remain documented mappings, not implemented integrations.

## Verification and open work

The [2 October validation record](SUPERVISION-VALIDATION-2026-10-02.md) binds the executed automated checks and browser journey to a specific source revision. It distinguishes observed behavior from open work and records known usability limits.

[Supervision tests](../tests/test_supervision.py) cover cancellation/dispatch races, late controls during an in-flight provider call, duplicate cancellation across restart, stale revisions, owner/scope restrictions, shared-cap concurrency, rollback, conservative crash accounting, and old-store refusal. [HTTP tests](../tests/test_review_server.py) check queue/control commands and reject client budget overrides. [Component tests](../ui/src/components.test.tsx) check explicit controls, disabled dispatch at zero budget, and truthful cancelled labels.

Full [conformance procedures](VALIDATION-PLAN-v0.1.md) remain unassessed. Production identity, delegation, cancellation of accepted remote work, general run controls, budgets for time/tokens/money, bounded reconciliation polling, partial effects, load/security/accessibility assessment, and migration are not implemented.

The validator retains historical v0.1/v0.2 schemas for decoding. Runtime startup rejects nonempty older host/provider stores. Preserve those stores; use a fresh fixture directory instead of replacing old evidence.
