# TUN Systemic Engineering — Threat Model

Status: initial design review model. The [local pilot](PILOT.md) has limited executable checks; this is not a completed security assessment or a claim that every mitigation has been tested.

[Documentation index](README.md) · [Architecture](ARCHITECTURE.md) · [Specification](SPECIFICATION-v0.1.md) · [Validation plan](VALIDATION-PLAN-v0.1.md)

## Scope and assumptions

The first workflow proposed for assessment is a person approving publication through an application host, worker, provider adapter, journal, verifier, and presentation adapter. The threat model includes malicious inputs as well as crashes, stale state, and misleading interpretation.

Protected assets include identity and permissions, exact reviewed content, operation identity, provider credentials, private context, evidence, and action history. People outside the initiating user can be affected by disclosure or publication.

The model assumes the host's trust base can enforce its declared controls. Compromised administrators, storage, or providers can undermine those assumptions; their residual risks and deployment protections need a separate operational assessment.

## Boundaries

Candidate model output and retrieved documents are untrusted data. Browser-supplied identity, permissions, status, and executable parameters cannot become authoritative by reaching an API. Workers need authenticated commands. Provider observations need correlation and appropriate provenance. Every viewer has an access boundary.

The [architecture](ARCHITECTURE.md#trust-boundaries) assigns owners to these boundaries.

## Initial register

| ID | Failure or attack | Required design response | Planned check |
|---|---|---|---|
| TM-01 | Client changes tenant, actor, or target references | Derive trusted scope and check object access on every path | [V-03](VALIDATION-PLAN-v0.1.md#v-03) |
| TM-02 | Retrieved text instructs an agent to grant itself permission | Treat source text as data; authority stays in the host | [V-08](VALIDATION-PLAN-v0.1.md#v-08) |
| TM-03 | Content changes after human review | Immutable material revision; reject stale approval | [V-04](VALIDATION-PLAN-v0.1.md#v-04), [V-05](VALIDATION-PLAN-v0.1.md#v-05) |
| TM-04 | Broad delegation substitutes for a high-consequence decision | Particular C4 approval and attenuated delegation | [V-07](VALIDATION-PLAN-v0.1.md#v-07), [V-09](VALIDATION-PLAN-v0.1.md#v-09) |
| TM-05 | Forged, expired, or replayed grant reaches the executor | Authentic bounded grant; operation and actor binding | [V-10](VALIDATION-PLAN-v0.1.md#v-10) |
| TM-06 | Permission or resource state changes between review and effect | Dispatch checks, provider preconditions, stated race boundary | [V-11](VALIDATION-PLAN-v0.1.md#v-11) |
| TM-07 | Concurrent workers or SDK retries create duplicate effects | Stable operation identity, atomic reservation, provider safeguards | [V-12](VALIDATION-PLAN-v0.1.md#v-12), [V-13](VALIDATION-PLAN-v0.1.md#v-13) |
| TM-08 | Host crashes after provider commit | Persist reservation; reconcile before unsafe replay | [V-14](VALIDATION-PLAN-v0.1.md#v-14), [V-15](VALIDATION-PLAN-v0.1.md#v-15) |
| TM-09 | Wrong-target evidence or forged callback claims success | Validate producer, operation, target, revision, and claim scope | [V-17](VALIDATION-PLAN-v0.1.md#v-17), [V-18](VALIDATION-PLAN-v0.1.md#v-18) |
| TM-10 | UI rounds partial or unknown work into success | Preserve state dimensions and truthful projections | [V-16](VALIDATION-PLAN-v0.1.md#v-16), [V-19](VALIDATION-PLAN-v0.1.md#v-19) |
| TM-11 | Traces, source links, or error text leak private data | Filter before transmission; enforce access at retrieval | [V-20](VALIDATION-PLAN-v0.1.md#v-20) |
| TM-12 | Stored preference or operational memory extends authority | Separate context reuse from grants and retention | [V-21](VALIDATION-PLAN-v0.1.md#v-21) |
| TM-13 | Journal tampering or deletion hides partial effects | Declared integrity, access, correction, and retention controls | [V-22](VALIDATION-PLAN-v0.1.md#v-22) |
| TM-14 | Unbounded work consumes resources or ignores intervention | Enforced budgets and evidence-backed control results | [V-23](VALIDATION-PLAN-v0.1.md#v-23), [V-24](VALIDATION-PLAN-v0.1.md#v-24) |
| TM-15 | Recovery overwrites newer state or bypasses permission | Fresh authority and preconditions; separate linked effects | [V-25](VALIDATION-PLAN-v0.1.md#v-25), [V-26](VALIDATION-PLAN-v0.1.md#v-26) |
| TM-16 | Late events or clock skew rewrite the outcome | Correlation and causal ordering; traceable reassessment | [V-27](VALIDATION-PLAN-v0.1.md#v-27) |
| TM-17 | Adapter or model update silently changes behavior | Versioned compatibility and regression evaluation | [V-29](VALIDATION-PLAN-v0.1.md#v-29), [V-30](VALIDATION-PLAN-v0.1.md#v-30) |
| TM-18 | Documentation or a logo is represented as operational proof | Scoped evidence and explicit implementation status | [V-31](VALIDATION-PLAN-v0.1.md#v-31), [V-32](VALIDATION-PLAN-v0.1.md#v-32) |

The [conformance matrix](CONFORMANCE-MATRIX.md) connects each procedure to its source requirement. A row here describes work to assess; it does not establish a mitigation has passed.

## Residual risks to declare

A malicious or mistaken provider can produce convincing but false evidence. Independent sources may reduce that risk but are not always available. A local journal and a provider call have separate transaction boundaries. Some effects cannot be cancelled or restored. A person may approve a misleading or incorrect proposal even when the record binding works correctly.

Deployment owners also need protections for credential storage, transport, database access, backups, dependencies, and incident handling. Domain-specific safety and content quality remain separate assessments.

## Review procedure

For a new adapter, diagram its real boundaries, enumerate downstream effects, and document which existing threats change. Add concrete failure timing and observable assertions to the validation plan.

Record the implementation revision, responsible reviewer, evidence location, residual risk, and decision for each applicable threat. Revisit the model after a provider change, authority change, new data use, or incident.
