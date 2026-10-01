# TUN Systemic Engineering — Contracts v0.1

Status: proposed record model; no released schemas, SDK, or transport API.

[Documentation index](README.md) · [Specification](SPECIFICATION-v0.1.md) · [Glossary](GLOSSARY.md) · [Lifecycles](LIFECYCLES-v0.1.md)

## Reading this document

This document translates the specification into candidate record shapes. Field names are design proposals, not supported imports or a promise of wire compatibility. The specification defines required behavior. A future schema release will fix required fields, unions, field limits, and migration rules.

Engineering and design records can share names such as `ActionProposal` or `ContextSnapshot` without being interchangeable. The [presentation adapter](DESIGN-INTEGRATION-v0.1.md) owns that conversion.

## Common conventions

| Concept | Proposed representation |
|---|---|
| Record identity | Opaque host-issued `id`, scoped to its record family and security domain |
| Record revision | Opaque string `version`; an immutable revision reference is `{ id, version }` |
| Schema version | Separate `schemaVersion`; never used as a business revision |
| Security scope | Host-derived tenant/account scope, including an explicit scope for single-tenant applications |
| Actor and producer | Identity of the acting principal and the trusted service that created the record |
| Time | Explicit timezone and seconds; separate event, observation, and recording times when they differ |
| Causality | Operation, attempt, parent-event, and producer-sequence references where relevant |
| Integrity | Material binding plus trusted storage or authenticated provenance appropriate to the boundary |
| Visibility | Access and retention policy references, with payload content held separately when useful |

An ID or digest is not a permission token. An authenticated request still needs object-level access checks. Sorting events by client timestamps does not establish cross-service causality.

## Core records

### ActionProposal

Canonical description of one action revision.

Proposed fields: `id`, `version`, `intentRef`, `actorRef`, `actionType`, `targetRef`, `parameters`, `expectedEffects`, `consequence`, `classificationBasis`, `preconditions`, `validity`, `recovery`, `reviewBasis`, and `materialBinding`.

The material binding covers the canonical action-specific field set, including referenced content versions or digests. It records the canonicalization and digest method. Display text can be a projection, but review must expose the material meaning of the bound action.

A resource precondition can describe an expected revision. A changed resource can invalidate execution even when the proposal itself has not been edited.

### ApprovalDecision

An authenticated person's decision about one proposal revision.

Proposed fields: proposal reference, material binding, principal reference, decision `approve` or `reject`, decision time, and an identity for deduplicating decision submission.

Withdrawal or supersession is a later event affecting decision eligibility, not an edit to what the person originally decided. Repeated submission should resolve to a consistent record; a new decision needs an explicit relationship to earlier decisions.

### AuthorizationDecision

A host policy evaluation at a particular time.

Proposed fields: proposal reference, principal and executing actor references, policy revision, permission/delegation references, applicable approval reference, result `allow` or `deny`, bounded scope, validity conditions, and a safe explanation.

The record distinguishes an approval-based decision from a delegation-based decision. A denied evaluation produces no executable grant. An allowed evaluation can cease to be usable before dispatch.

### ExecutionGrant

A bounded authorization artifact resolved by the executor.

Proposed fields: authorization reference, operation identity, proposal reference and material binding, executing actor, security scope, permitted action and target, validity interval, revocation reference, and dispatch-use constraints.

An internal database record can serve this role. If represented as a token across a trust boundary, authenticity, audience, expiry, revocation, and replay behavior need an explicit transport design. Token possession alone is not a reason to accept substituted parameters.

### OperationRecord

Stable identity of the intended logical action.

Proposed fields: `operationId`, proposal reference, material binding, current grant references, provider namespace and idempotency identity, aggregate revision, attempt references, known-effect references, verification references, and unresolved conditions.

One approved proposal revision normally resolves to one operation in the pilot. Creating a second intentional occurrence requires an explicit new action; retries do not create a new occurrence. A replacement proposal cannot erase an unresolved operation.

For a composite action, child operations or effect identifiers need their own mappings. The first pilot uses one publication effect.

### ExecutionAttempt

