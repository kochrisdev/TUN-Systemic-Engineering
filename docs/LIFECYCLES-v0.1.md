# TUN Systemic Engineering — Lifecycles v0.1

Status: draft lifecycle guidance; vocabulary is not a released runtime enum.

[Documentation index](README.md) · [Specification](SPECIFICATION-v0.1.md) · [Contracts](CONTRACTS-v0.1.md) · [Authority and execution](AUTHORITY-AND-EXECUTION-v0.1.md)

## Separate records answer separate questions

A single status field cannot express whether a proposal remains valid, whether a person approved it, whether the host allows it now, and whether an external effect occurred.

| Lifecycle | Question | Illustrative states |
|---|---|---|
| Proposal | Is this revision reviewable and usable? | Draft, ready, expired, superseded |
| Human decision | What did this person decide? | Approved, rejected, later withdrawn |
| Authorization | Did this host evaluation allow dispatch? | Allowed, denied |
| Grant eligibility | Can this executor use the grant now? | Usable, expired, revoked, consumed or otherwise unavailable |
| Attempt | What happened to this invocation? | Queued, running, ended |
| Effect knowledge | What is established about the effects? | Unassessed, unknown, partial, observed expected effect, confirmed no effect |
| Verification | Does evidence support a specific claim? | Pending, verified, contradicted, unavailable |
| Intervention | What happened to this control request? | Requested, acknowledged, effective, failed, unknown |

These labels describe independent dimensions. Implementations may choose other terms while preserving their meaning. “Approved” on a plan or proposal is not the current authorization result.

## Proposal and decision lifecycle

A candidate becomes ready only after host validation and canonicalization. Decisions reference that exact revision and material binding.

A material edit creates a new revision; prior approval cannot transfer. Supersession affects eligibility for future dispatch. It cannot erase an earlier dispatch or its effects. If the original operation is unresolved, preparing equivalent replacement work does not make a second write safe.

Expiry is evaluated using a trusted host clock at review and dispatch. It prevents new uses of expired authority; it does not retroactively negate a legitimately dispatched action. Evidence for that action remains available under applicable read permissions.

Rejection means the particular proposal was rejected. Withdrawal changes the eligibility of prior consent. If work is already dispatched, intervention is a separate request.

## Dispatch lifecycle

| Transition | Guard | Recorded result |
|---|---|---|
| Review → decision recorded | Authenticated principal; exact, valid proposal | Human decision and deduplicated acknowledgement |
| Decision/delegation → authorization | Current policy and scope; required approval present | Allow or deny evaluation |
| Authorization → reservation | Authentic bounded grant; operation not already reserved inconsistently | Durable operation identity and dispatch intent |
| Reservation → invocation | Current dispatch checks, resource preconditions, worker ownership, budgets | Attempt and provider request binding |
| Invocation → observation | Correlation and producer checks | Acknowledgement, error, progress, or effect evidence |
| Observation → assessment | Evidence checks for a defined claim | Pending, verified, contradicted, or unavailable assessment |

Reservation does not prove dispatch occurred. After a crash, the host may be unable to distinguish a reserved-but-unsent request from one sent before the crash. Both require reconciliation when replay could duplicate effects.

## Lost-response walkthrough

| Moment | Attempt/activity | Effect knowledge | Verification | Next supported action |
|---|---|---|---|---|
| Proposal approved | No attempt | Unassessed | Not yet requested | Host authorization |
| Durable reservation made | Queued or preparing | Unassessed | Not yet requested | Guarded dispatch |
| Provider commits; response lost | Attempt ends ambiguously | Unknown to host | Pending | Reconcile original operation |
| Host restarts | No new invocation | Still unknown | Pending | Resume evidence lookup |
| Matching provider record found | Earlier attempt retained | Expected effect observed | Verified for publication claim | Show scoped receipt |
| Readback unavailable instead | Earlier attempt retained | Still unknown | Unavailable | Explain limitation and escalate |

The provider's actual state and the host's knowledge of that state can differ. The host reports what its evidence supports.

## Acknowledgements and late evidence

Acknowledgement is an event, not a required stage before every observation. Provider callbacks may arrive before a client response, and a response can arrive after the client has stopped waiting.

Correlate by operation, provider request/effect identity, and relevant revisions. Maintain per-producer order and causal references where available. A later wall-clock timestamp alone does not outrank an earlier authoritative fact.

When new evidence contradicts a receipt, record a revised assessment, explain the conflict, and update the accessible projection. Preserve the original assessment and avoid launching recovery from an unverified interpretation.

## Retry eligibility

Retry is a guarded decision about the same logical operation. It requires current authority, unchanged material parameters, applicable duplicate protection, and a policy that permits another attempt.

Reconciliation should precede a new effectful attempt after ambiguity. If the result remains unknown, any provider-supported repeat needs an explicit still-valid safeguard; otherwise automatic execution remains blocked. A fresh operation ID, a lease timeout, or a new human click does not supply that safeguard.

The current design `RecoveryControl` is stricter: it permits only reconciliation while the original outcome is unknown. The [design integration guide](DESIGN-INTEGRATION-v0.1.md) preserves that boundary.

## Intervention and recovery lifecycle

An intervention is requested, acknowledged, and then assessed against its promised scope. “Stop effective” can mean that no new work will be dispatched while an already accepted provider action can finish. Describe that scope explicitly.

Reconciliation can resolve knowledge without creating another effect. A correction, restoration, compensation, or withdrawal is a new linked operation with its own decision and execution history. A retry keeps the original logical operation and adds a new attempt.

The original action record remains inspectable even after recovery. See [Supervision and recovery](SUPERVISION-AND-RECOVERY-v0.1.md).

## State review questions

Can the system represent an approved but denied action? A stopped worker with an unknown effect? A verified partial effect? A failed compensation? An expired grant with readable historical evidence?

If the answer depends on forcing all facts into one status, the state model needs another dimension.
