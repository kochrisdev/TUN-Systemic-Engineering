# Local Publication and Recovery Pilot

Status: experimental local reference code, not a production service or full conformance implementation.

[Documentation index](README.md) · [Review walkthrough](REVIEW-AND-RECOVERY-PILOT.md) · [Contracts](CONTRACTS-v0.1.md) · [Schemas](../schemas/README.md)

## What is implemented

Python and two separate SQLite files provide canonical proposals, fixture human decisions, authorization evaluations, grants, reservations, attempts, verification assessments, and receipt projections. The provider stores an immutable operation-outcome journal and a separately versioned current-resource table.

The v0.2 pilot supports publication, correction, and withdrawal. Each recovery action is a new proposal and operation with fresh approval, action-specific permission, and an exact resource-revision precondition. A local React interface renders the actual pinned TUN ApprovalGate and ActionReceipt components.

There is no model invocation, real identity service, or external publishing account. Everything is synthetic and local.

## Run the command-line experiment

Use a dedicated environment with Python 3.11 or newer. The recorded environment uses Python 3.13.4 on Windows; other versions and operating systems are not validated here.

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

On macOS/Linux, use .venv/bin/python in place of the Windows executable path. Installing dependencies requires package-index access; running the experiment afterward requires no API keys or external provider.

The command-line demo simulates approval, commits one publication, loses the response, reopens both stores, and reconciles the original operation. It prints pending then completed receipts and providerPublicationCount equal to 1. That diagnostic counts provider journal rows; it is not a general active-resource count after recovery.

By default, the demo creates and cleans up temporary databases. To retain fixtures, add --directory followed by a new directory path. The command-line demo rejects existing directories; it never resets them. For the interactive version, follow the [review and recovery guide](REVIEW-AND-RECOVERY-PILOT.md).

## Implementation map

| File | Responsibility |
|---|---|
| [Current schema](../schemas/pilot-v0.2.schema.json) | Eight specialized action-record families plus provider evidence |
| [Contract validation](../reference/tse_pilot/contracts.py) | Strict JSON, schema checks, dates, fingerprints, cross-record bindings |
| [Local runtime](../reference/tse_pilot/runtime.py) | Host journal, fixture policy, durable dispatch, provider preconditions, readback |
| [Presentation adapter](../reference/tse_pilot/presentation.py) | Access-filtered proposal and receipt views |
| [Local server](../reference/tse_pilot/server.py) | Loopback HTTP boundary and built UI assets |
| [React interface](../ui/src/App.tsx) | Explicit review, decision, execution, readback, and recovery controls |
| [Publication tests](../tests/test_pilot.py) | Contract, authority, concurrency, corruption, and crash fixtures |
| [Recovery tests](../tests/test_recovery.py) | Fresh decisions, action-specific permission, stale revisions, retained history |
| [HTTP tests](../tests/test_review_server.py) | Command boundaries and host-to-design projections |
| [Component tests](../ui/src/components.test.tsx) | Rendering and review/receipt semantics against pinned design code |

## Actual boundaries and choices

- Principal is trusted fixture context, not authentication. Only the named actor in the same scope can read or operate on their host records.
- Permission administration is a test helper, not an exposed management endpoint. Publish, correct, and withdraw rights are separate.
- C3 conservatively exercises consequential-action review; effects are confined to the local database.
- One terminal approval or rejection is allowed per proposal revision. Repeated submission identity returns the original decision. Revoking or replacing a human decision is not implemented; withdrawing a published resource is a different action.
- Publication proposals can be revised before reservation. Recovery uses a new proposal. Existing grants never silently transfer to changed material.
- The committed reserved-to-attempted transition is the dispatch/revocation boundary. Later permission changes cannot cancel the in-flight provider call.
- At most one host invocation is allowed per operation. Unknown work is never automatically reissued.
- Exact same-target/content publications and recovery operations for the same original resource cannot replace unresolved work. This is not semantic similarity detection.
- The provider atomically stores the resource change or precondition rejection with its unique scope/operation key. Keys persist for the database lifetime, with no expiry or protection against database loss/rollback.
- Readback compares scope, operation, target, content, binding, action, original resource, precondition, and resulting revision. An acknowledgement alone cannot produce completed status.
- Receipts describe historical operation outcomes, not current resource state. Later correction or withdrawal does not falsify the original publication receipt.
- Each assessment and projection is a new record revision. Attempt activity is a last observation, not a worker-liveness guarantee.
- The journal is application-append-only, not tamper-proof. Coordinated database compromise is outside this fixture trust model.

## Evidence and limits

The [original publication validation](PILOT-VALIDATION-2026-10-01.md) preserves the earlier source revision and its 36-test result. It does not establish the later recovery or UI behavior.

Current tests remain narrower than the [planned procedures](VALIDATION-PLAN-v0.1.md); complete [conformance requirements](CONFORMANCE-MATRIX.md) remain unassessed. The child-process interruption test is not power-loss, disk-corruption, or multi-host resilience testing.

No general supervision controls, cancellation, budgets, delegation, partial effects, automatic retry, production identity, operational monitoring, retention/deletion service, or schema migration is implemented. UI smoke tests are not a full accessibility audit.

A verified claim establishes only the bound local provider outcome at the recorded observation time. It does not establish delivery, factual truth, product value, or present resource state.

## Version boundary

New records use tse-pilot/0.2. The validator can decode the retained v0.1 fixtures, but the runtime rejects nonempty v0.1 host/provider stores. Use new synthetic stores; do not overwrite old evidence. No automatic migration or upgrade compatibility is promised.
