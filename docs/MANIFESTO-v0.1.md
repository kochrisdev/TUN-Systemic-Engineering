# TUN Systemic Engineering

## Manifesto v0.1

### Engineering Intelligence for the Real World

Software used to wait.

It waited for a click.

It waited for a command.

It waited for a person to decide each next step.

Now software can interpret intent, assemble context, propose actions, use tools, coordinate agents, and change the world beyond its interface.

This changes the work of engineering.

We are no longer building only applications that respond.

We are building systems that may act.

An intelligent system is not trustworthy because its model is powerful, its response is fluent, or its interface appears confident. It becomes trustworthy when its authority is bounded, its effects are visible, its claims are supported, its failures remain honest, and its recovery paths work.

This requires a new engineering discipline.

We call it:

# TUN Systemic Engineering

## 01 — Begin With Intent, Not Execution

Every consequential action should begin with a human purpose.

Not a tool call.

Not a generated command.

Not an agent decision.

Intent.

The system must understand what outcome is wanted, for whom, within which boundaries, and under which conditions.

Intent guides the system.

It does not authorize every possible way of achieving the outcome.

```text
Human Intent → Bounded Proposal → Authorized Action → Verified Outcome
```

## 02 — Engineer the Whole Effect

An AI action does not end at the model boundary.

It moves through:

- people;
- models;
- agents;
- context;
- memory;
- policy;
- applications;
- tools;
- networks;
- providers;
- data stores;
- organizations;
- and the world beyond the product.

A locally successful call may produce a failed outcome.

A local timeout may hide a completed effect.

A reversible database change may still send an irreversible notification.

Systemic engineering follows the complete effect, including its downstream consequences.

Engineer outcomes, not merely invocations.

## 03 — Contracts Before Prompts

Prompts are powerful instruments for interpreting, generating, and reasoning.

They are not authorization protocols.

They are not durable records.

They are not transaction boundaries.

They are not proof.

Consequential operations require explicit, typed, validated, and versioned contracts. Models may help construct those contracts, but models do not replace them.

Natural language can express intent.

Engineering must bind it to exact system meaning.

## 04 — Capability Is Not Authority

A model may be able to generate a command.

An agent may be able to call a tool.

A tool may be able to modify a system.

None of these facts establish permission.

Authority belongs to the host system. It is grounded in authenticated identity, legitimate permissions, declared scope, current policy, consequence, time, and revocation state.

Authority must not be inferred from:

- model instructions;
- retrieved content;
- agent memory;
- tool availability;
- interface state;
- previous approval;
- or apparent urgency.

Power must always meet permission at the moment of action.

## 05 — Bind Decisions to Reality

Approval must refer to something exact.

The person should approve the proposal that the system will execute—not an earlier draft, a similar summary, or a silently changed version.

Material changes require a new decision.

Changed content.

Changed target.

Changed amount.

Changed authority.

Changed context.

Changed consequence.

Changed recovery conditions.

A decision without a stable proposal is only an impression of control.

## 06 — Acknowledgement Is Not Outcome

A request can be accepted without being completed.

A callback can resolve without the intended effect occurring.

A provider can report success without proving the final result.

An agent can say “done” without knowing what happened.

TUN separates:

```text
Requested
  ↓
Authorized
  ↓
Attempted
  ↓
Acknowledged
  ↓
Observed
  ↓
Verified
```

These stages may occur at different times and in different systems. They must not be collapsed for convenience.

Success is a claim that requires evidence.

## 07 — Evidence Before Confidence

The language of certainty must follow the strength of evidence.

Plans explain intended work.

Logs describe recorded events.

Provider responses report what a provider returned.

Readback observes current state.

Verification connects evidence to a claimed outcome.

None should pretend to be another.

When evidence is partial, stale, conflicting, inaccessible, or absent, the system should say so.

Trust should emerge from inspectable relationships between claims and evidence—not from tone, animation, or confident wording.

## 08 — Unknown Is an Honest State

Distributed systems do not always return clean answers.

Networks fail after sending.

Workers stop after writing.

Providers complete actions after clients time out.

Acknowledgements disappear.

In these moments, the outcome may be unknown.

