# TUN Systemic Engineering — Documentation Checks

[Documentation index](README.md) · [Contributing](../CONTRIBUTING.md) · [Conformance matrix](CONFORMANCE-MATRIX.md)

## Run the checker

From the repository root, use Python 3.10 or newer:

```sh
python scripts/check_docs.py
```

The [checker source](../scripts/check_docs.py) uses only the standard library and performs read-only checks. It needs no credentials, package installation, or network access. Its exit code is zero on success and nonzero when it finds an issue.

To test the checker itself, run:

```sh
python -B scripts/test_check_docs.py
```

These [regression tests](../scripts/test_check_docs.py) create isolated temporary documentation fixtures, exercise valid and deliberately broken cases, and clean up their fixtures afterward. They do not execute the engineering validation plan. The `-B` option avoids creating Python bytecode files in the checkout.

## What it checks

- Markdown documents have one primary title and balanced fenced blocks.
- Local file links and supported heading anchors resolve within the repository.
- Documents under `docs/` are linked from the documentation index.
- Illustrative JSON blocks parse without duplicate keys or non-JSON numeric constants.
- Requirement, component, and procedure definitions have unique identifiers.
- References to those identifiers are defined.
- Every specification requirement has exactly one row in the conformance matrix.
- Each mapped component and procedure references its assigned requirement.
- Every planned procedure appears in the matrix.
- Markdown lines have no trailing whitespace.

Heading anchors use the repository's simple GitHub-style Markdown convention. The checker supports the inline links and fenced blocks used here; it is not a complete Markdown parser.

## What it does not check

It does not run a host, agent, provider, schema validator, or runtime conformance procedure. It does not authenticate evidence, prove requirement sufficiency, test external URLs, render Mermaid diagrams, or validate accessibility.

It does not turn a proposed field shape into a supported API. Parsing an illustrative JSON fragment only establishes its syntax.

Human review still checks technical meaning, scope, consistency across workflows, provider guarantees, readable diagrams, and honest implementation claims.

## Traceability workflow

Edit requirement text in the specification. Update the relevant component, procedure, and matrix row in the same change. Update the index when adding a document.

Keep IDs stable. When retiring an obligation, document the change and update its mappings deliberately rather than reusing its identifier for a different meaning.

The current runtime matrix remains not assessed. Future execution evidence should identify implementation and specification revisions, environment, procedures, results, reviewer, and limitations.

## Recording validation

A documentation validation record should name the checked source revision, Python version, command, exit status, and limitations. A passing checker establishes only the structural checks listed here.

Runtime validation is described separately in the [validation plan](VALIDATION-PLAN-v0.1.md). Those procedures remain planned until supported by executed or reviewed evidence.
