# An Introduction to TUN Systemic Engineering

[Documentation index](README.md) · [Concept note](CONCEPT-NOTE-v0.1.md) · [Getting started](GETTING-STARTED.md)

## An AI action needs an account of what happened

Imagine asking an assistant to publish a project update. You review the text and approve it. The publication service saves the update, but the network response is lost.

The assistant now has a difficult choice. Publishing again could create a duplicate. Saying “failed” could hide the existing update. Saying “done” requires evidence.

TUN Systemic Engineering proposes a consistent way to handle that situation: preserve the approved action, enforce its authority, track its execution, reconcile uncertainty, and explain the supported result.

## The key distinctions

| Concept | What it means in the example |
|---|---|
| Intent | You want the project update published to a particular destination |
| Proposal | The exact text, destination, effects, and recovery limits prepared for review |
| Approval | Your decision about that proposal revision |
| Authorization | The application's check that the action is permitted now |
| Operation | This one intended publication |
| Attempt | One invocation of the publication provider |
| Verification | Evidence that the expected publication exists within the stated scope |
| Receipt | An understandable account of the outcome and remaining limits |

A model can help prepare the update and plan the work. The host application enforces permissions and owns the authoritative records.

## What makes the approach systemic

One action crosses several boundaries: person, interface, model, application, worker, provider, evidence, and back to the person. TUN follows those relationships so that meaning and authority survive each handoff.

The proposed architecture groups responsibilities into control, execution, and evidence. A small application can implement all three in one process. The grouping helps make responsibility clear; it does not demand a large platform.

## How it relates to TUN Systemic Design

TUN Systemic Design describes how people understand and control AI behavior. It includes interaction patterns for proposals, approval, activity, evidence, intervention, and receipts.

TUN Systemic Engineering develops the host contracts behind those experiences. An approval gate needs a service that checks the exact proposal. A receipt needs supported outcome records. A stop control needs a real runtime control path.

The design repository has existing UI code and a bounded local host example. This engineering repository now includes its own [experimental publication pilot](PILOT.md), specialized schemas, and focused tests alongside the draft documents. A local React review interface now uses the pinned ApprovalGate and ActionReceipt; it is not a production runtime or general-purpose adapter package.

## Where to begin

Choose one action with a clear target and a visible effect. Define what would count as success, how the result can be checked, and what happens if the response is lost.

Then read the [specification](SPECIFICATION-v0.1.md), identify the applicable requirements, and use the [integration checklist](INTEGRATION-CHECKLIST.md) to assign owners and evidence. The [validation plan](VALIDATION-PLAN-v0.1.md) turns common failures into concrete procedures.

This work complements evaluation of model output and product usefulness. A publication can be correctly authorized and verified while still containing a poor answer.