Unknown does not mean failed.

Unknown does not mean safe to repeat.

Unknown means the system must reconcile what actually happened before taking another action that could duplicate or compound the effect.

Honest uncertainty is safer than invented certainty.

## 09 — Preserve Partial Effects

Actions are not always atomic.

A workflow may update one record and fail on the next.

A message may reach one recipient but not another.

A cancellation may stop future work but not reverse completed work.

A compensation may reduce harm without restoring the original state.

Partial effects must remain visible in system records, user-facing receipts, recovery decisions, and audits.

We do not rewrite a complicated reality into a convenient binary.

What happened must survive the failure state.

## 10 — Make Repetition Safe

Retries are part of real systems.

Duplicate effects do not have to be.

Every consequential execution should have a stable identity and an appropriate idempotency strategy. Repeated delivery must not silently become repeated consequence.

But idempotency is not a magic word.

It must be enforced at the boundary that owns the effect, retained for an appropriate period, scoped to the correct operation, and paired with reconciliation when the result is uncertain.

A retry policy without an effect model is merely repetition with optimism.

## 11 — Design Recovery Before Failure

Recovery is not an error-screen feature.

It is part of the action design.

Before execution, the system should know whether an operation can be:

- interrupted;
- cancelled;
- reconciled;
- retried;
- restored;
- corrected;
- compensated;
- escalated;
- or only acknowledged and disclosed.

These words are not interchangeable.

Undo means restoring the relevant prior state.

Compensation means applying another effect in response.

Retry means attempting again.

Reconciliation means discovering what happened.

Good recovery begins before anything goes wrong.

## 12 — Keep Agents Within Boundaries

Agents are participants in the system.

They may interpret, plan, delegate, use tools, observe, and adapt.

They are not the source of their own authority.

Every agent should operate with understandable:

- identity;
- purpose;
- capability;
- authority;
- context;
- duration;
- resource limits;
- intervention paths;
- and accountability.

Delegation must not silently increase authority. A sub-agent receives no more authority than the delegating actor can legitimately assign.

The more autonomous the operation, the stronger its boundaries, observation, exception handling, and recovery must become.

## 13 — Build Intervention Into the Runtime

A visible stop button is not enough.

Intervention is a system capability.

Pause requested is not paused.

Cancel requested is not cancelled.

Permission revoked is not proof that in-flight effects stopped.

Takeover is not restoration of earlier state.

Long-running and autonomous work needs real control paths, acknowledged state transitions, bounded response time, and evidence of the resulting condition.

Human authority must reach the runtime, not end at the interface.

## 14 — Observe Without Exposing

AI systems need meaningful observability.

Teams should be able to understand:

- what was proposed;
- what was authorized;
- what was attempted;
- which tools were used;
- which effects were observed;
- what was verified;
- what remains unknown;
- and what recovery occurred.

But observability is not permission to disclose everything.

Context, prompts, evidence, logs, traces, receipts, and memory can contain sensitive information. They must remain subject to access control, redaction, tenant isolation, retention limits, and legitimate purpose.

We make systems inspectable without making private data public.

## 15 — Compose Systems Without Losing Meaning

Models will change.

Tools will change.

Providers will change.

Frameworks will change.

The human control contract must not silently change with them.

TUN engineering contracts should travel across components while preserving identity, authority, proposal version, effect semantics, evidence, and recovery obligations.

Composability is not merely the ability to connect services.

It is the ability to connect them without losing meaning.

## 16 — Test the Uncomfortable Paths

The happy path proves very little about an action system.

We test:

- stale decisions;
- changed proposals;
- expired authority;
- duplicate delivery;
- partial completion;
- lost acknowledgement;
- delayed provider effects;
- conflicting evidence;
- revoked permission;
- agent handoff;
- cancellation races;
- unavailable verification;
- failed compensation;
- and recovery after restart.

Conformance comes from demonstrated behavior under pressure, not from adopting vocabulary or drawing an architecture diagram.

If a safety property matters, it should be testable.

## The TUN Engineering Model

For consequential AI actions:

