# Getting Started With TUN Systemic Engineering

[Documentation index](README.md) · [Specification](SPECIFICATION-v0.1.md) · [Integration checklist](INTEGRATION-CHECKLIST.md) · [Status](STATUS-AND-ROADMAP.md)

## What you can use today

Read and adapt the draft documents, run the documentation checker, or try the [local publication pilot](PILOT.md). The pilot includes experimental JSON schemas, a Python/SQLite host and provider, and focused tests. Follow its setup instructions; it is not a stable installable engineering SDK.

For context on a running example, the separate design repository includes a [local host pilot](https://github.com/kochrisdev/TUN-Systemic-Design/blob/81b52e8d64c90891ef1340802502e398dc6c0340/examples/host-integration/README.md). Follow that repository's instructions there. Its implementation and test results do not establish compliance with this engineering draft.

## Read in this order

1. [Introduction](INTRODUCTION.md): understand the publication example.
2. [Specification](SPECIFICATION-v0.1.md): identify the applicable obligations.
3. [Components](COMPONENTS-v0.1.md) and [Architecture](ARCHITECTURE.md): assign host responsibilities.
4. [Contracts](CONTRACTS-v0.1.md) and [Lifecycles](LIFECYCLES-v0.1.md): model records and state.
5. [Integration checklist](INTEGRATION-CHECKLIST.md): record decisions, ownership, and evidence.

## Prepare the first workflow

Choose one bounded action, such as publishing to a local board. Record its target, actor, material content, expected effects, consequence, and recovery limits.

Define the provider's duplicate protection and readback behavior before designing retries. Decide which evidence can support the intended completion claim.

Use fixture content and identity for the first implementation. An LLM is optional; a person can prepare the proposal while the action contract is being tested.

## Implementation order

Start with canonical proposals, recorded human decisions, host authorization, and durable operation identity. Add the provider adapter and its effect store, then verification and receipt projection.

Inject a lost acknowledgement after provider commit. Restart the host and reconcile the original operation. Demonstrate that the outcome becomes known without another publication.

The pilot now demonstrates that publication/readback slice. Separately authorized withdrawal, richer supervision, the React adapter, and additional providers remain future increments. The [roadmap](STATUS-AND-ROADMAP.md) gives exit criteria.

## Check the documentation

With Python 3.10 or newer installed, run from the repository root:

```sh
python scripts/check_docs.py
```

On Windows, `py -3 scripts/check_docs.py` is an equivalent option if the launcher selects a supported Python version.

The checker uses the standard library and requires no third-party packages or network access. It validates documentation structure and traceability; it does not exercise AI actions or providers. See [Documentation checks](DOCUMENTATION-CHECKS.md) for exact coverage.

## Record progress honestly

A requirement being documented is draft specification work. A function existing is implementation work. A passing test is evidence only for its named case and environment.

Keep unresolved cases visible in the assessment. A working demonstration, passing Markdown checks, and production readiness are separate milestones.
