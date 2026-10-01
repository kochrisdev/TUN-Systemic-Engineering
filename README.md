# TUN Systemic Engineering

Engineering AI actions with explicit authority, evidence, and recovery.

TUN Systemic Engineering is a proposed companion to [TUN Systemic Design](https://github.com/kochrisdev/TUN-Systemic-Design). It explores how an AI product can connect a person's intent to an action, enforce the authority to perform it, and report what actually happened.

**Current status: draft specification with an experimental local pilot.** The library includes engineering requirements, architecture, and guides. A Python/SQLite publication pilot now supplies specialized JSON schemas and focused tests. There is no stable SDK, production runtime, full conformance result, or hosted engineering site.

## Start here

| Document | What it covers |
|---|---|
| [Documentation library](docs/README.md) | Reading paths and the complete engineering reference |
| [Getting started](docs/GETTING-STARTED.md) | Apply the draft to one bounded workflow |
| [Run the local pilot](docs/PILOT.md) | Executable schemas, publication, lost-response recovery, and focused tests |
| [Specification v0.1](docs/SPECIFICATION-v0.1.md) | 32 proposed engineering requirements and their applicability |
| [Components v0.1](docs/COMPONENTS-v0.1.md) | 12 logical components, ownership, inputs, outputs, and failure behavior |
| [Architecture](docs/ARCHITECTURE.md) | Trust boundaries, persistence, dispatch, evidence, and recovery |
| [Contracts v0.1](docs/CONTRACTS-v0.1.md) | General record semantics and the narrower experimental schema profile |
| [Concept Note v0.1](docs/CONCEPT-NOTE-v0.1.md) | Scope, proposed records, architecture, engineering constraints, and the first pilot |
| [Manifesto v0.1](docs/MANIFESTO-v0.1.md) | The commitments that guide the project |

The concept note explains the rationale; the manifesto states principles. The draft specification is the source of proposed requirements. The [conformance matrix](docs/CONFORMANCE-MATRIX.md) connects each requirement to a component and a planned procedure; complete requirements remain unassessed; focused pilot tests provide only partial evidence. See [status and roadmap](docs/STATUS-AND-ROADMAP.md) for what exists and what remains to be built.

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

The intended integration is a host that supplies trustworthy records to TUN components such as `ApprovalGate` and `ActionReceipt`. The [design integration guide](docs/DESIGN-INTEGRATION-v0.1.md) maps all 14 design patterns to engineering responsibilities against a pinned design baseline. Compatibility remains to be demonstrated by a working pilot.

## Current pilot and next increment

The [local pilot](docs/PILOT.md) implements fixture approval, current authorization checks, durable operation records, local provider duplicate protection, and verification through readback. Its demonstration loses a provider response and recovers the original publication after reopening the stores.

Next: separately approved correction/withdrawal and a tested design-component adapter. The current pilot has no real identity service, external provider, or interactive review UI.

The [concept note](docs/CONCEPT-NOTE-v0.1.md#9-first-pilot-and-acceptance-criteria) defines the acceptance criteria. Model, retrieval, and product-quality evaluations remain separate responsibilities.

## Contributing

Feedback is welcome through [issues](https://github.com/kochrisdev/TUN-Systemic-Engineering/issues) or pull requests. Useful contributions include concrete failure scenarios, corrections to proposed semantics, and examples of provider guarantees or limitations. Include expected behavior and evidence where possible.

Read the [contribution guide](CONTRIBUTING.md) and run the [documentation checks](docs/DOCUMENTATION-CHECKS.md) when editing the library.

## License

[MIT](LICENSE).
