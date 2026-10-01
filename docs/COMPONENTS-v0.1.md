# TUN Systemic Engineering — Components v0.1

Status: draft logical component catalog. The [local pilot](PILOT.md) combines selected responsibilities; these are not twelve implemented packages.

[Documentation index](README.md) · [Specification](SPECIFICATION-v0.1.md) · [Architecture](ARCHITECTURE.md) · [Design integration](DESIGN-INTEGRATION-v0.1.md)

## What a component means

An engineering component is a responsibility with explicit inputs, outputs, trust boundaries, and failure behavior. The twelve components below are proposed logical building blocks. They can share a process, database, or module. They are not package exports or a requirement to deploy twelve services.

The specification supplies the obligations; this catalog describes one way to assign them. A product owner still owns usefulness and AI quality, and an operational owner still owns the deployed service.

## Catalog

| ID | Component | Primary output |
|---|---|---|
| EC-01 | Intent and planning coordinator | Scoped intent and reviewable plan |
| EC-02 | Context and record boundary | Validated records and context manifest |
| EC-03 | Proposal registry | Immutable canonical proposal revision |
| EC-04 | Human decision service | Bound approval or rejection |
| EC-05 | Authority service | Authorization decision and bounded grant |
| EC-06 | Operation coordinator | Durable operation and execution attempts |
| EC-07 | Tool adapter | Provider request and correlated observation |
| EC-08 | Journal and action projection | Causal history and versioned action record |
| EC-09 | Evidence and reconciliation service | Scoped verification assessment |
| EC-10 | Supervision controller | Control request and observed intervention result |
| EC-11 | Recovery coordinator | Authorized response to known or unresolved effects |
| EC-12 | Presentation adapter | Access-filtered review, activity, and receipt views |

## EC-01

**Intent and planning coordinator**

Purpose: capture the desired outcome, constraints, responsible owner, and stopping conditions. Inputs may include natural language and candidate model plans. Outputs are an `IntentContract` and, where useful, a `PlanRecord`.

It resolves material ambiguity and records assumptions. It can propose consequential actions but cannot grant their authority. A reviewed plan has no implied blanket approval. If the plan or goal changes, affected proposals return to review.

The product team attaches output-quality evaluation and change-review evidence here. Acceptance includes identifying downstream consequences and separating answer quality from successful execution.

