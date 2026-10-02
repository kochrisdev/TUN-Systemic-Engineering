# TUN Systemic Engineering — Documentation

[Repository home](../README.md) · [Introduction](INTRODUCTION.md) · [Getting started](GETTING-STARTED.md) · [Status and roadmap](STATUS-AND-ROADMAP.md) · [Scope](SCOPE.md)

## Reading paths

**New to TUN:** Introduction → Concept Note → Manifesto → Getting Started.

**Building an integration:** Specification → Components → Architecture → Contracts → Lifecycles → Authority and Execution → Integration Checklist.

**Connecting the interface:** Design Integration → Evidence and Memory → Supervision and Recovery.

**Reviewing reliability and security:** Threat Model → Validation Plan → Conformance Matrix → Integration Checklist.

The documents define an initial engineering draft. An experimental local pilot provides specialized schemas, a host/provider implementation, separately approved recovery, and a two-component React review interface. It is not a released SDK or complete conformance implementation.

## Foundation

| Document | Purpose |
|---|---|
| [Introduction](INTRODUCTION.md) | A concrete example and a plain-language explanation |
| [Concept Note v0.1](CONCEPT-NOTE-v0.1.md) | Purpose, scope, initial system model, and pilot direction |
| [Manifesto v0.1](MANIFESTO-v0.1.md) | Engineering commitments |
| [Glossary](GLOSSARY.md) | Shared meanings for approval, authorization, operation, effect, and evidence |
| [Existing approaches](EXISTING-APPROACHES.md) | How TUN relates to design guidance and established engineering practices |
| [Scope and non-claims](SCOPE.md) | What this draft applies to and what it does not establish |

## Engineering model

| Document | Purpose |
|---|---|
| [Specification v0.1](SPECIFICATION-v0.1.md) | Draft behavioral requirements with stable identifiers |
| [Components v0.1](COMPONENTS-v0.1.md) | Logical host responsibilities, inputs, outputs, and failure behavior |
| [Architecture](ARCHITECTURE.md) | Control, execution, and evidence boundaries |
| [Contracts v0.1](CONTRACTS-v0.1.md) | Proposed record fields and relationships |
| [Lifecycles v0.1](LIFECYCLES-v0.1.md) | Independent status dimensions and guarded transitions |
| [Authority and Execution v0.1](AUTHORITY-AND-EXECUTION-v0.1.md) | Review, permission checks, reservations, dispatch, and retries |
| [Evidence and Memory v0.1](EVIDENCE-AND-MEMORY-v0.1.md) | Claim scope, provenance, context use, access, and retention |
| [Supervision and Recovery v0.1](SUPERVISION-AND-RECOVERY-v0.1.md) | Intervention, reconciliation, restoration, and compensation |
| [Design Integration v0.1](DESIGN-INTEGRATION-v0.1.md) | Proposed mappings to all fourteen design components and known type gaps |

## Adoption and assessment

| Document | Purpose |
|---|---|
| [Getting started](GETTING-STARTED.md) | First reading and implementation decisions; actual documentation-check command |
| [Local pilot](PILOT.md) | Run the implementation, understand its tests, and inspect its limits |
| [Local supervision pilot](LOCAL-SUPERVISION-PILOT.md) | Queued cancellation, dispatch budgets, races, and operational limits |
| [Review and recovery pilot](REVIEW-AND-RECOVERY-PILOT.md) | Build the local interface and exercise publication, correction, and withdrawal |
| [Review/recovery validation — 1 October 2026](REVIEW-RECOVERY-VALIDATION-2026-10-01.md) | Revision-bound automated tests, browser observations, and limitations |
| [Pilot validation — 1 October 2026](PILOT-VALIDATION-2026-10-01.md) | Revision-bound executed results, captured output, and coverage limits |
| [Integration checklist](INTEGRATION-CHECKLIST.md) | Adoption worksheet with ownership and evidence fields |
| [Threat model](THREAT-MODEL.md) | Failure and attack scenarios across trust boundaries |
| [Validation plan v0.1](VALIDATION-PLAN-v0.1.md) | Planned procedures with setup, observations, and evidence |
| [Conformance matrix](CONFORMANCE-MATRIX.md) | Requirement-to-component-to-procedure mapping; runtime status is not assessed |
| [Status and roadmap](STATUS-AND-ROADMAP.md) | Available documents, missing implementation, and next milestones |
| [Documentation checks](DOCUMENTATION-CHECKS.md) | What the checker verifies and its limits |

For project changes, read [Contributing](../CONTRIBUTING.md) and the [Changelog](../CHANGELOG.md).

## Sources of truth

The specification owns requirement text. Contracts and lifecycle documents explain the proposed record model and behavior; components and architecture describe an implementation approach. The validation plan owns procedure descriptions, and the conformance matrix records traceability rather than copying requirements.

The concept note and manifesto establish direction. If a new behavioral decision differs from them, update the affected documents together. Preserve requirement IDs and record meaningful changes in the changelog.

Use status language consistently: draft-specified, implemented, validated, and published describe different facts. Every runtime result needs a source revision, environment, procedure, and evidence.

## Design baseline

The organization follows the [TUN Systemic Design site](https://design.tun.systems/). Technical mappings use the design repository's pinned source revision documented in [Design Integration](DESIGN-INTEGRATION-v0.1.md), rather than relying on landing-page implementation counts.