One bounded invocation attempt for an operation.

Proposed fields: `attemptId`, `operationId`, grant reference, worker identity, dispatch reservation, provider request identity, adapter revision, start/end times, lifecycle state, and observations.

Attempt identity changes for each permitted invocation. Operation and applicable provider idempotency identity remain stable. Automatic SDK retries need a declared mapping to attempts or transport sub-attempts; the history cannot imply only one outbound call when several occurred.

### VerificationRecord

An assessment of a claim based on evidence.

Proposed fields: claim text/type, operation reference, relevant attempts or provider effects, target and content/resource revisions, evidence references, method and method version, source authority, observed/assessed times, result, limitations, and reviewer or verifying service.

Proposed results are `pending`, `verified`, `contradicted`, and `unavailable`. These are assessment states, not a numeric confidence scale. A partial effect can contain a verified subclaim while the complete operation remains unresolved.

A later assessment links to its predecessor and explains what changed.

### ActionRecord

Versioned, host-owned aggregate used to produce receipts and operational views.

Proposed fields: operation reference, actor, proposal and decision references, activity summary, established effects, unresolved effects, verification summaries, material limitations, recovery offers, and the record revision.

The aggregate can change as observations arrive while the underlying proposal and historical decisions remain immutable. A user-visible receipt is an access-filtered projection of this record, not a separately authored account of success.

## Supporting records

| Record | Key content |
|---|---|
| `IntentContract` | Desired outcome, owner, constraints, scope, assumptions, stopping condition |
| `ContextSnapshot` | Versioned source manifest; availability, actual usage, provenance, permitted persistence |
| `PlanRecord` | Intent/context references, steps, dependencies, review checkpoints, limitations |
| `DelegationRecord` | Delegator/delegate, operations, targets, validity, budgets, exceptions, revocation |
| `ActivityObservation` | Producer, run/attempt, observed activity, time, known effects, optional measured progress |
| `EffectRecord` | Identified effect, provider reference, target/content binding, observation and verification relationships |
| `InterventionRequest` | Control and run references, requester, requested effect, limits, acknowledgement |
| `ControlOutcome` | Matching control/run references, observed intervention result, scope, time, evidence |
| `RecoveryOperation` | Original operation, kind, known original outcome, safeguards, new action or read references |
| `EvidenceReference` | Source identity, access scope, version, location/digest when applicable, availability, retention |

Supporting structures may be embedded initially. They describe responsibilities, not mandatory independent database tables.

## Cross-record invariants

- Decision, grant, and operation resolve to the same proposal revision and material meaning.
- Security scope and actor references are checked by the host, not copied from an untrusted request.
- A changed proposal cannot reuse earlier approval; a retry cannot substitute changed parameters.
- An attempt always identifies its operation and applicable grant.
- Verification identifies the claim it supports; evidence for another target or revision does not transfer.
- A control outcome matches both the control revision and run revision requested.
- Recovery references the original operation and preserves its effects even when the recovery succeeds.
- A new projection revision does not change the meaning of historical records.

These relationships need semantic validation in addition to schema validation.

## Illustrative state projection

This is a partial explanatory JSON example, not a complete runtime input:

```json
{
  "operationId": "op-publication-01",
  "attemptId": "attempt-publication-01",
  "proposalRef": {
    "id": "proposal-publication-01",
    "version": "3"
  },
  "attemptState": "ended",
  "effectKnowledge": "unknown",
  "verificationState": "pending",
  "explanation": "Provider response was lost; reconcile the original operation."
}
```

The ended attempt does not establish that publication failed. A later verification assessment can resolve the same operation without another write.

## Versioning and next decisions

Before publishing schemas, settle the required envelope, exact state unions, fingerprint representation, duplicate JSON-key handling, and transport limits. Include valid and invalid fixtures for cross-record mismatches and schema evolution.

Persist schema and adapter revisions with records needed for restart recovery. Reject unsupported versions at active decision boundaries; migrations need review of approval bindings and preserved interpretation.

The [status page](STATUS-AND-ROADMAP.md) tracks these as future implementation work.
