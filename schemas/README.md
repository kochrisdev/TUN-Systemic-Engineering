# Experimental Pilot Schemas

[Documentation index](../docs/README.md) · [Pilot guide](../docs/PILOT.md) · [Contract model](../docs/CONTRACTS-v0.1.md)

## Scope

[pilot-v0.3.schema.json](pilot-v0.3.schema.json) is the current JSON Schema 2020-12 bundle for local publication, recovery, and bounded supervision. It specializes eight core action-record families and adds ProviderEffect, DispatchBudget, and CancellationRecord. It is not a general SDK contract or the design library's React types.

Every record carries kind, schemaVersion, id, version, scope, and createdAt. New runtime records use tse-pilot/0.3. Schema version and record revision are separate. Unknown fields, record kinds, unsupported schema versions, and wrong field types are rejected.

The retained [v0.1 schema](pilot-v0.1.schema.json) and [v0.2 schema](pilot-v0.2.schema.json) support historical record decoding. They do not enable the v0.3 runtime to reopen old nonempty databases.

Identifiers are bounded to 128 characters and content to 4,096 characters. UTC timestamps require seconds with optional millisecond precision. The Python boundary additionally limits encoded records to 65,536 bytes and checks calendar validity. Duplicate JSON keys and non-JSON numeric constants are rejected.

Validation uses [Draft202012Validator](https://python-jsonschema.readthedocs.io/en/stable/validate/) and JSON Schema's [closed object rules](https://json-schema.org/understanding-json-schema/reference/object#additionalproperties). Cross-record equality, identity, authority, and outcome verification are host responsibilities.

## Additions in v0.3

- DispatchBudget is a versioned per-principal/scope record: total limit, consumed dispatch slots, and last charged operation (null for administrative changes).
- ExecutionAttempt carries budgetRef, null before dispatch or when dispatch was denied. A charged attempt references the exact budget revision written in the same transaction.
- CancellationRecord binds principal, proposal, operation ID and requested revision, observed operation revision/state, and effective/too-late/stale outcome. It is not a general run-control protocol.
- OperationRecord adds cancelled. ActionRecord adds queued/cancelled; these are host facts with no effectful provider invocation, not completed or reversed provider receipts.
- Invalid or unsupported versions still fail closed. See [local supervision semantics](../docs/LOCAL-SUPERVISION-PILOT.md) for limits that schemas alone cannot enforce.

## Retained recovery semantics from v0.2

| Record | Added semantics |
|---|---|
| ActionProposal | actionType, recoveryFor, expectedResourceVersion; publication has null recovery fields; recovery binds an original publication and positive revision |
| AuthorizationDecision / ExecutionGrant | actionType binds permission to publish, correct, or withdraw |
| ProviderEffect | Bound action and precondition, applied/rejected result, resulting revision or null for rejection |
| VerificationRecord | Applied/rejected outcome when verified; claim scoped to provider operation history |
| OperationRecord / ActionRecord | Failed state for a verified provider precondition rejection |

Semantic validation additionally rejects inconsistent proposal recovery fields. A recovery precondition is checked atomically by the provider, not inferred from schema validity. The runtime compares action-specific grants and readback fields against the canonical proposal.

ProviderEffect also serves as the internal fixture request envelope; its provisional result fields are not evidence. The provider computes the result and resulting revision before journaling the outcome. Only correlated readback of that journal supports a receipt.

## Material binding

The pilot hashes the complete proposal excluding its binding field, including identity, revision, scope, actor, target, content, expiry, action, original resource, expected resource revision, and disclosures.

Encoding is Python sorted-key JSON with no insignificant whitespace and ASCII-escaped strings, then SHA-256 with a sha256: prefix. There is no Unicode normalization. The v0.2 profile adds an integer resource revision; this is still a pilot-specific encoding, not RFC 8785/JCS or a portable production canonicalization standard.

A binding detects changes relative to trusted records. It neither authenticates the principal nor protects against coordinated database-administrator changes.

## Fixtures and tests

[cases.json](fixtures/cases.json) retains v0.1 examples for structural, version, date, duplicate-key, and material-binding cases. [Publication tests](../tests/test_pilot.py) load those exact files and generate every current record family through the runtime. [Recovery tests](../tests/test_recovery.py) exercise v0.2 cross-record and resource-precondition behavior.

A structurally valid changed-content fixture fails fingerprint validation. The historical valid fixture has a fixed validity interval: shape validation can succeed even when a new host action would be expired.

## Store compatibility

The validator recognizes tse-pilot/0.1, tse-pilot/0.2, and tse-pilot/0.3; all other namespaces are rejected. Current host and provider startup explicitly refuse nonempty v0.1/v0.2 stores. No conversion is performed. Preserve old stores and use new fixture directories.

The [local interface guide](../docs/REVIEW-AND-RECOVERY-PILOT.md) documents its separate presentation-view version and bounded command shapes. Future migration needs explicit interpretation of existing records, tests, and source-revision evidence before real data is used.
