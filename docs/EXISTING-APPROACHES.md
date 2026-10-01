# TUN Systemic Engineering and Existing Approaches

Status: positioning and engineering background for the draft.

[Documentation index](README.md) · [Concept note](CONCEPT-NOTE-v0.1.md) · [Architecture](ARCHITECTURE.md)

## The proposed contribution

TUN connects human review and control to host enforcement and evidence of effects. Many of its mechanisms are established engineering practices. The project organizes them around a consistent product contract and a traceable assessment.

| Existing discipline or tool | Role in an adopting product | What the TUN draft connects to it |
|---|---|---|
| Product and interaction design | Explain actions and support human decisions | Exact proposal binding and truthful outcome projection |
| Identity and policy systems | Authenticate principals and evaluate permission | Current authorization, delegated scope, and bounded execution grants |
| Workflow engines and queues | Schedule work and coordinate retries | Stable operation identity, effect semantics, and unresolved outcomes |
| Provider APIs | Perform or observe external effects | Declared duplicate protection, readback, cancellation, and recovery limits |
| Event journals and observability | Record activity and diagnose operations | Causal records and claims supported by evidence |
| AI evaluation | Assess output quality and behavioral changes | Separate quality evidence from execution correctness |
| Reliability practice | Operate services and recover from failure | Ownership, unresolved-operation response, and tested restart behavior |

These are architectural relationships, not compatibility claims with any named vendor.

## TUN Systemic Design

The [design specification](https://github.com/kochrisdev/TUN-Systemic-Design/blob/81b52e8d64c90891ef1340802502e398dc6c0340/docs/SPECIFICATION-v0.1.md) already includes requirements for authority, uncertainty, outcomes, and recovery. The engineering project develops proposed records and host responsibilities for implementing those requirements.

The design repository also has a [local host example](https://github.com/kochrisdev/TUN-Systemic-Design/blob/81b52e8d64c90891ef1340802502e398dc6c0340/examples/host-integration/README.md). That example provides a concrete point of comparison, not evidence that this draft's entire contract is implemented. The [integration guide](DESIGN-INTEGRATION-v0.1.md) records the actual source baseline and known presentation gaps.

## Idempotency and operation identity

[AWS's idempotent API guidance](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) explains how caller request identity expresses repeat intent and why changed parameters need special handling. TUN uses the same practical distinction between one logical operation and multiple attempts.

[Stripe documents](https://docs.stripe.com/api/idempotent_requests) parameter comparison and retention behavior for its own idempotency keys. This illustrates why an adapter needs an explicit provider contract. The TUN draft does not generalize one provider's retention or retry guarantees to all integrations.

## Canonical data and fingerprints

[RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) describes deterministic JSON canonicalization suitable for reproducible data representations. It is a candidate foundation for material bindings, not a selected or implemented TUN serialization format.

Canonicalization needs an action-specific field set and versioned references. Authentication, storage integrity, policy enforcement, and content truth remain separate concerns.

## Requirement language

[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) provide the requirement vocabulary used by the engineering specification. Adopting that vocabulary makes obligations easier to interpret; it does not make this project an industry standard.

## Design-site structure translated to engineering

| Design documentation area | Engineering counterpart |
|---|---|
| Principles and concept | Manifesto and concept note |
| Specification | Host behavioral requirements |
| UI components | Logical engineering components and their boundaries |
| Visual tokens | Record vocabulary, material bindings, and lifecycle semantics |
| React API | Proposed host contracts and a separate presentation adapter |
| Review workflow | Approval, authorization, and dispatch protocol |
| Evidence and memory | Verification provenance, context use, access, and retention |
| Supervision and recovery | Runtime controls and linked recovery operations |
| Validation records | Planned scenarios, then revision-bound execution evidence |
| Showcase | Future local publication pilot and its observable failure journeys |

The correspondence preserves the design site's reading experience while giving engineering its own technical substance. A future runtime or documentation website should derive its claims from the same status and evidence records.
