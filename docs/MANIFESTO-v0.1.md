# TUN Systemic Engineering

## Manifesto v0.1

### Engineering Intelligence for the Real World

Status: draft principles

Revision: 1 October 2026

[Project overview](../README.md) · [Documentation library](README.md) · [Concept note](CONCEPT-NOTE-v0.1.md)

AI products can interpret a person's request, choose tools, prepare changes, and carry out work across services. Each connection gives engineering a responsibility: preserve the person's intent, enforce the limits of authority, and establish what happened.

Software has automated consequential work for decades. AI adds variable interpretation and planning to that work. We build on the disciplines of security, reliability, distributed systems, and human-centered design to make this relationship dependable.

TUN Systemic Engineering is a proposed set of contracts and practices for that purpose. Its ambition is to make AI actions understandable through their records, controllable through their runtime, and accountable through their evidence.

These are commitments that guide the project. The [concept note](CONCEPT-NOTE-v0.1.md) describes the rationale and limits. The [draft specification](SPECIFICATION-v0.1.md) translates the commitments into proposed requirements. An [experimental local pilot](PILOT.md) exercises a narrow publication and recovery workflow with a review interface. A production runtime and full executable conformance suite remain future work.

## 01 — Begin With Human Purpose

We begin by understanding the desired outcome, the people affected, the constraints, and the conditions for stopping.

Natural language should make intent easier to express. The system carries that intent into precise proposals and bounded operations. Where uncertainty materially changes the action, it seeks clarification.

A person's goal establishes direction. Their legitimate permissions and applicable policy establish which actions can follow.

## 02 — Follow the Whole Effect

We examine what an action changes across the complete system: people, models, agents, tools, data, services, and downstream recipients.

Publishing a record may notify another person. Reading a source may expose sensitive information. Removing a message may leave copies elsewhere.

We define success and recovery at the level of the effect people care about. Local completion is one piece of that account.

## 03 — Make Contracts Explicit

We use clear records for intent, proposals, decisions, operations, attempts, and evidence.

Models may prepare those records. The host validates their meaning, relationships, and permitted transitions. Machine-readable structure makes obligations inspectable and helps engineers test them.

We keep the contract small enough to implement and precise enough to survive a change of model, tool, or provider.

## 04 — Bind Consent and Enforce Authority

When a person approves an action, their decision applies to an exact proposal: its target, content, material parameters, effects, and disclosed recovery limits.

Material changes require renewed review. The host checks whether the action is currently permitted, including after delays or changes in permissions.

Approval records a human decision. Authorization evaluates current permission. Both matter where approval is required.

Models, retrieved content, and agent memory cannot grant authority. Human authority itself remains bounded by legitimate access and the rights of others.

## 05 — Bound Autonomy and Support Intervention

We define delegated work through its goal, permitted actions, targets, duration, budgets, and exception behavior.

Delegation to another agent preserves or narrows those limits. Resource limits and stopping conditions remain part of the assignment.

People need controls that reach the running system. We distinguish a request to pause or stop from evidence that it took effect, and explain which in-flight actions can still complete.

As autonomy and consequence increase, the system needs stronger supervision and clearer accountability.

## 06 — Match Every Claim to Its Evidence

We state what verification establishes and when.

A provider can confirm that it accepted a message without confirming delivery. A readback can establish that the approved publication exists without establishing that every sentence is true.

Evidence identifies the relevant operation, target, revision, source, and observation time. Where possible, verification uses a method independent of the executor's success assertion.

A receipt communicates the supported result and its limits.

## 07 — Keep Unknown and Partial Outcomes Visible

We preserve uncertainty when the evidence cannot resolve it.

A network response may be lost after an action succeeds. A workflow may complete some effects before stopping. An ended worker may leave an unresolved external operation.

The system retains what is known, identifies what remains uncertain, and offers the next supported step. Later evidence updates the assessment without erasing earlier events.

An honest unknown is useful information for deciding what happens next.

## 08 — Make Retries Account for Effects

We give an intended operation a stable identity and distinguish it from the attempts used to carry it out.

Duplicate protection needs a documented scope, retention period, and enforcement boundary. A new attempt should not accidentally become a new consequence.

When an outcome is ambiguous, we reconcile it. Any further attempt requires current authority and safeguards that still apply. When a provider cannot support safe repetition, the system stops automatic retries and exposes the unresolved result.

## 09 — Plan Recovery With the Action

We describe recovery options before a consequential action proceeds.

Reconciliation establishes what happened. Retry attempts an operation again. Restoration returns relevant state to an earlier condition. Correction and compensation apply new effects.

Each option has limits. Restoration may conflict with later edits; withdrawal may leave copies with recipients. Recovery itself can fail and may require fresh approval.

The engineering obligation is to provide the recovery that is actually possible and disclose what cannot be recovered.

## 10 — Protect Data Throughout Its Journey

We apply access boundaries to context, memory, tool calls, evidence, logs, and receipts.

Useful observability records enough to explain actions while limiting unnecessary copies of sensitive content. People receive the evidence they are authorized to inspect.

Remembering a preference, retaining workflow state, keeping an audit record, and training a model are separate uses of information. We make their purposes and controls explicit.

When deletion or loss of source material prevents later verification, we preserve that limitation in the account.

## 11 — Preserve Meaning Across Integrations

We expect models, frameworks, tools, and providers to change.

Integrations should preserve proposal identity, approved meaning, authorization scope, operation identity, and the relationship between claims and evidence.

Each adapter declares what its provider can guarantee and where those guarantees end. Compatibility requires checking behavior as well as matching types.

A simpler architecture is valuable when it preserves these obligations. Separate responsibilities do not automatically require separate services.

## 12 — Evaluate the Product and Its Failures

We test delayed work, stale approval, duplicate delivery, lost responses, partial effects, cancellation races, contradictory evidence, and restart recovery.

We also evaluate whether the AI product is useful and its outputs are appropriate. Correct execution alone cannot establish answer quality or product value.

Incidents and observed failures should inform regression scenarios and reviewed improvements. Adaptation follows the same authority and data controls as other changes.

Claims of conformance should name a version, scope, evidence, and limitations. Tests support specific claims; they do not certify universal safety.

## One Contract Between Design and Engineering

[TUN Systemic Design](https://github.com/kochrisdev/TUN-Systemic-Design) describes how people understand and control AI behavior, including the responsibilities of the application behind it.

TUN Systemic Engineering develops the proposed records and enforcement paths that support that experience.

Together, they should let a person inspect an action and understand what was proposed, who permitted it, what was attempted, what changed, what evidence supports that account, and what can happen next.

## Our Commitment

We will make authority explicit and enforce it where actions occur.

We will report outcomes in proportion to their evidence.

We will preserve uncertainty, partial effects, and the history needed to understand them.

We will build intervention and recovery into the operation.

We will keep people and organizations accountable for the systems they deploy.

We will develop these commitments through small implementations, observable results, and clearly stated limits.

**Human intent. Bounded authority. Verified outcomes.**

TUN Systemic Engineering exists to connect human intent to system effects while preserving control, evidence, and accountability.
