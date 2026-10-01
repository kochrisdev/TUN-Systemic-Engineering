# TUN Systemic Engineering — Integration Checklist

Status: adoption worksheet; unchecked items are not implementation evidence.

[Documentation index](README.md) · [Specification](SPECIFICATION-v0.1.md) · [Conformance matrix](CONFORMANCE-MATRIX.md) · [Validation plan](VALIDATION-PLAN-v0.1.md)

## Assessment header

Copy this worksheet into the adopting product's own review record and fill in:

| Field | Value to record |
|---|---|
| Product and operation scope | Name the actions, targets, consequence classes, and downstream effects |
| Implementation revision | Source commit, build/configuration, and relevant provider versions |
| TUN baseline | Engineering specification commit and any design-library commit |
| Owner and reviewer | Responsible product, engineering, and operational roles; actual reviewer |
| Environment and date | Where and when the assessment was performed |
| Data and identity | Security scopes, authentication, sensitive content, and retention purpose |
| Evidence location | Access-controlled test reports and review records |
| Decision and gaps | Supported claim, open issues, owners, and planned resolution |

For each item record applicability, owner, evidence, result, and unresolved risk. Use justified not-applicable only where the capability is outside the declared scope.

## Intent and records

- [ ] Enumerate whole effects, including notifications, data access, and downstream disclosure.
- [ ] Identify actor, principal, owner, and stopping conditions.
- [ ] Separate record identity, business revision, and schema version.
- [ ] Validate untrusted requests, model output, messages, and persisted decision inputs.
- [ ] Define the material proposal fields, canonicalization, referenced content binding, and resource preconditions.
- [ ] Separate context available to the system from context actually used.

Requirements: [TSE-001](SPECIFICATION-v0.1.md#tse-001), [TSE-002](SPECIFICATION-v0.1.md#tse-002), [TSE-004](SPECIFICATION-v0.1.md#tse-004), [TSE-021](SPECIFICATION-v0.1.md#tse-021).

## Approval and authority

- [ ] Bind human decisions to the exact canonical proposal.
- [ ] Handle expired, changed, rejected, and withdrawn reviews without erasing earlier actions.
- [ ] Define C3 approval/delegation behavior and particular C4 approval.
- [ ] Derive identity and security scope from trusted context on every relevant path.
- [ ] Evaluate current policy before dispatch and block when required checks fail.
- [ ] Attenuate delegated rights and define explicit renewal and revocation behavior.
- [ ] Bind grants to the operation, actor, proposal, target, parameters, and validity limits.

Requirements: [TSE-003](SPECIFICATION-v0.1.md#tse-003), [TSE-005 through TSE-010](SPECIFICATION-v0.1.md#tse-005).

## Execution and provider guarantees

- [ ] Declare the dispatch boundary and its ordering with permission changes.
- [ ] Enforce resource preconditions at the effect boundary where supported; record remaining races.
- [ ] Distinguish a logical operation from each invocation attempt.
- [ ] Declare provider key scope, retention, parameter matching, concurrency, hidden SDK retries, and uncovered effects.
- [ ] Reserve dispatch durably and prevent competing workers from treating it as new work.
- [ ] Exercise crash windows and restart recovery against provider-side evidence.
- [ ] Block unsafe retries, including when duplicate protection has expired.
- [ ] Bound time, calls, retries, and cost; define escalation after exhaustion.

Requirements: [TSE-011 through TSE-016](SPECIFICATION-v0.1.md#tse-011), [TSE-023](SPECIFICATION-v0.1.md#tse-023).

## Evidence, privacy, and receipts

- [ ] State the exact claim each verification method can establish.
- [ ] Bind evidence to the operation, source, target, revision, and observation time.
- [ ] Preserve unknown, partial, unavailable, and contradictory outcomes.
- [ ] Project receipts from host records; do not generate them from callback success.
- [ ] Filter private source content and metadata before transmission.
- [ ] Label quotation, paraphrase, and generated interpretation accurately.
- [ ] Document memory use separately from retention, deletion, backups, and training.
- [ ] Define journal integrity, correction, retention, and content-unavailability behavior.
- [ ] Correlate late events without relying on wall-clock order alone.

Requirements: [TSE-017 through TSE-022](SPECIFICATION-v0.1.md#tse-017), [TSE-027](SPECIFICATION-v0.1.md#tse-027).

## Supervision and recovery

- [ ] Offer only controls the runtime supports and disclose their effective boundary.
- [ ] Bind control requests and evidence to exact control/run revisions.
- [ ] Distinguish requested, acknowledged, and effective intervention.
- [ ] Preserve in-flight and completed effects after a stop request.
- [ ] Authorize recovery reads and writes appropriately.
- [ ] Distinguish reconciliation, retry, restoration, correction, and compensation.
- [ ] Protect intervening edits and retain history when recovery fails.

Requirements: [TSE-024 through TSE-026](SPECIFICATION-v0.1.md#tse-024).

## Interface, quality, and operations

- [ ] Pin the design-library revision and test the actual projection mappings used.
- [ ] Review keyboard controls, focus, status announcements, material details, and meaning without color.
- [ ] Record unsupported mappings and host views needed for unknown or conflicting states.
- [ ] Validate contract and adapter compatibility across upgrades.
- [ ] Evaluate product/content quality separately from execution correctness.
- [ ] Review changes to models, prompts, policy, data reuse, and tools.
- [ ] Assign operational ownership, unresolved-operation alerts, and recovery runbooks.
- [ ] Document an assessment against every applicable requirement and its actual evidence.

Requirements: [TSE-028 through TSE-032](SPECIFICATION-v0.1.md#tse-028).

## Outcome

Summarize what was demonstrated, what remains unassessed, and which residual limits matter to users. An applicable unmet mandatory requirement prevents a full scoped claim. Passing a subset of scenarios can still be useful when described as that subset.

This worksheet is a review aid. The specification remains the source of obligations, and the validation plan describes the proposed evidence procedures.
