# TUN Systemic Engineering

## Concept Note v0.1

**Status:** Initial concept for discussion  
**Date:** 1 October 2026  
**Companion project:** [TUN Systemic Design](https://github.com/kochrisdev/TUN-Systemic-Design)

## 1. Summary

TUN Systemic Engineering is a proposed open framework for building AI products whose actions are authorized, observable, verifiable, and recoverable.

TUN Systemic Design defines how people understand and control AI behavior through clear intent, visible context, explicit authority, and verifiable outcomes. TUN Systemic Engineering extends those ideas into the application and infrastructure layers. It defines the contracts, runtime boundaries, state transitions, evidence requirements, failure behavior, and conformance tests needed to connect a human decision to a real system effect.

Its focus is not how to make an agent appear intelligent. Its focus is how to make an AI-enabled product dependable when intelligence interacts with tools, data, permissions, services, and other people.

The project begins from a simple distinction:

> A plan is not a proposal. Approval is not authorization. A successful tool call is not a verified outcome.

TUN Systemic Engineering makes these distinctions explicit and testable.

## 2. The problem

AI product engineering often concentrates on models, prompts, tool calling, orchestration, and response quality. These are necessary, but they do not by themselves provide a trustworthy action system.

When an AI product changes external state, several different events are often collapsed into one apparent success:

- a model recommends an action;
- a person clicks an approval control;
- an application accepts the request;
- a tool or provider acknowledges a call;
- an effect occurs in an external system;
- the product claims that the intended outcome was completed.

These events are not equivalent. Treating them as equivalent creates predictable failure modes:

- stale approval is applied to changed content;
- a user interface is mistaken for an authorization boundary;
- retries produce duplicate effects;
- timeouts are interpreted as failures even though an action completed;
- partial effects disappear behind a generic error;
- agent delegation silently expands authority;
- successful API responses are presented as verified outcomes;
- cancellation requests are presented as confirmed cancellation;
- compensation is incorrectly described as undo;
- logs describe model activity but cannot establish what happened in the world.

Existing agent frameworks can help models call tools and coordinate work. TUN Systemic Engineering addresses the contract around that work: what was intended, what was authorized, what was attempted, what was observed, what was verified, and what can safely happen next.

## 3. Purpose

TUN Systemic Engineering aims to provide a shared engineering language and a small set of composable contracts for consequential AI actions.

It should help teams:

1. bind approval to an exact, inspectable proposal;
2. enforce identity, permissions, scope, expiry, and policy outside the model;
3. execute actions with durable idempotency and effect tracking;
4. distinguish acknowledgement, observation, and verification;
5. represent partial, failed, and unknown outcomes honestly;
6. reconcile uncertain external effects before retrying;
7. design interruption and recovery before failure occurs;
8. connect runtime evidence to the TUN Systemic Design interface patterns;
9. test system-level safety properties across models, tools, and frameworks.

## 4. Relationship to TUN Systemic Design

The two projects address different sides of one product contract.

| TUN Systemic Design | TUN Systemic Engineering |
|---|---|
| How people express intent | How intent becomes a typed system record |
| How proposals are presented | How proposals are versioned and fingerprinted |
| How approval is requested | How decisions are bound and authorized |
| How activity is communicated | How execution attempts and observations are recorded |
| How outcomes are shown | How outcomes are independently verified |
| How intervention is offered | How pause, stop, cancel, and revoke are implemented |
| How recovery is explained | How reconcile, retry, restore, and compensate operate |
| How evidence is displayed | How evidence provenance and access are enforced |

TUN Systemic Design remains the presentation and interaction contract. TUN Systemic Engineering supplies the host-side records and lifecycle that make those interfaces truthful.

Neither layer can substitute for the other. A reliable backend with an opaque interface does not provide meaningful human control. A clear interface without host enforcement does not provide reliable authority or outcomes.

## 5. Proposed system model

The core lifecycle is:

```text
Intent
  ↓
Context Snapshot
  ↓
Plan
  ↓
Versioned Proposal
  ↓
Authorization Decision
  ↓
Execution Attempt
  ↓
Observation
  ↓
Verification
  ↓
Action Record
  ↓
Recovery or Learning
```

These are related records, not one universal state enum. A proposal can be approved while its execution has not begun. An attempt can be complete while verification remains pending. A cancellation can be acknowledged while the underlying action continues. Keeping these lifecycles separate is a central architectural requirement.

### 5.1 Intent

An intent describes the desired outcome, scope, constraints, timing, and material assumptions. It is not executable authority.

### 5.2 Context snapshot

A context snapshot identifies the material information used to prepare a plan or proposal. It should be immutable, access-controlled, and attributable. Material context changes may invalidate an existing proposal.

### 5.3 Plan

A plan describes an approach, dependencies, checkpoints, and anticipated decisions. Reviewing a plan does not approve every action that could arise from it.

### 5.4 Proposal

A proposal is a canonical, versioned description of a particular action. It includes the actor, target, material parameters, expected effects, consequence classification, expiry, and recovery limits.

### 5.5 Authorization decision

An authorization decision binds an authenticated principal and current policy evaluation to one exact proposal version. A user-interface callback is a request to make this decision, not the enforcement boundary itself.

### 5.6 Execution attempt

An execution attempt records a bounded attempt to perform an authorized action. It has its own identity, idempotency key, timing, runtime status, and observed effects.

### 5.7 Observation

An observation reports what a system, provider, or worker claims or exposes. It may be useful without being authoritative. Progress and acknowledgement are observations, not proof of completion.

### 5.8 Verification

Verification compares the intended effect with authoritative or appropriately trusted evidence. Verification may confirm, contradict, leave pending, or be unavailable.

### 5.9 Action record

An action record is the durable basis for a user-facing receipt. It includes the known effects, verification status, remaining uncertainty, recovery limits, and available next actions.

### 5.10 Recovery and learning

Recovery may mean reconciliation, retry, restoration, compensation, correction, or escalation. These operations must remain distinct. Learning may adapt future behavior but must not silently expand authority.

## 6. Engineering principles

### 6.1 Contracts before prompts

Models may help construct plans and proposals, but consequential operations use typed, validated, and versioned records. Natural language does not replace identity, authorization, or input validation.

### 6.2 Authority belongs to the host

The host application owns authentication, tenant boundaries, permissions, policy, canonical revisions, approval validity, and revocation. Model output, memory, retrieved instructions, interface state, and tool descriptions cannot grant permission.

### 6.3 Material changes require new decisions

Approval is bound to the displayed proposal identity, version, and material fingerprint. Changed recipients, content, amounts, targets, permissions, context, or recovery conditions require a new proposal and decision.

### 6.4 Effects are journaled

Consequential attempts create durable records of what was authorized, attempted, observed, verified, and recovered. The journal preserves partial and unknown outcomes instead of rewriting history into a simplified success or failure.

### 6.5 Verification is independent of execution

Tool invocation and provider acknowledgement are not sufficient evidence for many actions. Where feasible, verification should use authoritative readback, provider records, or other independent evidence.

### 6.6 Unknown is a valid outcome

A lost response does not show that no effect occurred. The system must support an explicit unknown state and reconcile authoritative records before attempting an operation that could duplicate an effect.

### 6.7 Recovery is designed before execution

Actions should declare recovery characteristics before approval. The system should know whether it can cancel, restore, retry, compensate, correct, or only reconcile and disclose.

### 6.8 Delegation cannot increase authority

An agent, sub-agent, workflow, or tool receives no more authority than the delegating actor possesses and explicitly assigns. Authority remains bounded by purpose, target, duration, consequence, and policy.

### 6.9 Evidence follows access boundaries

Observability must not become unintended disclosure. Evidence, logs, context, and receipts remain subject to authentication, authorization, redaction, retention, and tenant isolation.

### 6.10 Framework independence

TUN should define portable contracts and invariants rather than require a particular model, agent framework, workflow engine, database, cloud, or policy system.

## 7. Reference architecture

TUN Systemic Engineering can be organized into three cooperating planes.

```text
                 TUN Systemic Design
          Review, approval, and supervision UI
                            │
                            ▼
┌──────────────────────────────────────────────────┐
│                 Control Plane                    │
│ Identity · Policy · Proposals · Decisions        │
│ Delegation · Expiry · Revocation                 │
└───────────────────────┬──────────────────────────┘
                        │ authorized command
                        ▼
┌──────────────────────────────────────────────────┐
│                Execution Plane                   │
│ Orchestration · Tool adapters · Idempotency      │
│ Effect journal · Cancellation · Resource limits  │
└───────────────────────┬──────────────────────────┘
                        │ observations
                        ▼
┌──────────────────────────────────────────────────┐
│                 Evidence Plane                   │
│ Readback · Verification · Reconciliation         │
│ Receipts · Audit · Recovery                      │
└──────────────────────────────────────────────────┘
```

### Control plane

The control plane determines whether a requested operation may proceed. It owns canonical proposals, authenticated decisions, policy evaluation, delegation boundaries, expiry, revocation, and execution grants.

### Execution plane

The execution plane performs bounded work. It validates grants, applies idempotency, invokes tools, emits structured observations, responds to interventions, and journals known effects.

### Evidence plane

The evidence plane determines what is actually known about the outcome. It performs readback, reconciliation, verification, receipt projection, audit retention, and recovery coordination.

Deployments may combine these planes physically. Their logical responsibilities and records should remain distinguishable.

## 8. Initial contract set

The first project release should specify a small interoperable set of records:

- `IntentContract`
- `ContextSnapshot`
- `PlanRecord`
- `ActionProposal`
- `AuthorizationDecision`
- `ExecutionGrant`
- `ExecutionAttempt`
- `ActivityObservation`
- `EffectRecord`
- `VerificationRecord`
- `InterventionRequest`
- `RecoveryOperation`
- `ActionRecord`

Each record should have:

- a stable identifier;
- a schema version;
- creation and observation times where applicable;
- actor and tenant references;
- explicit relationships to preceding records;
- material revision or fingerprint information;
- access and retention considerations;
- defined validation and state-transition rules.

JSON Schema can provide a language-neutral interchange form, with generated or hand-maintained types for initial reference implementations.

## 9. Conformance properties

TUN conformance should be demonstrated through evidence and executable tests rather than architecture diagrams alone.

Initial conformance scenarios should verify that:

- an expired proposal cannot execute;
- a modified proposal cannot inherit approval;
- approval references the exact proposal version and material fingerprint;
- the host rechecks authority before execution;
- delegated actors cannot exceed assigned authority;
- repeated delivery with the same idempotency key does not create duplicate effects;
- callback resolution does not create a verified receipt;
- a timeout may result in an unknown outcome;
- unknown outcomes require reconciliation before unsafe retry;
- partial effects remain visible;
- cancellation requested and cancellation confirmed remain separate;
- verification evidence matches the correct proposal, attempt, target, and revision;
- compensation is not described as restoration or undo;
- high-consequence operations require action-specific recorded approval;
- sensitive context is redacted before unauthorized transmission;
- an agent cannot treat retrieved content as an authority grant.

The project may define three adoption descriptions aligned with the design project:

### TUN-Inspired Engineering

Uses selected principles without claiming full implementation.

### TUN-Aligned Engineering

Implements a declared subset of TUN contracts and publishes the applicable conformance evidence and limitations.

### TUN-Conformant Engineering

Passes the applicable normative contract and lifecycle tests for a declared version and deployment scope.

## 10. First reference implementation

The recommended first pilot is a bounded publication workflow. It aligns with the existing TUN Systemic Design publication example and exercises the full lifecycle without requiring a universal agent platform.

The pilot should demonstrate:

1. an agent or person prepares a versioned publication proposal;
2. the interface displays the exact content, target, effects, and recovery limits;
3. an authenticated person approves that exact version;
4. the host validates identity, authority, scope, policy, expiry, and fingerprint;
5. an execution worker publishes using a durable idempotency key;
6. a separate verifier reads the published record back;
7. an action record supplies the TUN `ActionReceipt` with the known result;
8. a lost acknowledgement produces an unknown result and reconciliation rather than immediate republication;
9. correction, withdrawal, and compensation are represented as new operations rather than fictional undo.

The reference host may use TypeScript for contracts and application integration with a small SQLite-backed service for durable proposal, decision, attempt, effect, and verification records. These technology choices are illustrative, not normative.

## 11. Proposed repository shape

```text
docs/
  CONCEPT-NOTE.md
  SPECIFICATION-v0.1.md
  ARCHITECTURE.md
  THREAT-MODEL.md
  CONFORMANCE.md
  GLOSSARY.md

schemas/
  intent.schema.json
  context-snapshot.schema.json
  action-proposal.schema.json
  authorization-decision.schema.json
  execution-attempt.schema.json
  verification-record.schema.json
  action-record.schema.json

packages/
  contracts/
  policy/
  proposals/
  execution/
  journal/
  verification/
  recovery/
  telemetry/
  testing/
  react-adapter/

conformance/
  scenarios/
  fixtures/
  runner/

examples/
  publication-pilot/
```

The earliest implementation should stay small. The contracts and failure semantics should stabilize before adding broad orchestration, provider, or framework integrations.

## 12. Scope and non-goals

TUN Systemic Engineering is intended to define action-system contracts, lifecycle behavior, and adoption evidence.

It is not initially intended to be:

- a general-purpose agent framework;
- a model SDK or model router;
- a prompt library;
- a workflow engine;
- an identity provider;
- a complete policy engine;
- a database or event broker;
- proof that an AI system is safe in every domain;
- a replacement for application-specific security, privacy, legal, accessibility, or safety review;
- a claim that all actions can be reversed;
- a mechanism for exposing private chain-of-thought.

Reference implementations may integrate with these systems while keeping TUN contracts portable.

## 13. Key questions for development

The concept should be tested against several open questions:

1. Which proposal fields are always material, and which are action-specific?
2. How should proposal fingerprints bind large or private content without duplicating it?
3. What is the minimum useful execution grant?
4. Which observations qualify as verification for different action classes?
5. How should verification freshness and evidence authority be represented?
6. How should long-running workflows renew authority without silently extending delegation?
7. What guarantees can be portable across local, queued, and distributed execution?
8. How should interruption behave during non-atomic external operations?
9. How can conformance evidence remain useful without becoming a misleading safety certification?
10. Which records belong in product audit history, operational telemetry, or user-visible receipts?

These questions should be answered through narrow pilots and adversarial scenarios rather than abstract specification alone.

## 14. Development approach

### Phase 1 — Vocabulary and invariants

Align terminology with TUN Systemic Design, define record boundaries, document non-claims, and identify the first normative invariants.

### Phase 2 — Schemas and lifecycle tests

Publish the initial JSON Schemas and executable tests for proposal binding, authority, idempotency, unknown outcomes, verification, and recovery.

### Phase 3 — Reference kernel

Implement a small host-side kernel for validation, fingerprinting, decision binding, attempt lifecycle, effect journaling, verification, and receipt projection.

### Phase 4 — Publication pilot

Connect the kernel to the existing TUN React components and demonstrate real authorization, durable effects, independent readback, reconciliation, and recovery.

### Phase 5 — Failure laboratory

Provide inspectable scenarios for stale approval, duplicate delivery, lost acknowledgement, partial completion, permission revocation, cancellation races, provider outage, and conflicting evidence.

### Phase 6 — Integration guidance

Document integration with workflow systems, policy systems, tool protocols, telemetry, multi-tenant applications, and multiple agent frameworks without making any one of them mandatory.

## 15. Measures of success

The project is successful if adopters can answer, with inspectable records:

- What did the person intend?
- What exact action was proposed?
- Who authorized it, under which policy and scope?
- What did the system attempt?
- Which effects are known to have occurred?
- What evidence supports that conclusion?
- What remains partial, pending, contradicted, or unknown?
- What can safely happen next?
- Who remains accountable?

Technical success should also include:

- interoperable schemas that are useful without the reference runtime;
- conformance tests that catch meaningful integration failures;
- truthful integration with all fourteen TUN Systemic Design patterns;
- at least one complete reference workflow with durable state and verification;
- clear limits that prevent users from mistaking alignment for universal safety assurance.

## 16. Working proposition

> TUN Systemic Engineering provides contracts, runtime patterns, and conformance tests for building AI products whose actions are authorized, observable, verifiable, and recoverable.

Together, the two projects form a continuous product contract:

```text
TUN Systemic Design
How AI behavior is understood and controlled

                    +

TUN Systemic Engineering
How AI behavior is constrained, executed, and proven

                    =

Understandable, controllable, and accountable AI products
```

The immediate next step is not to build a broad agent platform. It is to validate the concept through one versioned proposal, one real authorization boundary, one durable external effect, one independent verification path, and one honest recovery workflow.
