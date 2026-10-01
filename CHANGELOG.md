# Changelog

This log records documentation milestones. The v0.1 label denotes an evolving draft, not a package release. Source commits identify exact revisions.

## 2026-10-01 — Experimental publication pilot

- Added a JSON Schema 2020-12 pilot profile for eight core records and provider readback evidence, with valid and invalid fixtures.
- Added strict JSON decoding, structural validation, material fingerprints, and selected cross-record checks.
- Added a Python host and separate SQLite publication provider with durable reservations, fixture approval/policy, readback, and versioned receipts.
- Added focused tests for stale approval, revocation, expiry, concurrency, corruption, lost responses, and selected process/persistence failures.
- Added a runnable synthetic demonstration and updated all implementation-status guidance.
- Recorded a revision-bound local validation report and captured command output, without claiming complete conformance.

This is a local experiment with trusted fixture identity. It does not release a production SDK, React adapter, remote provider, recovery writes, or complete conformance assessment.

## 2026-10-01 — Engineering documentation expansion

- Added a draft specification with stable requirement identifiers.
- Added the engineering component catalog, architecture, proposed contracts, lifecycle guidance, and glossary.
- Added authority/execution, evidence/memory, supervision/recovery, and design-integration guides.
- Added onboarding, scope, status, integration checklist, existing-approaches, and contribution guidance.
- Added planned validation procedures and a requirement traceability matrix, with runtime evidence explicitly not assessed.
- Added a standard-library documentation checker, regression tests for the checker, and a coverage description.
- Updated the original concept, manifesto, and root overview to reflect the expanded draft.

No engineering runtime, schema package, provider adapter, or runtime conformance result is released by this documentation change.

## 2026-10-01 — Review of founding documents

[Commit 87f456b](https://github.com/kochrisdev/TUN-Systemic-Engineering/commit/87f456b02dbe4018519cc2b87e694e11d78d4d8c) clarified approval and authorization, separated operations from attempts, narrowed verification and retry claims, and tightened the manifesto.

## 2026-10-01 — Initial concept and manifesto

[Commit 90ed133](https://github.com/kochrisdev/TUN-Systemic-Engineering/commit/90ed13320db4ed9a28f8bab8bde8f98b48007604) added the initial README, concept note, and manifesto.
