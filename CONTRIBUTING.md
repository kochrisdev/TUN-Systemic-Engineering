# Contributing to TUN Systemic Engineering

TUN Systemic Engineering is at the draft specification stage. Contributions can clarify behavior, identify failure cases, improve the documents, or develop a bounded implementation through a separately scoped change.

[Documentation index](docs/README.md) · [Scope](docs/SCOPE.md) · [Status](docs/STATUS-AND-ROADMAP.md)

## Propose a focused change

Describe the concrete action or failure scenario, the current ambiguity, and the desired behavior. Include provider documentation or reproducible evidence when it matters.

Keep requirement changes separate from claims that an implementation already satisfies them. A document, schema, runtime, and validation result have distinct completion criteria.

## Maintain the document relationships

The specification owns behavioral requirements. Contracts and lifecycles explain records and transitions. Components and architecture assign responsibility. Procedures in the validation plan provide evidence expectations, and the matrix maps them to requirements.

Update affected guides, scenarios, status, and the changelog together. Keep stable identifiers for requirements, components, and scenarios; do not reuse an old identifier for unrelated meaning. Document material decisions and their reasoning.

When changing a design-library mapping, inspect and cite the exact upstream commit. Do not infer compatibility from matching type names or a website summary.

## Validate documentation

Run from the repository root with Python 3.10 or newer:

```sh
python scripts/check_docs.py
```

When changing the checker, also run `python -B scripts/test_check_docs.py` to exercise its regression fixtures.

Also review technical meaning, examples, evidence scope, and provider assumptions. The checker cannot establish semantic correctness or runtime conformance. See [Documentation checks](docs/DOCUMENTATION-CHECKS.md).

## Share evidence responsibly

Use synthetic or appropriately authorized fixtures. Do not include credentials, private payloads, raw production databases, or identifying traces in issues, commits, or reports.

Runtime evidence should identify source revision, environment, procedure, result, and limitations. Preserve earlier reports with their original scope when later tests improve coverage.

For suspected sensitive security issues, use a private repository reporting channel if one is available; do not publish exploit details or secrets in a public issue. This repository does not promise a response time or operate a certification service.