Related rules: [TSE-001](SPECIFICATION-v0.1.md#tse-001), [TSE-030](SPECIFICATION-v0.1.md#tse-030).

## EC-02

**Context and record boundary**

Purpose: validate incoming and stored records and construct scoped context manifests. Inputs include source records, access policy, and supported schema versions. Outputs identify sources, versions, actual usage, provenance, and availability.

This responsibility is shared across API ingress, worker messages, model outputs, and persisted data read during recovery. Validation checks structure and cross-record meaning. Untrusted values cannot supply the effective identity or security scope.

Unavailable context is explicit. Deleted source content may leave a manifest with an unavailable reference; it does not become fabricated evidence or a promise of reproducible replay.

Related rules: [TSE-002](SPECIFICATION-v0.1.md#tse-002), [TSE-021](SPECIFICATION-v0.1.md#tse-021).

## EC-03

**Proposal registry**

Purpose: establish the precise action that a person can review. The registry takes candidate parameters and host-resolved resource identity, computes a material binding, and creates an immutable `ActionProposal` revision.

It stores expected effects, resource preconditions, consequence classification, validity limits, and recovery disclosure. Material change produces another revision. Expiring or superseding a proposal does not erase earlier attempts or effects.

Failure behavior: reject inconsistent same-version content and block dispatch against stale resource conditions.

Related rule: [TSE-004](SPECIFICATION-v0.1.md#tse-004).

## EC-04

**Human decision service**

Purpose: record what an authenticated person decided about an exact proposal. It consumes an identity-only decision request and looks up canonical content; it does not accept replacement executable parameters.

The service checks that the proposal can still be reviewed, then records an `ApprovalDecision`. Duplicate delivery of the same request returns a consistent acknowledgement. Withdrawal is a new recorded event. Rejecting an undispatched proposal and cancelling a running operation remain separate actions.

Its acknowledgement confirms storage of a decision, with no assertion that execution occurred.

Related rules: [TSE-005](SPECIFICATION-v0.1.md#tse-005), [TSE-006](SPECIFICATION-v0.1.md#tse-006), [TSE-007](SPECIFICATION-v0.1.md#tse-007).

## EC-05

**Authority service**

Purpose: enforce current identity, security scope, permissions, policy, and delegation. Inputs include the proposal and applicable approval or delegation. Outputs are an allow/deny `AuthorizationDecision` and, when allowed, an `ExecutionGrant`.

The authority service can integrate an existing policy engine or identity provider. The model and presentation layer cannot override its decision. Unavailable mandatory checks result in a blocked dispatch.

Delegated rights are narrowed by host policy. C4 operations still need particular human approval. Grants are bounded records; using an external token is an implementation choice requiring its own authenticity and replay controls.

Related rules: [TSE-003](SPECIFICATION-v0.1.md#tse-003), [TSE-008](SPECIFICATION-v0.1.md#tse-008), [TSE-009](SPECIFICATION-v0.1.md#tse-009), [TSE-010](SPECIFICATION-v0.1.md#tse-010).

## EC-06

**Operation coordinator**

Purpose: manage one logical operation across scheduling, attempts, restarts, budgets, and permitted retries. It consumes a grant, reserves the operation durably, rechecks authority and preconditions at dispatch, and invokes the adapter with canonical parameters.

The coordinator distinguishes new intended work from redelivery. It uses an atomic claim or equivalent concurrency control, and records how worker ownership is fenced. A timed-out lease alone does not prove that the previous worker or provider has stopped.

A restart recovers unresolved reservations for reconciliation. Budget exhaustion blocks further dispatch while leaving completed and in-flight effects inspectable.

Related rules: [TSE-011](SPECIFICATION-v0.1.md#tse-011), [TSE-012](SPECIFICATION-v0.1.md#tse-012), [TSE-023](SPECIFICATION-v0.1.md#tse-023).

## EC-07

**Tool adapter**

Purpose: translate an authorized operation into a provider call and return a correlated observation. It exposes documented capabilities for effects, idempotency, lookup, cancellation, and recovery.

The adapter declares request identity scope, parameter comparison, retention, retry behavior, and provider errors. SDK-level retries are part of that declaration. It uses credentials available through controlled host execution, rather than allowing the model direct unchecked access.

It returns what the provider established: for example, accepted, rejected before effect, or ambiguous. An adapter cannot turn a transport timeout into proof of no effect.

Related rules: [TSE-013](SPECIFICATION-v0.1.md#tse-013), [TSE-029](SPECIFICATION-v0.1.md#tse-029).

## EC-08

**Journal and action projection**

Purpose: persist dispatch reservations, attempts, observations, known effects, and subsequent assessments. It provides causal history and a versioned `ActionRecord`.

A transaction protects local invariants; it cannot make an external provider call part of the same transaction. Failure before reservation blocks dispatch. Failure after dispatch creates a reconciliation obligation.

Projections preserve separate status dimensions and late evidence. Access, retention, integrity controls, monitoring, and operational recovery are explicit responsibilities of the owning host team.

Related rules: [TSE-014](SPECIFICATION-v0.1.md#tse-014), [TSE-016](SPECIFICATION-v0.1.md#tse-016), [TSE-022](SPECIFICATION-v0.1.md#tse-022), [TSE-027](SPECIFICATION-v0.1.md#tse-027), [TSE-031](SPECIFICATION-v0.1.md#tse-031).

## EC-09

**Evidence and reconciliation service**

Purpose: assess a defined claim from appropriate evidence and determine what is known about an unresolved operation. It consumes operation references, provider lookup results, and source provenance; it emits `VerificationRecord` assessments.

Reconciliation is a read or evidence-gathering process. It does not automatically replay a write. Negative results have a declared consistency/finality interpretation. Evidence that cannot be tied to the operation may support a state claim without establishing causality.

Conflicting, restricted, stale, and missing evidence remain distinct. This component owns the scope of claims, not the authority to repair state.

Related rules: [TSE-015](SPECIFICATION-v0.1.md#tse-015), [TSE-017](SPECIFICATION-v0.1.md#tse-017), [TSE-018](SPECIFICATION-v0.1.md#tse-018), [TSE-020](SPECIFICATION-v0.1.md#tse-020).

## EC-10

**Supervision controller**

Purpose: accept authorized intervention requests and observe their actual effect. Requests bind control identity and revision to the intended run and revision.

Capabilities can include stopping new dispatches, pausing at a checkpoint, cancelling a provider request, revoking further authority, or transferring control. Their availability and limitations are specific to the executor.

An acknowledgement means the request was accepted. Confirmation needs evidence of the described intervention. The controller preserves already completed work and reports effects that can continue.

Related rule: [TSE-024](SPECIFICATION-v0.1.md#tse-024).

## EC-11

**Recovery coordinator**

Purpose: choose and prepare a supported response to a failure or unwanted effect. It uses the original action record, current resource state, provider capabilities, and recovery policy.

It proposes reconciliation, safe retry, restoration, correction, compensation, or escalation. Reads use applicable access permission; writes return through the normal approval and authorization path.

Recovery creates linked history. A failed compensation can leave both the original effect and a partial compensating effect requiring further attention.

Related rules: [TSE-025](SPECIFICATION-v0.1.md#tse-025), [TSE-026](SPECIFICATION-v0.1.md#tse-026).

## EC-12

**Presentation adapter**

Purpose: turn authorized host records into intelligible reviews, activity, evidence, and receipts. It also translates user requests back into reference-bound host commands.

The adapter handles differences between engineering records and presentation types. It cannot infer authority from a UI enum or conceal a state that a component does not support. The [design integration guide](DESIGN-INTEGRATION-v0.1.md) maps all fourteen design patterns and records the current type limitations.

Related rules: [TSE-019](SPECIFICATION-v0.1.md#tse-019), [TSE-028](SPECIFICATION-v0.1.md#tse-028), [TSE-032](SPECIFICATION-v0.1.md#tse-032).

## Composition and implementation order

For the first publication pilot, combine EC-03 through EC-06 in one host service, EC-08 in its durable store, and EC-07 in one provider adapter. Add explicit verification through EC-09 and the two essential presentation paths through EC-12: approval and receipt.

Support EC-10 only to the extent the pilot can genuinely cancel undispatched work. Add EC-11 for reconciliation and separately approved withdrawal. General multi-agent orchestration and production deployment can follow after those paths have evidence.
