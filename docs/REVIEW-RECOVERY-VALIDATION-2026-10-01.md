# Review and Recovery Pilot — Validation Record

Executed: 1 October 2026. Status: focused local validation, not full conformance or independent certification.

[Documentation index](README.md) · [Run the interface](REVIEW-AND-RECOVERY-PILOT.md) · [Earlier publication evidence](PILOT-VALIDATION-2026-10-01.md)

## Revision and environment

- Tested engineering implementation: [725dfbb](https://github.com/kochrisdev/TUN-Systemic-Engineering/commit/725dfbbd76a8e8785ec63fa5d87ab2feea60eba3) (725dfbbd76a8e8785ec63fa5d87ab2feea60eba3).
- Pinned design source: [81b52e8](https://github.com/kochrisdev/TUN-Systemic-Design/tree/81b52e8d64c90891ef1340802502e398dc6c0340).
- Windows 11 build 26200; Python 3.13.4; SQLite 3.49.1; Python dependencies pinned in requirements-pilot.txt.
- Node 22.23.2; npm 10.9.8; React 19.3.0; Vite 7.3.6; Vitest 4.1.11; TypeScript 5.8.3. The UI lockfile records resolved dependencies.
- Browser: isolated Headless Chrome 154.0.0.0, controlled with the native Windows agent-browser 0.38.1 binary.
- Review method: agent-executed automated checks and visual browser inspection; no independent human review or assistive-technology assessment.

The evidence commit containing this report follows the tested implementation commit. Later source changes require a new run; this report does not certify an evolving branch.

## Executed checks

| Check | Observed result |
|---|---|
| Python unittest discovery | 58 passed: 36 publication/contract tests, 14 recovery tests, 8 local HTTP/projection tests |
| UI component suite | 6 passed against the actual pinned ApprovalGate and ActionReceipt |
| TypeScript check and Vite build | Exit 0; client bundle produced |
| Documentation checker | 31 Markdown files, 484 local links, 32 requirements, 12 components, 32 planned procedures checked at the tested revision |
| Documentation-checker regression suite | 13 passed |
| Command-line lost-response demonstration | Pending before readback, completed afterward, one provider journal row for the single publication |
| npm audit | Zero reported known vulnerabilities at execution time; not a security certification |
| Upstream source comparison | All seven vendored source/style/license files match the pinned source after documented line-ending/end-of-file whitespace normalization |
| Browser load and diagnostics | Page and controls render; no error overlay, page errors, or console messages reported in the checked session |

See the [captured automated results and browser observations](../validation/review-recovery-2026-10-01.txt). The report and its navigation links are added after the documentation counts above.

Build output includes ignored upstream use-client directives and associated sourcemap-location warnings. The build succeeds and the browser renders in a client-only context. No server-component support is claimed.

## Observed browser journey

1. Prepared the synthetic publication and approved it using keyboard focus plus Enter. Approval showed no operation receipt and required a separate execute action.
2. Executed with lost-response simulation enabled. The provider board showed an active publication at revision 1 while its receipt remained pending verification.
3. Reconciled the original operation. The receipt became completed without creating another publication.
4. Prepared a correction. Review showed the exact original publication ID, required revision 1, replacement content, and recovery limit. Fresh approval and execution were required.
5. Reconciled the correction. The board advanced to revision 2 and the original publication receipt remained completed.
6. Prepared and separately approved withdrawal for that publication at revision 2. Execution again used lost-response simulation; readback established its outcome.
7. Reloaded the page. The host returned three completed historical operations—publish, correct, withdraw—and one withdrawn resource at revision 3. Recovery operations retained the original-operation link.
8. Inspected desktop and 390 × 844 mobile layouts. The mobile document-width check found no horizontal overflow. This is a layout smoke test, not mobile-browser or accessibility certification.

The [review screenshot](../validation/review-recovery-2026-10-01.png) shows the final state. Displayed fixture identity is not proof of authenticated human identity. The original publication remains an historical event; withdrawal is not labelled reversal or deletion.

## Negative coverage added in this increment

Recovery tests reject missing or inconsistent recovery bindings, substituted action authority, original approval reuse, insufficient recovery permission, queued revocation, unknown original outcomes, and another actor's recovery attempt. They exercise stale resource revisions, unresolved replacement blocking, response loss, retained original history, legacy-store refusal, and prevention of silent restoration after withdrawal.

HTTP tests exercise exact approval requirements, unexpected command fields, duplicate JSON keys, oversized bodies, origin/token/Host/fetch-site boundaries, static-path traversal, rejection without execution, and contradiction projection without false success. These are selected boundary tests, not a penetration test.

Component tests cover review detail, escaped text, approval versus execution, unverified-success downgrading, separate withdrawal receipts, and unsafe evidence links. They use server-side rendering; the browser journey provides separate interaction evidence.

## Limitations and open work

The [full conformance matrix](CONFORMANCE-MATRIX.md) remains unassessed. Neither these tests nor the earlier report establish complete coverage of its 32 procedures.

There is no production authentication, external provider, multi-user security assessment, general supervision interface, cancellation, budget enforcement, partial-effect model, automatic retry, retention/deletion service, migration, or deployment reliability evidence. Fixture policy and the local provider are trusted.

Browser checks covered one controlled sequence, one desktop browser engine, and one mobile viewport size. They did not assess screen readers, keyboard-only traversal of every control, color contrast comprehensively, reduced motion, cross-browser behavior, or load. The loopback HTTP server must not be exposed publicly.
