# Local Review and Recovery Pilot

Status: experimental v0.2, synthetic data only. Not a hosted website, production service, or general SDK.

[Documentation index](README.md) · [Pilot internals](PILOT.md) · [Design integration](DESIGN-INTEGRATION-v0.1.md) · [Schema profile](../schemas/README.md)

## What this demonstrates

A person's review decision, the host's permission check, a provider operation, and evidence of its outcome are four different things. This pilot makes those boundaries visible with two actual TUN design components:

- ApprovalGate displays the exact proposal and records approve/reject. It does not execute.
- ActionReceipt displays the host's evidence-backed historical outcome. It does not infer success from a click or acknowledgement.

The provider board is a separate view of current local resource state. A completed publication receipt remains historical evidence after that resource is corrected or withdrawn.

## Start the interface

First install the [Python pilot dependencies](PILOT.md#run-the-command-line-experiment). For the UI, use Node 22.12 or newer with npm. The recorded environment uses Node 22.23.2 and npm 10.9.8; no cross-version support claim is made.

From the repository root:

~~~sh
cd ui
npm ci
npm test
npm run build
cd ..
~~~

The checked-in lockfile fixes the dependency graph. Initial lockfile generation used a locally invoked npm 11.6.4 after npm 10 encountered a dependency-resolution error; subsequent npm 10.9.8 ci succeeds. No global package-manager update is needed.

Start the host on Windows:

~~~powershell
.\.venv\Scripts\python.exe -B -m reference.tse_pilot.server
~~~

On macOS/Linux use .venv/bin/python. Open [the local review interface](http://127.0.0.1:8765). Use that exact address: localhost and other Host values are intentionally rejected. Close the host with Ctrl+C.

Default stores are temporary. Optional --directory followed by a path retains or reopens v0.2 synthetic stores. Unlike the command-line demo, the server can reopen a compatible directory; it does not reset existing permissions or migrate v0.1 records. Use a new directory for a fresh experiment and preserve old evidence.

The build can report ignored upstream use-client directives and associated sourcemap diagnostics. These components are rendered entirely in this client-only build; no server-component behavior is claimed.

## Walkthrough

1. Prepare a publication. Inspect the content, target, actor, consequence, expiry, and recovery limit. No operation exists yet.
2. Approve it. The gate shows that execution is not confirmed. A separate execute button appears.
3. Leave the lost-response checkbox enabled and execute. The provider commits the publication, but the receipt remains pending verification.
4. Reconcile that operation. Readback verifies the original journal entry without another publication.
5. In the provider board, edit the proposed correction and prepare it for review. Check the exact publication ID, active-resource revision, and replacement content.
6. Approve and execute the correction separately, then reconcile it. The board advances to revision 2; the original publication receipt remains completed as a historical statement.
7. Prepare withdrawal. Review the exact publication ID, revision 2, and content being withdrawn. Approve, execute, and reconcile this new operation.
8. The board shows withdrawn at revision 3. Historical publication, correction, and withdrawal receipts remain. Nothing says the original event was undone or erased.

With lost-response simulation disabled, dispatch still requires readback before reporting completed. The checkbox changes the fixture transport response, not the authorization or verification rules.

Rejecting a proposal makes no provider call. If a command fails or its acknowledgement is uncertain, refresh history before further work; there is no automatic mutation retry. Another pending request blocks controls within that page, while the host enforces durable identities across pages.

## Recovery rules

| Situation | Host/provider behavior |
|---|---|
| Original outcome unknown | Reconcile first; no effectful recovery proposal |
| Publication permission only | Correction/withdrawal reservation denied |
| Old publication approval reused | Rejected; recovery needs its own decision |
| Permission revoked before dispatch | No provider call for that reserved operation |
| Resource changed after review | Atomic precondition rejection; no resource change |
| Recovery response lost | Reconcile the same operation; do not create a substitute |
| Resource already withdrawn | No silent restoration through correction |
| Successful recovery | New receipt and causal link; original history preserved |

Each provider transaction commits the outcome journal entry together with any resource update. A rejected precondition also has a correlated journal entry, making a verified no-effect result distinguishable from a network timeout.

Withdrawal affects the active board. Content remains in authorized proposals and historical provider records. It is not a deletion service and cannot erase external copies or downstream consequences.

## Local architecture and ownership

~~~text
Browser: pinned ApprovalGate / ActionReceipt + explicit host controls
  -> loopback HTTP commands, exact Origin and per-instance request token
  -> host: canonical proposal -> decision -> permission -> durable operation
  -> provider: operation-key deduplication + resource revision precondition
  -> readback: bound journal outcome -> verification -> receipt projection
~~~

The [projection adapter](../reference/tse_pilot/presentation.py) sends viewVersion tse-design-view/0.1, proposals, operations, and access-filtered resources. This version is separate from tse-pilot/0.2 storage records. The [source attribution](../ui/vendor/tun-design/README.md) pins the upstream design commit and license.

| Local endpoint | Accepted fields |
|---|---|
| GET /api/state | None; returns the current view and local request token |
| POST /api/proposals | content |
| POST /api/recovery | originalId, action (correct/withdraw), content (null for withdrawal) |
| POST /api/decision | proposalId, proposalVersion, decision (approve/reject) |
| POST /api/execute | proposalId, proposalVersion, loseResponse (boolean fixture fault) |
| POST /api/reconcile | operationId |

Unexpected fields are rejected. The browser cannot choose actor, scope, target, permission, canonical provider parameters, or execution identity. Fixture identity is alice-fixture in sandbox; the target is project-board. New fixture stores separately seed all three action permissions. There is no policy-management HTTP endpoint.

The server enforces loopback binding, exact Host/Origin, a per-instance request token for mutations, bounded JSON bodies, duplicate-key rejection, and constrained static paths. These checks reduce selected local-browser attack paths; they do not authenticate a person or protect against a local process that can read state. Do not expose this server through a tunnel or public bind. Python's [HTTP server documentation](https://docs.python.org/3/library/http.server.html) also cautions against production use.

## Verification and remaining work

The [validation record](REVIEW-RECOVERY-VALIDATION-2026-10-01.md) identifies the tested source revision, automated results, browser observations, and remaining gaps.

Run the Python suite from the repository root and the component tests/build from ui. The suites cover approval binding, duplicate protection, revision conflicts, permission separation, HTTP boundaries, and selected rendering semantics. The full [conformance matrix](CONFORMANCE-MATRIX.md) remains unassessed.

The interface uses explicit event handlers for mutations and a cancellable startup read; rendering does not trigger actions. Browser checks follow the journey from displayed review through HTTP, persisted outcome, readback, and receipt.

Remaining work includes production identity and sessions, multi-user operation, remote-provider semantics, cancellation, budgets, partial effects, general supervision components, schema migration, operational controls, and full accessibility/security assessment. The other twelve design components are mapped in the guide but not integrated in this pilot.
