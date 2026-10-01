# TUN Systemic Engineering — Specification v0.1

Status: draft behavioral specification; unimplemented in this repository.

Revision: 1 October 2026.

[Documentation index](README.md) · [Contracts](CONTRACTS-v0.1.md) · [Lifecycles](LIFECYCLES-v0.1.md) · [Assessment matrix](CONFORMANCE-MATRIX.md) · [Scope](SCOPE.md)

## Purpose and authority

This specification defines proposed host behavior for connecting human intent to authorized actions and supported outcome claims. It is the source of requirement text within this repository. Architecture, component, and workflow documents explain possible implementations without adding independent normative requirements.

The requirements are a draft for review and implementation. A published document does not establish a working runtime, provider guarantee, or successful assessment.

## Normative language

The terms MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY use the meanings described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174), only when capitalized. Mandatory requirements determine a scoped assessment; recommendations permit justified departures. This convention does not make TUN an IETF standard.

Stable requirement identifiers belong to the clauses below. Their applicability limits the obligation. The [assessment matrix](CONFORMANCE-MATRIX.md) maps every clause to a proposed procedure; none has runtime evidence in this repository yet.

## Applicability

The core action scope covers consequential operations selected for an adopting product, including local and shared writes, communications, and other external effects. Authentication, access control, source handling, and data protections also apply to protected reads and informational experiences.

Capability-specific clauses apply when the product uses delegation, persistent memory, autonomous work, recovery, or a human interface. Omission requires a scope-based explanation, not an assumption that the feature is safe. A C0 answer does not exempt its underlying data access or tools from applicable rules.

A minimal synchronous action may combine services and records internally. It still preserves the distinctions needed to satisfy the applicable clauses. No clause requires a separate microservice, model vendor, workflow framework, or cryptographic grant format.

## Alignment with TUN Systemic Design

