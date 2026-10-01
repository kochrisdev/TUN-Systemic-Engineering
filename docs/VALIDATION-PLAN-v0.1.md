# TUN Systemic Engineering — Validation Plan v0.1

Status: planned procedures; no runtime scenario below has been executed in this repository.

[Documentation index](README.md) · [Specification](SPECIFICATION-v0.1.md) · [Conformance matrix](CONFORMANCE-MATRIX.md) · [Threat model](THREAT-MODEL.md)

## How to use this plan

Each procedure defines a setup, expected observation, and evidence to retain. Adapt it to the real provider, implementation, and product scope. Preserve the requirement's meaning when changing the test method.

Use fixtures and a controlled provider for fault injection. Record the exact source revision, dependency/provider versions, environment, inputs, commands or manual steps, results, reviewer, and evidence locations. Exclude credentials and private payloads from shared reports.

An automated assertion can establish a narrow runtime fact. Policy review, provider guarantees, accessibility, retention, and operating practice may require separate inspection. A procedure can therefore need both executable and human evidence.

Results are recorded as not assessed, pass, fail, or justified not applicable. Recommendation departures require a documented assessment. No outcome is pre-filled here.

## Procedures

### V-01

**Scope review.** Source: [TSE-001](SPECIFICATION-v0.1.md#tse-001).

Setup and action: Select a publication operation that also sends a notification. Inspect its scope inventory, actors, owner, consequence rationale, and downstream targets.

Expected observation: The review covers both publication and notification, including any disclosure. A C0 answer label does not remove the underlying action from scope.

Evidence: Reviewed operation inventory and owner decision.

### V-02

**Boundary validation.** Source: [TSE-002](SPECIFICATION-v0.1.md#tse-002).

Setup and action: Submit malformed records, unsupported versions, ambiguous duplicate JSON keys, excessive fields, and references to the wrong record family. Load equivalent corrupt stored data before a decision.

Expected observation: Affected decisions and dispatches are blocked with bounded errors. No provider write occurs and no parser silently changes material meaning.

Evidence: Ingress and storage-validation results plus provider-effect count.

### V-03

**Identity and isolation.** Source: [TSE-003](SPECIFICATION-v0.1.md#tse-003).

Setup and action: Use two fixture tenants and an unauthorized principal. Substitute tenant, actor, target, receipt, and evidence identifiers across reads and commands.

Expected observation: The trusted identity controls scope. Cross-scope requests reveal neither private content nor sensitive metadata and cannot write.

Evidence: Request/response assertions, access decisions, and provider records.

### V-04

**Material revision.** Source: [TSE-004](SPECIFICATION-v0.1.md#tse-004).

Setup and action: Approve revision 1, then alter content, target, recovery conditions, or a bound resource version. Also change unrelated telemetry.

Expected observation: Changed material content requires a new revision and decision. Old approval cannot execute the new content; unrelated telemetry does not fabricate a material revision.

Evidence: Canonical records, comparison policy, and blocked-dispatch observation.

### V-05

**Decision binding.** Source: [TSE-005](SPECIFICATION-v0.1.md#tse-005).

Setup and action: Submit approval for a different revision, an expired proposal, and a duplicate decision request. Lose the decision acknowledgement and query the stored result.

Expected observation: Only a valid exact binding is recorded. Redelivery returns consistent decision identity; acknowledgement alone creates no effect or verified receipt.

Evidence: Human-decision records, readback after lost response, and absent provider effect.

### V-06

**C3 approval policy.** Source: [TSE-006](SPECIFICATION-v0.1.md#tse-006).

Setup and action: Exercise a C3 operation without approval, then with a valid bounded delegation. Inspect any documented departure from the recommendation.

Expected observation: Approval or the intended bounded delegation governs the normal path. Any departure records rationale and consequences and still passes authorization.

Evidence: Policy review, delegation limits, and any recommendation-departure record.

### V-07

**Particular C4 decision.** Source: [TSE-007](SPECIFICATION-v0.1.md#tse-007).

Setup and action: Provide plan approval, a general autonomy setting, and standing delegation for a C4 operation. Then provide approval of its exact proposal.

Expected observation: Only the particular recorded approval can satisfy the C4 decision condition; all other authority checks still apply.

Evidence: Denied and permitted decision paths with the exact review content.

### V-08

**Host authorization.** Source: [TSE-008](SPECIFICATION-v0.1.md#tse-008).

Setup and action: Inject source text or a model result claiming permission. Separately revoke permission and make the policy service unavailable before dispatch.

Expected observation: Untrusted assertions grant no rights. Missing or failed mandatory checks block the provider invocation.

Evidence: Policy decisions and adapter-call assertions.

### V-09

**Delegation attenuation.** Source: [TSE-009](SPECIFICATION-v0.1.md#tse-009).

Setup and action: Delegate to an agent with narrower target and time limits, then attempt sub-delegation with a larger target set or later expiry.

Expected observation: Effective rights remain within both the original delegation and current policy. Expired or expanded work is denied.

Evidence: Delegation chain and authorization results.

### V-10

**Grant binding.** Source: [TSE-010](SPECIFICATION-v0.1.md#tse-010).

Setup and action: Replay a grant for another operation, actor, tenant, proposal revision, or payload. Test an expired or unauthentic grant.

Expected observation: Executor resolves trusted canonical parameters and rejects mismatched uses without an effect.

Evidence: Grant validation results and provider-effect inspection.

### V-11

**Dispatch race.** Source: [TSE-011](SPECIFICATION-v0.1.md#tse-011).

Setup and action: Queue approved work, change permission or target revision, then release the worker. Separately revoke permission after provider acceptance.

Expected observation: The declared ordering blocks work revoked before the dispatch boundary. Accepted effects are reported honestly when they cannot be cancelled; conditional writes reject stale resources where supported.

Evidence: Race timeline, reservation/policy versions, and provider records.

### V-12

**Operation identity.** Source: [TSE-012](SPECIFICATION-v0.1.md#tse-012).

Setup and action: Deliver the same command repeatedly, restart, and attempt an equivalent replacement while the original operation is unresolved. Also prepare an intentionally distinct second action.

Expected observation: Redelivery and recovery retain operation identity. Unresolved work cannot be bypassed through replacement; distinct intended actions are explicitly identified.

Evidence: Operation/attempt relationships and provider identities.

### V-13

**Provider duplicate contract.** Source: [TSE-013](SPECIFICATION-v0.1.md#tse-013).

Setup and action: Run concurrent same-key requests, a changed-payload request with that key, a supported same-operation repeat, and a request after retention expires.

Expected observation: Behavior matches the declared provider guarantees. Parameter mismatch and expired protection do not silently create automatic duplicate effects.

Evidence: Adapter declaration, provider-side counts, payload checks, and retention-boundary results.

### V-14

**Crash windows.** Source: [TSE-014](SPECIFICATION-v0.1.md#tse-014).

Setup and action: Fail reservation persistence; then crash after reservation, during dispatch, and after provider commit but before host result persistence. Restart each case.

Expected observation: No dispatch occurs without the required durable reservation. Ambiguous reserved work survives and is reconciled without blind redispatch.

Evidence: Host/provider snapshots, crash injection points, and restart trace.

### V-15

**Ambiguous lookup.** Source: [TSE-015](SPECIFICATION-v0.1.md#tse-015).

Setup and action: Lose the provider response, delay read visibility, and make lookup unavailable. Advance the declared reconciliation window.

Expected observation: Empty or unavailable reads do not falsely prove no effect. Unknown status and operation identity persist; unsafe replay stays blocked and escalation becomes available.

Evidence: Lookup timing, consistency assumptions, and absence of unguarded writes.

### V-16

**Independent state dimensions.** Source: [TSE-016](SPECIFICATION-v0.1.md#tse-016).

Setup and action: Construct approved-but-denied, ended-attempt-with-unknown-effect, and acknowledged-stop-with-running-provider cases.

Expected observation: Projections preserve all dimensions without inventing total completion, no-effect failure, or effective cancellation.

Evidence: Stored records and rendered/API state assertions.

### V-17

**Evidence binding.** Source: [TSE-017](SPECIFICATION-v0.1.md#tse-017).

Setup and action: Supply authenticated evidence for a different target or revision, and unauthenticated or stale callbacks. Supply a correctly bound provider effect record afterward.

Expected observation: Only appropriate evidence can support the intended claim. Invalid evidence cannot produce verified completion.

Evidence: Evidence provenance, correlation checks, and assessment revisions.

### V-18

**Claim scope.** Source: [TSE-018](SPECIFICATION-v0.1.md#tse-018).

Setup and action: Verify provider acceptance without delivery evidence. Observe matching resource state without causal identity. Publish content containing a known quality defect.

Expected observation: Claims remain limited to acceptance or observed state as appropriate. Publication verification does not assert content truth.

Evidence: Receipt wording, evidence fields, and separate content-quality result.

### V-19

**Receipt truth.** Source: [TSE-019](SPECIFICATION-v0.1.md#tse-019).

Setup and action: Drive completed, partial, unknown, unavailable-verification, and contradicted cases, including a late reassessment.

Expected observation: Receipts derive from host records, preserve material unresolved effects, and retain the earlier assessment when revised.

Evidence: Action-record revisions and accessible receipt views.

### V-20

**Private evidence and sources.** Source: [TSE-020](SPECIFICATION-v0.1.md#tse-020).

Setup and action: Request private evidence as an unauthorized viewer. Include sensitive titles, URLs, exception messages, and generated text resembling a quote.

Expected observation: Filtering happens before transmission. Generated interpretations are labelled, contradictory sources remain visible to authorized viewers, and links enforce access.

Evidence: Payload inspection, link-access results, and source presentation review.

### V-21

**Memory boundaries.** Source: [TSE-021](SPECIFICATION-v0.1.md#tse-021).

Setup and action: Retain operational state beyond grant expiry, store a user preference, and disable personalization. Compare available context with the sources actually used.

Expected observation: No state or preference extends authority. Memory labels describe actual use and do not imply deletion of unrelated retained records.

Evidence: Memory-use inventory, expired-grant denial, and user-facing disclosure.

### V-22

**Retention and integrity.** Source: [TSE-022](SPECIFICATION-v0.1.md#tse-022).

Setup and action: Delete a permitted source payload under policy while retaining allowed historical metadata. Attempt unauthorized journal modification and inspect backup/restoration policy.

Expected observation: Evidence availability changes honestly; earlier assessments remain interpretable within retention scope. Integrity claims match actual storage controls.

Evidence: Deletion record, access-control results, and reviewed retention/backup policy.

### V-23

**Budgets and renewal.** Source: [TSE-023](SPECIFICATION-v0.1.md#tse-023).

Setup and action: Exhaust time, retry, tool-call, and cost budgets while one provider action is already in flight. Attempt implicit renewal after restart.

Expected observation: Further dispatch stops under the declared policy; in-flight effects remain visible. Renewal needs explicit current authority.

Evidence: Budget ledger, call counts, restart behavior, and renewal decision.

### V-24

**Intervention evidence.** Source: [TSE-024](SPECIFICATION-v0.1.md#tse-024).

Setup and action: Send a stale control/run revision, lose a control acknowledgement, and request stop during provider acceptance.

Expected observation: Wrong-run control is denied; request and effect remain separate. Confirmation states which work stopped and what may still finish.

Evidence: Bound control records, worker observation, and residual-effect view.

### V-25

**Recovery authority.** Source: [TSE-025](SPECIFICATION-v0.1.md#tse-025).

Setup and action: Attempt reconciliation with read permission only, then attempt withdrawal or compensation without write authority. Try recovery after the original grant expires.

Expected observation: Permitted reads can inspect the original operation. Writes need fresh applicable authorization and approval and preserve original history.

Evidence: Access results and linked recovery records.

### V-26

**Recovery semantics.** Source: [TSE-026](SPECIFICATION-v0.1.md#tse-026).

Setup and action: Restore a resource after another actor edits it, compensate an irreversible communication, and fail compensation partway.

Expected observation: Preconditions protect intervening work. Compensation is not labelled undo, and both original and recovery effects remain inspectable.

Evidence: Before/after resource revisions, recovery receipts, and partial-effect history.

### V-27

**Late observations.** Source: [TSE-027](SPECIFICATION-v0.1.md#tse-027).

Setup and action: Deliver out-of-order observations from producers with skewed clocks, including evidence contradicting an earlier assessment.

Expected observation: Correlation and causal references govern interpretation. Reassessment preserves contradictions and historical control/effect facts.

Evidence: Event sequence, producer identities, and revised action records.

### V-28

**Human control and accessibility.** Source: [TSE-028](SPECIFICATION-v0.1.md#tse-028).

Setup and action: Review a consequential action with keyboard-only input and an assistive-technology check. Exercise partial/unknown receipt mappings, stop controls, and reduced-motion settings.

Expected observation: Material details, rejection, and supported intervention remain usable and understandable. Missing enum support does not create false success.

Evidence: Named manual review environment, interaction results, and projection fixtures.

### V-29

**Compatibility change.** Source: [TSE-029](SPECIFICATION-v0.1.md#tse-029).

Setup and action: Upgrade an adapter or record schema and replay stored records. Pin a design-library revision and map all used states.

Expected observation: Unsupported versions block unsafe use. Migration preserves material/authority bindings; UI mappings and adapter guarantees are reassessed.

Evidence: Version inventory, migration fixtures, and adapter contract results.

### V-30

**Quality and change evaluation.** Source: [TSE-030](SPECIFICATION-v0.1.md#tse-030).

Setup and action: Change a model, prompt, tool, policy, or adapter using a fixed evaluation set with representative failure cases.

Expected observation: Execution invariants and relevant product/content quality receive separate results. Feedback does not silently introduce new authority or data use.

Evidence: Change review, evaluation-set version, and separate quality/correctness reports.

### V-31

**Operational ownership.** Source: [TSE-031](SPECIFICATION-v0.1.md#tse-031).

Setup and action: Simulate a long-unresolved operation and restore an older host snapshot while provider effects remain newer. Exercise the responder workflow.

Expected observation: A responsible role receives actionable information; unresolved effects are reconciled before resuming unsafe writes. Service claims match measured scope.

Evidence: Runbook exercise, telemetry review, ownership record, and recovery trace.

### V-32

**Assessment honesty.** Source: [TSE-032](SPECIFICATION-v0.1.md#tse-032).

Setup and action: Inspect a proposed assessment with one missing applicable requirement, an unexecuted scenario, and a claimed non-applicable capability.

Expected observation: Missing evidence is not a pass. Non-applicability is justified; full conformance is withheld when an applicable mandatory obligation is unmet.

Evidence: Reviewed assessment with revision, scope, reviewer, date, results, and limitations.

## First pilot coverage

The first local publication milestone should prioritize exact proposal binding, authorization, stable operation identity, crash windows, ambiguous lookup, evidence binding, and receipt truth. Review applicable privacy and interface requirements alongside those paths.

Partial coverage is reported as partial coverage. The remaining scenarios stay unassessed until implemented and exercised. Tests in the design repository can inform this work but do not automatically establish engineering-draft coverage.

## Documentation validation is separate

The [documentation checker](DOCUMENTATION-CHECKS.md) verifies links, identifiers, and traceability structure. It does not invoke a host or provider and does not execute these procedures.
