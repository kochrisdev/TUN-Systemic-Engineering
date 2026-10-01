# TUN Systemic Engineering — Status and Roadmap

Updated: 1 October 2026.

[Documentation index](README.md) · [Scope](SCOPE.md) · [Validation plan](VALIDATION-PLAN-v0.1.md)

## Current status

The project has draft documentation, a documentation checker, and an [experimental publication and recovery pilot](PILOT.md). Specialized schemas and focused local tests exist; general-purpose implementation and full assessment remain future work.

| Area | Current state | Evidence or next artifact |
|---|---|---|
| Concept and principles | Written | [Concept note](CONCEPT-NOTE-v0.1.md), [Manifesto](MANIFESTO-v0.1.md) |
| Behavioral requirements | Draft-specified | [Specification](SPECIFICATION-v0.1.md) |
| Logical components and architecture | Draft-specified | [Components](COMPONENTS-v0.1.md), [Architecture](ARCHITECTURE.md) |
| Records and state | Proposed | [Contracts](CONTRACTS-v0.1.md), [Lifecycles](LIFECYCLES-v0.1.md) |
| Design component integration | Two pinned React components integrated locally; broader mapping remains proposed | [Design integration](DESIGN-INTEGRATION-v0.1.md) |
| Threats and assessment | Full procedures unassessed; limited pilot tests exist | [Threat model](THREAT-MODEL.md), [Conformance matrix](CONFORMANCE-MATRIX.md) |
| Documentation checker | Implemented | [Check description](DOCUMENTATION-CHECKS.md), [source](../scripts/check_docs.py) |
| Runtime schemas and types | Experimental v0.2 publication/recovery profile implemented | [Schema and fixtures](../schemas/README.md); general schemas and migration remain open |
| Authority and execution kernel | Narrow local host implemented | [Pilot](PILOT.md); fixture identity only, no production kernel |
| Provider and verification adapters | Local SQLite publication, correction, withdrawal, and readback implemented | [Pilot](PILOT.md); no remote provider; two-component React view exists |
| Runtime conformance runner | Complete runner not implemented | [Focused tests](../tests/test_pilot.py), not full procedure coverage |
| Distribution and hosted engineering site | Not supplied | Separate future decisions |

## Design baseline

See the [pilot validation record](PILOT-VALIDATION-2026-10-01.md) for the exact tested engineering source revision, commands, results, and limits.

The [design integration guide](DESIGN-INTEGRATION-v0.1.md) records the exact companion source revision inspected. The design project has an existing local host pilot; the engineering project can build on its lessons without claiming it already satisfies this draft.

## Milestone 1 — Review the draft contract

Resolve record envelopes, material binding, operation/attempt identity, supported claim scopes, and applicability. Review the requirements against at least two concrete workflows, including the local publication example.

Exit: the specification, contract model, lifecycle guidance, and scenario map agree on those decisions. The initial draft provides a starting point; expert review is still needed.

## Milestone 2 — Publish schema fixtures

Progress: the experimental publication/recovery profile and valid/invalid tests are implemented. The v0.1 fixture schema is retained for historical decoding, not automatic store migration. General schemas, migration, and portable binding decisions remain open.

Implement runtime schemas for the pilot's canonical records and request boundaries. Include invalid cross-record references, unsupported versions, material mutation, and migration cases.

Exit: fixtures can be validated repeatably, with semantic checks documented separately from structural validation. Schema validation is not runtime conformance.

## Milestone 3 — Implement the publication pilot

Progress: the local host, durable journal, provider, readback, and structured receipt are implemented and exercised by focused tests. A local interface now integrates the pinned ApprovalGate and ActionReceipt. This supplies the bounded pilot artifacts, not a production release or full accessibility assessment.

Build one host, durable journal, local provider, verification path, and presentation adapter. Use fixture identity and content.

Exit: a version-bound approval can produce one verified local publication; stale approval is blocked; a lost response survives restart and is reconciled without another publication. Unavailable readback remains unknown. Record source revisions and test evidence.

## Milestone 4 — Add supervision and recovery

Progress: separately approved correction and withdrawal now check action-specific authority and the exact provider resource revision. Both preserve the original history. Cancellation and budget controls remain unimplemented; this milestone is not complete.

Implement cancellation before dispatch, budget controls, reconciliation, and separately authorized withdrawal or correction. Expand to partial effects only when the provider model supports them.

Exit: control acknowledgements and actual outcomes remain distinct, recovery preserves the original action history, and applicable fault scenarios have recorded results.

## Milestone 5 — Validate a second provider

Choose a controlled provider with documented idempotency, lookup, and cancellation semantics. Record its differences from the local provider.

Exit: shared contracts handle those differences explicitly, the adapter passes its applicable scenarios, and unsupported guarantees are documented.

## Milestone 6 — Prepare distribution

Decide package boundaries from actual reuse, publish supported contracts and compatibility guidance, and document operations for the target deployment scope. A website can be built from the documentation after its content and release status are settled.

Exit: the distributed artifacts and stated compatibility are supported by named tests and ownership.

## Reporting progress

Update this page when an artifact actually exists or a named check has run. Preserve historical evidence with its original revision and environment. New implementation does not retroactively turn planned scenarios into passed tests.
