# Local Supervision Pilot — Validation Record

Executed: 2 October 2026. Status: focused local validation, not full conformance or independent certification.

[Documentation index](README.md) · [Local supervision guide](LOCAL-SUPERVISION-PILOT.md) · [Run the interface](REVIEW-AND-RECOVERY-PILOT.md) · [Earlier review/recovery evidence](REVIEW-RECOVERY-VALIDATION-2026-10-01.md)

## Revision and environment

- Tested implementation: [8255167](https://github.com/kochrisdev/TUN-Systemic-Engineering/commit/8255167d16389d7edff53b76de32d8c699142aa0) (8255167d16389d7edff53b76de32d8c699142aa0).
- Storage profile: tse-pilot/0.3; browser projection: tse-design-view/0.2.
- Pinned design components remain from [81b52e8](https://github.com/kochrisdev/TUN-Systemic-Design/tree/81b52e8d64c90891ef1340802502e398dc6c0340). No additional design components were integrated.
- Windows 11 build 26200; Python 3.13.4; SQLite 3.49.1; pinned Python requirements.
- Node 22.23.2; npm 10.9.8; React 19.3.0; Vite 7.3.6; Vitest 4.1.11; TypeScript 5.8.3; locked UI dependencies.
- Isolated Headless Chrome 154.0.0.0 using the native Windows agent-browser binary.
- Agent-executed checks and visual inspection; no independent human, assistive-technology, or production security assessment.

This evidence commit follows the tested implementation. Its changes are documentation and captured evidence only. Older validation records retain their original scope and revisions.

## Executed checks

| Check | Observed result |
|---|---|
| Python unittest discovery | 82 passed: 36 publication/contract, 14 recovery, 13 HTTP/projection, 19 supervision |
| UI component suite | 10 passed, including explicit queue controls, zero-budget dispatch disablement, cancellation labels, and render without side effects |
| Reproducible UI install | npm ci succeeded; audit reported zero known vulnerabilities at execution time |
| TypeScript check and Vite build | Exit 0; client bundle produced |
| Documentation checker at tested source | 33 Markdown files, 515 local links, one illustrative JSON block, 32 requirements, 12 components, 32 planned procedures |
| Documentation-checker regression suite | 13 passed |
| Command-line lost-response demonstration | Pending before readback; completed after reopening; one provider journal row |
| Browser journey | Two effective queued cancellations; three completed publish/correct/withdraw operations; cap retained after reload |
| Mobile viewport smoke check | 390 × 844; no document-width overflow; inspected budget and history views |

See [captured results](../validation/supervision-2026-10-02.txt). The documentation counts precede this report and its navigation additions. The audit is not a security certification.

The successful build retains ignored upstream use-client directive and sourcemap-location warnings. This is a client-only build, not a server-component integration.

## End-to-end observations

| Flow boundary | Observed evidence |
|---|---|
| Review → host reservation | Keyboard approval followed by a separate queue action; zero consumption and no provider resource |
| Queued cancellation → stored control | Cancelled host status, separate effective control record, no resource, budget still zero |
| Dispatch → provider → uncertain receipt | Lost-response simulation consumed one slot and left the publication pending verification |
| Readback → historical receipt | Reconciliation established completed without another dispatch charge |
| Recovery review → provider revision | Separately approved correction and withdrawal advanced the same resource to revisions 2 and 3; original receipt remained completed |
| Exhausted budget → explicit controls | Dispatch button disabled; cancellation and reconciliation remained enabled |
| Reload → persisted view | Five operations: two cancelled, three completed; two effective control records; one withdrawn resource at revision 3; used 3, remaining 0 |

The browser started with a new fixture directory and the host's three-slot allowance. Cancellation before dispatch did not consume a slot. Publishing, correcting, and withdrawing each consumed one. At zero, another approved proposal could be queued and cancelled but not dispatched through the interface. A readback at zero succeeded without changing the charge.

[Desktop history screenshot](../validation/supervision-2026-10-02.png) · [Mobile history screenshot](../validation/supervision-mobile-2026-10-02.png).

The first browser automation connection closed after the second proposal was approved, before it was queued. On reopening, persisted state showed the first cancellation, no provider resource, and zero usage. That unused approval had expired; the host rejected reservation with HTTP 403. A fresh proposal and approval were used to continue. No uncertain mutation was automatically replayed.

The final checked browser session reported no page errors or console messages and no development error overlay. The server log includes a harmless missing favicon response; diagnostics are not a claim that every request returned 200. The test server and isolated browser were stopped afterward, preserving the synthetic stores.

## Focused negative coverage

[Supervision tests](../tests/test_supervision.py) exercise cancellation versus dispatch contention, late cancellation during a held provider call, stale revisions, repeated cancellation across restart, another actor/scope, fresh reviewed work after cancellation, missing/zero caps, two workers competing for the last slot, no double charge, and shared recovery consumption.

They also exercise rollback when writing budget or cancellation evidence fails; a committed dispatch claim followed by a simulated crash before the provider call; cap changes and restart without resetting usage; permission denial without charging; non-mutating readback of uninvoked operations; invalid controls; and refusal of nonempty older-profile stores.

[HTTP tests](../tests/test_review_server.py) independently check zero-budget enforcement, cancellation redelivery, late cancellation without relabelling completed work, compatible-store reopen without refill, unexpected budget fields, and rejection of the removed execute shortcut. Race and crash claims come from these focused runtime tests, not browser clicks.

## Limits and follow-up

This demonstrates one local SQLite-backed host/provider model with trusted fixture identity. It does not establish distributed exactly-once effects, real worker termination, remote cancellation, production identity, multi-user security, or hardware durability.

The budget counts committed dispatch claims, not successful outcomes, money, tokens, or elapsed time. A crash after claim can spend a slot without a provider call. Readback and other non-dispatch work are not rate-limited by this cap.

One usability limitation was observed: an approved but expired proposal can retain its queue button even while the review card says it expired. The host rejects it; the interface could make that disabled state clearer. This does not authorize reuse of the approval.

Browser evidence covers one engine and a mobile-sized viewport, not an actual mobile browser, complete keyboard navigation, screen readers, or a full accessibility audit. Partial effects, time/token/money budgets, bounded polling, general supervision components, migration, and remote-provider assessment remain open.

The full [conformance matrix](CONFORMANCE-MATRIX.md) remains unassessed. These focused tests are not execution of all 32 planned procedures.

