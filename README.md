# TUN Systemic Engineering

Engineering AI actions with explicit authority, evidence, and recovery.

TUN Systemic Engineering is a proposed companion to [TUN Systemic Design](https://github.com/kochrisdev/TUN-Systemic-Design). It explores how an AI product can connect a person's intent to an action, enforce the authority to perform it, and report what actually happened.

**Current status: concept stage.** This repository contains a concept note and manifesto. There is no released specification, schema package, runtime, or conformance suite yet.

## Start here

| Document | What it covers |
|---|---|
| [Concept Note v0.1](docs/CONCEPT-NOTE-v0.1.md) | Scope, proposed records, architecture, engineering constraints, and the first pilot |
| [Manifesto v0.1](docs/MANIFESTO-v0.1.md) | The commitments that guide the project |

The concept note explains proposed behavior and open decisions. The manifesto states principles. Neither document establishes a compliance standard.

## The problem we address

A person approves a project update. The publication service creates it, but its response is lost. The agent sees a timeout.

Publishing again could create a duplicate. Reporting failure could hide an existing publication. Reporting success would require evidence.

TUN proposes a way to preserve the approved content, record the attempt, reconcile the provider's state, and show a receipt that distinguishes verified effects from unresolved ones.

## Proposed approach

- Bind human approval to an exact proposal version.
- Let the host enforce identity, permissions, policy, expiry, and delegation.
- Track one logical operation across execution attempts and possible partial effects.
- Support outcome claims with evidence for a stated scope and time.
- Treat unknown results, intervention, and recovery as part of normal operation.

Recovery depends on the action and provider. Some effects can be restored; others can only be corrected, compensated, or disclosed.

## Relationship to TUN Systemic Design

The design project defines how people understand and control AI behavior, including obligations for the host application. This project develops the proposed engineering contracts and tests for those obligations.

The intended integration is a host that supplies trustworthy records to TUN components such as `ApprovalGate` and `ActionReceipt`. Compatibility remains to be demonstrated by a working pilot.

## First milestone

Build a local publication pilot with versioned approval, authorization at dispatch, durable operation records, duplicate protection at the provider boundary, and verification through readback. Include a deliberate lost-response scenario and show that restarting the host does not cause another publication.

The [concept note](docs/CONCEPT-NOTE-v0.1.md#9-first-pilot-and-acceptance-criteria) defines the acceptance criteria. Model, retrieval, and product-quality evaluations remain separate responsibilities.

## Contributing

Feedback is welcome through [issues](https://github.com/kochrisdev/TUN-Systemic-Engineering/issues) or pull requests. Useful contributions include concrete failure scenarios, corrections to proposed semantics, and examples of provider guarantees or limitations. Include expected behavior and evidence where possible.

## License

[MIT](LICENSE).
