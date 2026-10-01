# Experimental Pilot Schemas

[Documentation index](../docs/README.md) · [Pilot guide](../docs/PILOT.md) · [Contract model](../docs/CONTRACTS-v0.1.md)

## Scope

[pilot-v0.1.schema.json](pilot-v0.1.schema.json) is a JSON Schema 2020-12 bundle for the local publication experiment. It specializes the eight core action-record families and adds ProviderEffect as supporting readback evidence. It is not a general engineering SDK contract or the design library's React types.

Every record carries kind, schemaVersion, id, version, scope, and createdAt. The accepted schemaVersion is tse-pilot/0.1, separate from the record's version. Unknown fields, record kinds, schema versions, or wrong field types are rejected.

The schema bounds identifiers to 128 characters, content to 4,096 characters, and defines UTC timestamps with seconds and optional millisecond precision. The Python boundary additionally limits each encoded record to 65,536 bytes and checks actual calendar validity. Duplicate JSON keys and non-JSON numeric constants are rejected before validation.

The implementation uses the official library's [Draft202012Validator](https://python-jsonschema.readthedocs.io/en/stable/validate/). JSON Schema's [closed object rules](https://json-schema.org/understanding-json-schema/reference/object#additionalproperties) enforce the allowed fields. Cross-record equality, current authority, and outcome verification are additional host checks, not schema guarantees.

## Material binding

The pilot hashes the complete proposal excluding its binding field. This includes identity, revision, scope, actor, target, content, expiry, and disclosed effect/recovery fields.

The encoding is Python sorted-key JSON, no insignificant whitespace, ASCII-escaped strings, then SHA-256 with a sha256: prefix. There is no Unicode normalization. The proposal's schema permits no numeric material fields.

This is a named pilot-specific encoding, not RFC 8785/JCS and not a portable production canonicalization standard. A binding detects changes relative to trusted records; it does not authenticate the principal or protect against coordinated changes by a database administrator.

## Fixtures

[cases.json](fixtures/cases.json) lists one valid proposal and invalid structural, version, date, duplicate-key, and material-binding cases. The [pilot tests](../tests/test_pilot.py) load those exact files. They also generate every record family through the runtime and validate the stored results.

A structurally valid changed-content fixture fails semantic fingerprint validation. This demonstrates why a successful schema check alone is insufficient.

The valid fixture is historical synthetic content with a fixed validity interval. Record validation accepts its shape and binding; the host would reject a new action after its expiry.

## Versioning

Only this experimental namespace is supported. Unsupported stored versions block the affected operation. No migration or upgrade compatibility is claimed.

Keep a source commit with any exported record examples. Future changes require new fixtures, reviewed interpretation of existing records, and explicit migration decisions before real data is used.