This draft takes its design baseline from [TUN Systemic Design specification at commit 81b52e8](https://github.com/kochrisdev/TUN-Systemic-Design/blob/81b52e8d64c90891ef1340802502e398dc6c0340/docs/SPECIFICATION-v0.1.md). Engineering assessments and design assessments have separate scopes; satisfying one does not automatically satisfy the other.

| Dimension | Meaning used here |
|---|---|
| Autonomy 0–4 | Arrangement for delegated work; never permission by itself |
| C0–C4 | Consequence of the complete effect, from informational through high consequence |
| M0–M3 | Context reuse categories; independent of retention and sensitivity |
| U0–U3 | Scoped qualitative certainty; independent of execution and verification status |

C0 is informational, C1 local reversible, C2 shared reversible, C3 external consequential, and C4 high consequence. Classification includes downstream notifications and disclosures. The host owns classification and records its rationale; the model may only suggest it. Material reclassification invokes proposal and authority checks.

## Requirement catalog

## Scope and records

### TSE-001

**Declare scope and ownership.** Applies to: All assessments.

The adopting product MUST identify the assessed operations, responsible owner, actors, trust boundaries, consequence classes, and enabled capabilities. Scope MUST include downstream disclosures and effects; an informational answer MUST NOT be used to hide a consequential tool operation.

### TSE-002

**Validate records at trust boundaries.** Applies to: All external inputs and stored records used for decisions.

The host MUST validate record structure, supported schema versions, field limits, and cross-record references before relying on them. Unsupported or ambiguous material fields and malformed bindings MUST block the affected decision or dispatch. Static types alone MUST NOT be treated as runtime validation.

### TSE-003

**Enforce identity and isolation.** Applies to: All access to protected records and tools.

The host MUST establish the principal and security scope from trusted identity context and enforce access on reads, commands, evidence, and receipt projections. Caller-supplied actor or tenant fields MUST NOT override that context. A model or tool output MUST NOT grant permissions.

### TSE-004

**Preserve canonical proposals.** Applies to: Actions in the core action scope.

The host MUST store immutable proposal revisions containing the actor, action, target, material parameters, expected effects, consequence, preconditions, validity limits, and recovery limits. Material changes MUST create a new revision and invalidate approval for the changed action. Mutable content references MUST be resolved to bound versions or digests before review.

## Approval and authority

### TSE-005

**Record exact human decisions.** Applies to: When human approval is required or obtained.

The host MUST bind each approval or rejection to the authenticated decision maker, proposal identity, revision, and material fingerprint. Invalid, expired, superseded, or materially changed proposals MUST NOT be accepted for approval. A decision request acknowledgement MUST NOT be treated as proof of authorization, execution, or effect.

### TSE-006

**Require review or bounded delegation for C3.** Applies to: C3 operations.

C3 operations SHOULD require explicit proposal approval unless an authorized person has intentionally delegated that action class with defined targets, limits, duration, and exception handling. Any departure from this recommendation MUST be documented with its rationale and consequences; departure never bypasses authorization or applicable C4 approval.

### TSE-007

**Require particular approval for C4.** Applies to: C4 operations.

A C4 operation MUST have explicit, recorded human approval of the particular proposal before dispatch. Standing delegation, an autonomy level, prior preference, or approval of a plan MUST NOT substitute for that decision. The review MUST disclose material effects and recovery limits.

### TSE-008

**Authorize in the host.** Applies to: Every consequential dispatch.

The host MUST evaluate current permissions, policy, scope, applicable approval or delegation, and proposal validity before allowing an operation. The host MUST deny dispatch when required checks are unavailable or fail. Authority MUST NOT be inferred from UI state, retrieved instructions, model confidence, or memory.

## Delegation and dispatch

### TSE-009

**Constrain delegation.** Applies to: Delegated or multi-agent work.

Delegation MUST identify the goal, delegator, delegate, permitted operations and targets, duration or stopping condition, budgets where applicable, and exception behavior. Effective authority MUST be limited by the intersection of the delegation and current host policy. Further delegation MUST NOT increase those rights or extend their duration.

### TSE-010

**Bind execution grants.** Applies to: Every authorized operation.

The executor MUST resolve an authentic host grant bound to the operation, proposal revision and fingerprint, actor, security scope, permitted action and target, and validity limits. It MUST obtain executable parameters from canonical host records and MUST reject grants used outside their bounds. A grant MAY remain an internal record; this specification does not require bearer tokens.

### TSE-011

**Define dispatch and revocation boundaries.** Applies to: Queued, concurrent, or externally executed work.

The host MUST recheck relevant authority, expiry, and resource preconditions at its defined dispatch boundary. It MUST define how reservations, revocation, and worker ownership are ordered and record residual in-flight effects that cannot be stopped. A pre-dispatch check MUST NOT be represented as atomic with an arbitrary external provider effect.

### TSE-012

**Separate operations from attempts.** Applies to: Core action scope.

One intended logical action MUST have a stable operation identity distinct from its attempts. Permitted retries MUST retain the operation identity, material parameters, and applicable provider idempotency identity. A changed payload MUST NOT be submitted as a retry, and an unresolved operation MUST NOT be bypassed by creating an equivalent replacement operation.

## Reliability and state

### TSE-013

**Declare duplicate-protection guarantees.** Applies to: Adapters that can produce effects.

Each adapter MUST declare idempotency scope, key retention, parameter matching, concurrent-request behavior, and uncovered downstream effects. The host MUST use those guarantees to bound retries and MUST NOT claim that a local ledger alone provides exactly-once remote effects. Expired or absent duplicate protection MUST prevent automatic reissue unless another documented safeguard establishes safety.

### TSE-014

**Persist dispatch reservations and outcomes.** Applies to: All effectful dispatches in the assessed action scope.

Before sending an effectful request, the host MUST durably reserve the operation and record dispatch intent using concurrency control that prevents independent workers from treating it as fresh work. If that write fails, dispatch MUST NOT occur. If outcome persistence fails after dispatch, the operation MUST remain unresolved for reconciliation; restart MUST NOT erase or blindly redispatch it.

### TSE-015

**Reconcile ambiguous outcomes.** Applies to: Timeouts, lost responses, or uncertain provider effects.

The host MUST preserve known and unknown effects and reconcile the original operation through authorized evidence. Absence from a read MUST NOT establish no effect unless the provider's consistency and finality guarantees support that conclusion. Reissue MUST require current authority and a still-valid duplicate-effect safeguard; otherwise automatic reissue MUST remain blocked and an escalation path provided.

### TSE-016

**Keep state dimensions distinct.** Applies to: All lifecycle projections.

The host MUST distinguish proposal validity, human decision, authorization, attempt activity, effect knowledge, verification, and intervention status. A worker ending, request acknowledgement, progress counter, or transport error MUST NOT independently establish a successful, failed-with-no-effect, or reversed outcome.

## Evidence and receipts

### TSE-017

**Bind and assess verification evidence.** Applies to: Any verified outcome claim.

Verification MUST identify the claim, operation, relevant attempts or provider effect references, target, content or resource revision, evidence source, observation time, method, and limitations. Evidence MUST be access-controlled and assessed for authenticity, relevance, and freshness before supporting a claim. An unrelated or mismatched record MUST NOT verify the action.

### TSE-018

**Limit claims to the evidence.** Applies to: All user-visible outcome claims.

A verified claim MUST state its scope. Provider acceptance MUST NOT be described as delivery without delivery evidence, and observed state MUST NOT establish causal attribution without an adequate operation binding. Verification of execution MUST NOT be presented as verification of generated content quality or truth.

### TSE-019

**Project truthful receipts.** Applies to: Receipts and inspectable action records.

A receipt MUST derive from authorized host records and preserve material partial, pending, contradicted, and unknown outcomes. Confirmed completion or restoration MUST have appropriate verification. Evidence updates MUST create a traceable revised assessment, rather than silently replacing history or manufacturing success from a callback.

### TSE-020

**Protect evidence and source meaning.** Applies to: Context, evidence, logs, and presentation.

The host MUST filter unauthorized content and sensitive metadata before transmission, including in errors, previews, traces, and links. It MUST distinguish source quotations, paraphrases, and generated interpretations and preserve material contradictions. Readable evidence links MUST respect the same access boundaries as the record.

## Memory and supervision

### TSE-021

**Separate memory use from authority.** Applies to: Context reuse and persistent workflow state.

The host MUST distinguish available context from context actually used and distinguish session context, user memory, and operational state. Reused memory MUST NOT grant new authority or extend a delegation. Memory-use labels MUST NOT imply deletion from logs, backups, or training stores; each applicable use and retention policy MUST be described separately.

### TSE-022

**Preserve accountable history with bounded retention.** Applies to: Durable journals and referenced content.

The host MUST retain causal links, partial effects, and corrections for its declared retention scope and restrict journal access. It MUST describe integrity controls, content deletion, backup exceptions, and any resulting evidence unavailability. An append-only journal MUST NOT be claimed to be tamper-proof or to require indefinite retention of all payloads.

### TSE-023

**Bound autonomous work and resources.** Applies to: Delegated, autonomous, or potentially unbounded work.

The host MUST define enforceable time, retry, tool-call, and cost or resource limits appropriate to the operation, with a stopping and escalation policy. Budget exhaustion MUST stop further dispatch according to that policy while preserving in-flight and completed effects. Renewal MUST be an explicit authorized change.

### TSE-024

**Confirm intervention separately.** Applies to: Autonomous or long-running operations with human supervision.

The host MUST provide meaningful intervention within declared capabilities and bind each control request to the intended run and control revision. Request acknowledgement MUST remain distinct from the observed intervention outcome. Confirmation MUST identify what stopped, paused, transferred, or was revoked and disclose remaining in-flight effects.

## Recovery and integration

### TSE-025

**Authorize recovery.** Applies to: Any recovery operation.

Recovery reads MUST have applicable access authority, and recovery writes MUST undergo applicable proposal, approval, authorization, and execution checks. Recovery MUST link to the original operation without deleting its history. A recovery control MUST NOT act as a permission bypass or conceal an unresolved original effect.

### TSE-026

**Describe recovery accurately.** Applies to: Recovery offers and results.

The host MUST distinguish reconciliation, retry, restoration, correction, compensation, and escalation. It MUST offer only supported actions, state their limits, and verify any claimed restoration. Compensation MUST NOT be labelled undo, and restoration MUST check relevant intervening changes before overwriting state.

### TSE-027

**Handle late and conflicting observations.** Applies to: Asynchronous evidence and state updates.

The host MUST correlate late observations with their original operation and preserve contradictory evidence for review. Wall-clock order alone MUST NOT determine causality across producers. Correcting an earlier assessment MUST remain auditable; a late acknowledgement MUST NOT erase confirmed cancellation limits or later effects.

### TSE-028

**Preserve meaningful human control in presentation.** Applies to: Interfaces for review, intervention, or receipts.

The host and interface MUST expose material action details, authority, uncertainty, and recovery limits in an understandable form. Approval, rejection, and supported intervention MUST be operable through accessible controls; critical meaning MUST NOT rely only on color. A presentation adapter MUST disclose unsupported state mappings rather than silently converting them to success.

## Compatibility and assessment

### TSE-029

**Version adapter and contract compatibility.** Applies to: Adapters, records, and UI integrations.

An integration MUST identify the record schema, adapter, policy, and relevant interface versions it supports. It MUST validate compatibility before relying on exchanged records and preserve approval and evidence bindings across migrations. Breaking changes MUST trigger review of affected requirements and scenarios.

### TSE-030

**Evaluate quality and behavioral changes.** Applies to: Products using AI generation or changing system behavior.

The adopting team MUST assess product and content quality separately from execution correctness. Changes to models, prompts, tools, policy, or adapters MUST receive relevant regression evaluation before promotion. Evaluation feedback or a learned preference MUST NOT silently expand authority or introduce unapproved data reuse.

### TSE-031

**Assign operational responsibility.** Applies to: Any deployed implementation.

A deployed implementation MUST identify an operational owner, monitor unresolved operations and verification lag, and define incident response, escalation, and restart recovery. Its telemetry MUST respect data boundaries, and its service claims MUST state the measured scope and known provider limits.

### TSE-032

**Support scoped assessment claims.** Applies to: Any claim of engineering conformance.

A conformance assessment MUST identify the specification revision and commit, implementation scope and revision, applicable requirements, evidence, reviewer, date, justified non-applicability, and documented recommendation departures. An unmet applicable MUST or MUST NOT requirement MUST prevent a full claim for that scope. Documentation validation alone MUST NOT be presented as runtime conformance or certification.

## Assessment boundary

The [validation plan](VALIDATION-PLAN-v0.1.md) defines candidate procedures and required evidence. Procedures can include automated tests, inspection of operational settings, provider documentation, and human interface review. A scenario label is not proof that a test exists.

The project currently supplies draft requirements and documentation checks. Runtime schemas, executors, adapters, and an executable conformance runner remain planned. For current capability status and the first delivery milestone, see [Status and roadmap](STATUS-AND-ROADMAP.md).