```text
INTENT
  ↓
CONTEXT
  ↓
PLAN
  ↓
PROPOSAL
  ↓
DECISION
  ↓
AUTHORIZATION
  ↓
EXECUTION
  ↓
OBSERVATION
  ↓
VERIFICATION
  ↓
RECEIPT
  ↓
RECOVERY OR LEARNING
```

This is a relationship between records and responsibilities, not one universal runtime state machine.

The system may simplify what people see.

It must not erase distinctions needed for authority, accountability, or truth.

## Three Planes of Responsibility

### CONTROL

Who may authorize what, under which policy, scope, identity, time, and conditions?

### EXECUTION

What bounded work was attempted, through which tool, with which safeguards and known effects?

### EVIDENCE

What can the system support about the outcome, what remains unknown, and what can safely happen next?

These responsibilities may run together.

They must remain conceptually distinct.

## The TUN Engineering Principles

We engineer AI action systems to be:

### INTENT-BOUND

Connect execution to a legitimate, scoped human purpose.

### AUTHORIZED

Enforce permission outside the model and at the time of action.

### VERSIONED

Bind decisions to exact proposals and material parameters.

### IDEMPOTENT

Prevent repeated delivery from becoming repeated consequence.

### OBSERVABLE

Preserve meaningful activity and effect records.

### VERIFIABLE

Support outcome claims with appropriate evidence.

### HONEST

Represent partial, failed, contradicted, pending, and unknown states truthfully.

### RECOVERABLE

Design intervention, reconciliation, correction, and compensation before failure.

### COMPOSABLE

Preserve system meaning across models, agents, tools, and providers.

### ACCOUNTABLE

Keep consequential actions attributable to responsible actors and owners.

## From Model Output to System Outcome

The history of AI product engineering is moving through a progression:

```text
Model Response
      ↓
Structured Output
      ↓
Tool Calling
      ↓
Agent Workflow
      ↓
Autonomous Operation
      ↓
Systemic Action Engineering
```

At each stage, the software gains more capacity to affect the world.

Engineering discipline must grow with that capacity.

Better generation is not enough.

Better orchestration is not enough.

The defining question becomes:

> Can the system connect human intent to real-world effects without losing authority, evidence, or accountability along the way?

## A Protocol for Trustworthy Action

TUN Systemic Engineering should not exist only as guidance that engineers read.

It should become machine-readable and testable.

An application should be able to validate a TUN proposal.

A policy service should be able to evaluate a TUN authorization request.

A worker should be able to accept a bounded TUN execution grant.

A verifier should be able to attach evidence to a TUN action record.

A user interface should be able to render that record through TUN Systemic Design.

A conformance suite should be able to test the complete relationship.

The framework therefore becomes both:

**a discipline for engineering intelligent action**

and

**a protocol connecting human authority to machine effects.**

## What We Refuse to Collapse

We will not collapse:

- intent into permission;
- capability into authority;
- planning into approval;
- approval into authorization;
- authorization into execution;
- invocation into effect;
- acknowledgement into completion;
- observation into verification;
- confidence into evidence;
- timeout into failure;
- retry into recovery;
- compensation into undo;
- activity logs into accountability;
- autonomy into the absence of human control.

These distinctions are not bureaucracy.

They are where dependable AI products begin.

## The TUN Engineering Promise

We will not engineer AI merely to act.

We will engineer it to act within legitimate authority.

We will not report success merely because a tool returned successfully.

We will connect outcome claims to evidence.

We will not erase uncertainty to make systems appear reliable.

We will represent what is known, what is partial, and what remains unknown.

We will not treat failure as an exceptional screen at the edge of the product.

We will design interruption, reconciliation, and recovery into the action lifecycle.

We will not use autonomy to remove accountability.

We will create clearer relationships between people, intelligence, software, and real-world effects.

# TUN Systemic Engineering

## HUMAN INTENT

## BOUNDED AUTHORITY

## VERIFIED OUTCOMES

Engineer intelligence for the real world.

### Founding Proposition

The defining engineering challenge of the AI era is no longer only how software processes commands.

It is how intelligent systems translate human intent into real-world effects while preserving authority, truth, and accountability.

TUN Systemic Engineering exists to engineer that relationship.
