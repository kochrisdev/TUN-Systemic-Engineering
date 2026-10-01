# TUN Systemic Engineering — Design Integration v0.1

Status: broader mapping remains proposed; the local pilot implements a two-component adapter for ApprovalGate and ActionReceipt.

[Documentation index](README.md) · [Components](COMPONENTS-v0.1.md) · [Contracts](CONTRACTS-v0.1.md) · [Lifecycles](LIFECYCLES-v0.1.md)

## Compatibility baseline

This guide inspects TUN Systemic Design at [commit 81b52e8](https://github.com/kochrisdev/TUN-Systemic-Design/tree/81b52e8d64c90891ef1340802502e398dc6c0340), specifically its [core contracts](https://github.com/kochrisdev/TUN-Systemic-Design/blob/81b52e8d64c90891ef1340802502e398dc6c0340/packages/react/src/contracts.ts), [review contracts](https://github.com/kochrisdev/TUN-Systemic-Design/blob/81b52e8d64c90891ef1340802502e398dc6c0340/packages/react/src/review-contracts.ts), [evidence contracts](https://github.com/kochrisdev/TUN-Systemic-Design/blob/81b52e8d64c90891ef1340802502e398dc6c0340/packages/react/src/evidence-contracts.ts), and [supervision contracts](https://github.com/kochrisdev/TUN-Systemic-Design/blob/81b52e8d64c90891ef1340802502e398dc6c0340/packages/react/src/supervision-contracts.ts).

The design library has fourteen presentation components. The twelve engineering components are host responsibilities, so the relationship is many-to-many.

Matching names do not establish type compatibility. The [local review pilot](REVIEW-AND-RECOVERY-PILOT.md) uses a [vendored subset](../ui/vendor/tun-design/README.md) at this exact revision, with its CC0 license preserved. The Python [projection adapter](../reference/tse_pilot/presentation.py) supplies the view; the [React host](../ui/src/App.tsx) renders the two components. Other components below are not integrated.

## Pattern mapping

| Design component | Engineering source and responsibility |
|---|---|
| `IntentComposer` | EC-01 accepts scoped intent; the host validates any candidate parameters |
| `AgentCard` | EC-05 supplies actor identity and delegated authority; operational labels remain projections |
| `ContextPanel` | EC-02 supplies an access-filtered context manifest with availability and actual usage |
| `PlanView` | EC-01 supplies steps and context references; plan approval does not authorize execution |
| `ProposalCard` | EC-03 supplies canonical material content; its review request is navigation |
| `ApprovalGate` | EC-04 records the bound human decision; EC-05 separately authorizes dispatch |
| `ActionReceipt` | EC-08 and EC-09 produce the action record; EC-12 maps its supported claims |
| `MemoryIndicator` | EC-02 supplies actual memory use and a separate retention explanation |
| `SourceView` | EC-09 supplies permitted evidence, provenance, relationships, and access limitations |
| `UncertaintySignal` | EC-09 supplies a scoped assessment with a basis; it cannot grant authority |
| `ToolActivity` | EC-06/EC-07 observations identify tool, target, category, and known effects |
| `AgentActivity` | EC-06/EC-08 supply run observations, blockers, and measured progress |
| `HumanOverride` | EC-10 handles a control bound to a run revision and returns observed control evidence |
| `RecoveryControl` | EC-11 supplies supported recovery; effectful recovery returns through authority and execution |

Component responsibilities are described in the [catalog](COMPONENTS-v0.1.md).

## Proposal and approval bridge

The design `ActionProposal` uses string `id` and `version`, displayable action and target, actor, consequence, effect, authority explanation, and recovery description. Optional `contentPreview`, `reviewBasis`, and `expiresAt` add review context.

The engineering host needs additional canonical parameters, policy references, material binding, and preconditions. It retains those records and sends an authorized presentation projection. Material details still need to be reviewable; filtering cannot hide the consequences needed for informed approval.

`ApprovalGate` emits a `DecisionRequest` containing `proposalId`, `proposalVersion`, and `decision` (`approve` or `reject`). The host authenticates the caller and resolves the exact canonical proposal. It records the decision and then evaluates authority.

The browser's proposal fingerprint and local duplicate-submission latch are supplementary checks. They do not authenticate the host's records or deduplicate across tabs, retries, restarts, and workers.

The UI's `approved` label reflects a decision lifecycle. If execution is denied later, the application also displays the denial and reason rather than implying that approval is sufficient.

## Receipt mapping and gaps

At the inspected design revision, `ReceiptStatus` contains `completed`, `partially-completed`, `failed`, `reversed`, and `pending-verification`. Verification state contains `verified`, `pending`, and `unavailable`. There is no dedicated receipt status for unknown or contradicted.

| Engineering fact | Proposed presentation |
|---|---|
| Expected publication is verified | `completed`, with verification detail limited to that publication claim |
| Known partial effect | `partially-completed` with an explicit account of established and unresolved effects |
| Outcome still unknown | `pending-verification`, with “Outcome unknown” in the summary and the supported next step |
| Verification service unavailable | `pending-verification` and `unavailable`, with the access or service limitation explained |
| Evidence contradicts the claim | Keep the claim unconfirmed, show the contradiction explicitly in the host view and `SourceView`; no silent conversion to success |
| Known failure | `failed`, stating any partial effects rather than implying no effect |
| Relevant prior state demonstrably restored | `reversed` only within that verified scope, with unrecoverable consequences disclosed |
| Compensation completed | A separate receipt for the compensating operation; the original action is not relabelled reversed |

If a flat receipt cannot faithfully express verified partial effects alongside unresolved effects, compose a host detail view. Do not erase information to fit an enum. Receipt timestamps come from the supported observation/assessment, not from the time the browser rendered it.

The local adapter implements completed, pending, unavailable, contradicted, blocked, and verified-rejection projections. Contradictions become pending-verification with explicit contradiction text; blocked dispatch becomes failed with a no-provider-call explanation. A verified correction or withdrawal has a separate completed receipt and never relabels the original reversed. SourceView, partial effects, and reversal are not implemented. Focused tests are not complete adapter acceptance or human-factors validation.

## Activity and controls

The design `ActivityRecord` already includes `unknown` and `partial` activity statuses, an observation time, effects, and optional evidence and progress. It is a host observation, not a universal operation state.

`ControlRequest` binds `controlId`, `controlVersion`, `runId`, and `runVersion`. Terminal `ControlEvidence` references the same tuple, an outcome, observation time, and explanation. The host enforces authenticity, authority, actual worker behavior, and record freshness.

The current `RecoveryOperation` allows only reconciliation when `originalOutcome` is `unknown`. A retry with a known outcome additionally requires `retrySafety` text. That explanation describes the host safeguard; it does not implement it. Preserve this UI restriction even if an adapter has a more permissive transport-level retry policy.

## Evidence, memory, and uncertainty

Filter source identities, excerpts, and URLs before sending data to the component. Hiding a restricted panel after transmission does not protect its contents.

Map memory use to M0–M3 with scope and actual influence. Store retention, backups, audit history, and training policies separately. Map uncertainty to U0–U3 only with a stated claim and basis; do not derive it from the model's self-rating or an operation status.

The design timestamp parser expects an explicit timezone, seconds, and at most millisecond precision. A projection may format timestamps for this contract while retaining original precision and provenance in the host record.

## Adapter acceptance

Exercise exact proposal revisions, lost decision acknowledgements, a denied dispatch after approval, unknown and partial effects, evidence contradictions, late control results, and cross-tenant reads.

Also review keyboard operation, focus, announcements, readable action details, reduced motion, and status meaning without color. Component samples cannot establish complete accessibility of a consuming application. Record the tested design commit and host revision with the evidence.
