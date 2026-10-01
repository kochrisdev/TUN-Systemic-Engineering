# TUN Systemic Engineering — Authority and Execution v0.1

Status: proposed workflow; commands below name responsibilities, not implemented endpoints.

[Documentation index](README.md) · [Specification](SPECIFICATION-v0.1.md) · [Contracts](CONTRACTS-v0.1.md) · [Architecture](ARCHITECTURE.md)

## Establish the action before permission

The host receives intent and candidate parameters, resolves the target in the caller's security scope, and classifies the whole effect. It prepares a canonical proposal with material content, preconditions, expiry, and recovery disclosure.

Model-generated values remain untrusted until validated. A provider's ability to send, write, or transact does not establish the current actor's permission to do so.

The host also determines whether it needs particular approval or can use a bounded delegation. C3 generally uses explicit review or intentional delegation. C4 always requires recorded approval of the particular proposal under this draft.

## Review and decision

Present the exact material action in a usable form. A summary can aid reading, but it cannot replace or conceal recipients, affected resources, amounts, content, or irreversible consequences that matter to the decision.

The client submits references to the proposal and decision, not replacement execution parameters. The host authenticates the principal, reloads canonical records, checks validity, and durably records the human decision.

Use a decision-submission identity or equivalent deduplication to handle double clicks and lost acknowledgements. Retrying storage of the same decision does not create another operation. Rejection, withdrawal, and stopping a dispatched operation remain separate commands.

## Authorization and grant

Evaluate current identity, object permissions, policy, relevant resource conditions, required approval, and delegation limits. Record the evaluation even when it denies permission, subject to access and retention policy.

When allowed, issue or store an execution grant bound to the operation, proposal revision and fingerprint, executing actor, security scope, action, target, and validity limits. Resolve that grant from trusted state before dispatch.

If a required policy or identity check is unavailable, stop the affected dispatch with a recoverable explanation. Historical receipts can remain readable where access policy permits; an outage in write authorization need not fabricate missing history.

## Dispatch protocol

The following sequence describes one implementation pattern:

1. Resolve the canonical proposal and current grant from host state.
2. Reserve the operation and record dispatch intent durably using atomic concurrency control.
3. Recheck authority, expiry, resource preconditions, worker ownership, and budgets at the declared dispatch boundary.
4. If a check fails before any request is sent, record the denial and the scope of the no-dispatch fact.
5. Send canonical parameters and the stable operation/idempotency identity through the adapter.
6. Record the provider observation. Distinguish confirmed rejection before effect from ambiguous transport failure.
7. Verify or reconcile the claimed outcome, then update the action projection.

Implementations may combine local steps in a transaction. They need to document ordering and the gap before remote acceptance. Holding a local database lock does not make a remote provider transaction atomic with policy changes.

## Permission changes and resource races

An approval can remain historically valid while current authority is revoked. Queued work checks current permission before dispatch. The host defines the ordering between revocation and dispatch ownership so competing requests have a predictable result.

Resource preconditions need enforcement where the resource can change. Prefer provider-supported conditional writes when available. A host-side read followed by an unconditional remote write leaves a race; document it and avoid claims that the earlier read eliminated it.

A late permission revocation does not prove that a provider has cancelled already accepted work. Intervention records identify the point at which further work was prevented and any effects still in flight.

## Repeated and replacement work

A repeated request for one approved proposal resolves to the existing operation. It does not mint a new idempotency identity on every HTTP request or worker restart.

A changed payload returns to proposal review. Before allowing an equivalent replacement for an unresolved action, determine whether the first effect occurred. Creating a new proposal revision is not an escape from that uncertainty.

Deliberately repeating the same content as a separate action can be legitimate. The host records that distinct intent and approval where required; content equality alone cannot decide whether two operations are duplicates.

## Transport and credential boundaries

Choose transport protections appropriate to the application: authenticated service requests, session and origin controls, bounded request bodies, replay handling, and object-level access. No particular HTTP route or token format is mandated by this guide.

Tools should receive only the credential scope they need. Provider secrets stay out of model-visible context, UI payloads, diagnostic errors, and routine traces. A tool path that bypasses the authorization service invalidates the intended boundary even if the normal path is well controlled.

## Decisions that need durable explanations

| Situation | Record and communicate |
|---|---|
| Proposal expired or changed | Why the old reference cannot proceed and how to review a new revision |
| Permission revoked | Dispatch denial and whether earlier effects are still possible |
| Provider response lost | Unresolved original operation and available reconciliation |
| Duplicate key has changed parameters | Validation failure without an additional effect |
| Retry guarantee expired | Automatic retry blocked; evidence or escalation needed |
| Verification cannot run | Existing observations and the unsupported claim |

Explanations should help the authorized person decide without exposing credentials, private policy internals, or another tenant's data.

## Review evidence

Use [V-04 through V-15](VALIDATION-PLAN-v0.1.md#v-04) to exercise proposal binding, approval, authorization, races, duplicate protection, and ambiguity. Include provider-side effect records in the evidence; a successful host response alone cannot establish that the boundary worked.
