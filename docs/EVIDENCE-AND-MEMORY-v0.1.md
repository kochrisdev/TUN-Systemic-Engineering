# TUN Systemic Engineering — Evidence and Memory v0.1

Status: draft engineering guidance. The [pilot](PILOT.md) implements narrow local readback; general evidence and memory services remain unimplemented.

[Documentation index](README.md) · [Specification](SPECIFICATION-v0.1.md) · [Contracts](CONTRACTS-v0.1.md) · [Design integration](DESIGN-INTEGRATION-v0.1.md)

## Evidence supports a particular claim

Start with the proposition being assessed. “The provider accepted request X,” “publication Y contains revision Z,” and “the recipient received the message” need different evidence.

An assessment records the claim, operation, relevant provider identities, target, content/resource version, method, source, observation time, result, and limitations. A result is meaningful within that scope and time.

| Evidence | What it may establish | What it does not establish alone |
|---|---|---|
| Host dispatch reservation | Intent to send an operation was durably recorded | Provider received or completed it |
| Authenticated acceptance response | Provider accepted the identified request | Final delivery or user benefit |
| Correlated readback | The expected state/effect exists for the bound operation | Truth of generated content or persistence forever |
| Provider delivery event | Delivery as defined by that provider | A human read or understood the message |
| Human inspection | The stated reviewer observed a specific condition | Universal correctness outside the reviewed scope |

Evidence quality depends on provenance and method, not merely its label or format. A provider event and provider readback can share failure modes. Independent verification means assessing evidence separately from the executor's success assertion; it does not necessarily mean another organization or process.

## Verification workflow

1. Identify the claim and expected effect from canonical records.
2. Obtain evidence through authorized access.
3. Validate producer authenticity and operation/resource bindings.
4. Evaluate freshness, consistency, relevance, and contradictions.
5. Record the result and its limits.
6. Update the authorized action projection with a traceable assessment revision.

An unavailable check remains unavailable. A pending check remains pending. A contradiction is retained for review. Do not select only confirming sources.

Provider lookup may reveal a matching state without proving that this operation caused it. Preserve that distinction when operation or effect identifiers are missing. Empty eventually consistent reads require a provider-specific finality interpretation.

## Context snapshots

A context snapshot is a versioned manifest of material sources and their role in preparation. It distinguishes:

- what the system could access;
- what it actually used;
- which source revision was used;
- whether the content was provided, retrieved, or inferred;
- whether a source is available, stale, missing, or restricted.

The host decides which changes affect a proposal's meaning. Material evidence changes can invalidate review; unrelated metadata updates need not.

A digest can bind content without duplicating it, but it neither authenticates truth nor conceals predictable sensitive content reliably. Protect manifests and digests according to their information content.

## Memory categories and separate retention

TUN Systemic Design's memory categories describe reuse, not legal or storage guarantees.

| Category | Engineering interpretation |
|---|---|
| M0 | No reuse as AI memory after the task; operational records may still remain |
| M1 | Context used within a session or workflow |
| M2 | Persistent user context with meaningful inspection and management |
| M3 | State retained to continue an authorized operation |

M3 persistence does not renew an expired grant. A stored preference does not approve a future C4 action. A user disabling personalization does not by itself remove audit records, backups, or training data.

Maintain a separate inventory for each data use: purpose, owner, source, access, retention, deletion behavior, backup exceptions, and any permitted training use. Training and evaluation reuse require their own applicable authority and controls.

## Deletion and historical evidence

Prefer references to protected content when full payload duplication is unnecessary. If source content is deleted, record its unavailability and the effect on future verification. Do not claim replay is reproducible when required data is gone.

Historical assessments can remain as records of what was established at a time, subject to retention policy. A current-state claim may need new evidence. Deletion does not automatically falsify the earlier observation, and retaining an old receipt does not prove the source still exists.

Append-only event history concerns how corrections are represented. It does not require indefinite retention or prevent policy-driven payload deletion.

## Access and presentation

Filter both content and sensitive metadata before model or client transmission. Titles, identifiers, counts, URLs, and snippets can themselves disclose private information.

Quote, paraphrase, and generated synthesis remain visibly distinct. Retrieval does not make generated interpretation a source quotation. Evidence links need permitted destinations and access enforcement at use time.

U0–U3 labels communicate scoped qualitative certainty with a basis. They are independent of execution activity and verification result and should not be treated as calibrated probabilities.

## Evaluation and operating signals

Useful signals include unresolved evidence age, verification delay, evidence-binding failures, contradictions, and access-denied reads. Aggregate without logging unnecessary private payloads.

The validation plan exercises evidence binding, claim scope, disclosure boundaries, memory use, and content deletion in [V-17 through V-22](VALIDATION-PLAN-v0.1.md#v-17). Successful syntax or schema validation cannot establish provenance or factual truth.
