# Local Publication Pilot

Status: experimental local reference code, not a production service or full conformance implementation.

[Documentation index](README.md) · [Contracts](CONTRACTS-v0.1.md) · [Schemas](../schemas/README.md) · [Validation plan](VALIDATION-PLAN-v0.1.md)

## What is implemented

The pilot uses Python and two separate SQLite files. The host stores canonical proposals, fixture human decisions, authorization evaluations, grants, reservations, attempts, verification assessments, and receipt projections. The provider stores publications with a unique scope/operation key.

The demonstration simulates approval, commits a publication, deliberately loses the response, reopens both stores, and verifies the original publication. Exactly one publication remains for that tested operation. There is no model invocation, network server, real identity service, or external publishing account.

## Run it

Use a dedicated environment with Python 3.11 or newer. The recorded local test environment uses Python 3.13.4; other versions and operating systems have not been validated here.

From the repository root:

~~~sh
python -m venv .venv
~~~

On Windows:

~~~powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-pilot.txt
.\.venv\Scripts\python.exe -B -m reference.tse_pilot.demo
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
~~~

On macOS/Linux, use .venv/bin/python in place of the Windows executable path. Installing dependencies requires package-index access; running the pilot and tests afterward requires no network or API keys.

By default, the demo creates and cleans up isolated temporary databases. To retain synthetic records for inspection, add --directory followed by a new directory path. An existing directory is rejected; the demo does not reset or reuse existing databases. Store only fixture data.

The demonstration prints a pending receipt before readback, a completed receipt afterward, and providerPublicationCount equal to 1. Its approval is a fixture event, not an actual authenticated user interaction.

## Implementation map

| File | Responsibility |
|---|---|
| [Record schemas](../schemas/pilot-v0.1.schema.json) | Eight specialized action records plus provider evidence |
| [Contract validation](../reference/tse_pilot/contracts.py) | Strict JSON, schema checks, calendar validation, fingerprints, cross-record bindings |
| [Local runtime](../reference/tse_pilot/runtime.py) | Host journal, fixture policy, durable dispatch, provider, readback, receipts |
| [Demonstration](../reference/tse_pilot/demo.py) | Lost-response and reopen walkthrough |
| [Tests](../tests/test_pilot.py) | Positive, negative, concurrency, corruption, and crash fixtures |
| [Dependencies](../requirements-pilot.txt) | Pinned versions used for the recorded local environment |

## Actual boundaries and choices

- Principal is trusted fixture context. Constructing that object does not authenticate anyone. Only the named actor in the same scope can read or operate on their records.
- set_permission is test administration, not a secured management endpoint. There is no authentication transport or policy-service outage model.
- Publication is classified C3 conservatively to exercise approval. The real effect is confined to a local fixture database, not an external communication.
- One terminal approval or rejection is allowed per proposal revision. Repeating the same submission identity returns the original decision. Withdrawal and decision replacement are not implemented.
- Material revision is allowed before reservation. This pilot rejects revision after any reservation; it does not silently move a grant to changed content.
- Host transactions serialize reservation and dispatch ownership. The committed transition from reserved to attempted is the dispatch/revocation boundary. A permission change after that point cannot cancel the in-flight provider call.
- At most one host invocation is allowed per operation. Repeated dispatch calls return the stored receipt. Unknown work is never automatically reissued, even when an empty local lookup might suggest no effect.
- Exact same-target, same-content replacements are blocked while an earlier operation is unresolved. This is not a general detector of semantically equivalent work.
- The provider atomically commits publication content and its unique operation key. Keys persist for the database's lifetime. There is no expiry, retention cleanup, external notification, or guarantee across database loss/rollback.
- Readback compares security scope, operation, target, content, and proposal binding. An acknowledgement alone cannot produce a completed receipt.
- Every assessment and projection is a new stored revision. An unavailable later lookup retains the fact that an earlier verification observed an effect, without claiming that the current state is verified.
- Attempt activity records the last observed step, not a worker-liveness guarantee. A crashed attempt can remain marked dispatching while readback resolves its effect.
- The journal is application-append-only, not tamper-proof. Fixtures deliberately corrupt rows to test selected validation failures; coordinated database compromise is outside the trust model.

## Tested behavior

The local suite exercises schema families, invalid fixtures, semantic binding, stale approval, rejection, duplicate decisions, permission denial/revocation, expiry, operation identity, competing workers, readback mismatch, cross-scope access, receipt consistency, and selected persistence/crash failures.

The child-process test terminates through an uncaught injected fault after provider commit, then reopens the durable records from the parent. This is an application/process interruption test, not power-loss, disk-corruption, or multi-host resilience testing.

Tests are narrower than the full [planned procedures](VALIDATION-PLAN-v0.1.md). The [conformance matrix](CONFORMANCE-MATRIX.md) therefore does not mark complete requirements as passed.

## Known gaps

No React adapter, accessible review UI, supervision controls, cancellation, withdrawal, compensation, delegation, multi-step orchestration, provider-key expiry, automatic retry, production authentication, operational monitoring, retention/deletion service, or schema migration is implemented.

The schema namespace is experimental. Unknown schema versions are rejected; old databases are not migrated automatically. The pilot is not a distributable SDK or a hosted website.

A verified receipt means only that the bound publication was observed in the local provider store at the recorded time. It does not establish delivery, content truth, or product value.

## Next increment

Add a separately approved withdrawal/correction with preconditions and a presentation adapter against the pinned design baseline. Keep its tests and claims separate from this publication/readback slice.
