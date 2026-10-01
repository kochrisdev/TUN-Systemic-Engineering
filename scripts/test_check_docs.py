"""Regression checks for documentation tooling, not engineering runtime conformance."""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import check_docs


SOURCES = {
    "docs/README.md": """# Index

[Specification](SPECIFICATION-v0.1.md)
[Components](COMPONENTS-v0.1.md)
[Validation](VALIDATION-PLAN-v0.1.md)
[Matrix](CONFORMANCE-MATRIX.md)
""",
    "docs/SPECIFICATION-v0.1.md": "# Specification\n\n### TSE-001\n\nA draft requirement.\n",
    "docs/COMPONENTS-v0.1.md": "# Components\n\n## EC-01\n\nRelated: TSE-001.\n",
    "docs/VALIDATION-PLAN-v0.1.md": "# Validation\n\n### V-01\n\nSource: TSE-001.\n",
    "docs/CONFORMANCE-MATRIX.md": """# Matrix

| Requirement | Component | Procedure |
|---|---|---|
| [TSE-001](SPECIFICATION-v0.1.md#tse-001) | [EC-01](COMPONENTS-v0.1.md#ec-01) | [V-01](VALIDATION-PLAN-v0.1.md#v-01) |
""",
}


class DocumentationChecks(unittest.TestCase):
    def run_fixture(self, changes=None):
        files = dict(SOURCES)
        files.update(changes or {})
        with tempfile.TemporaryDirectory(prefix="tse-docs-test-") as temporary:
            root = Path(temporary)
            for name, content in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            output, errors = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                result = check_docs.check(root)
            return result, output.getvalue() + errors.getvalue()

    def assert_failure(self, changes, message):
        result, output = self.run_fixture(changes)
        self.assertEqual(result, 1, output)
        self.assertIn(message, output)

    def test_valid_fixture(self):
        result, output = self.run_fixture()
        self.assertEqual(result, 0, output)
        self.assertIn("1 requirements, 1 components, 1 planned procedures", output)

    def test_missing_file(self):
        self.assert_failure({"README.md": "# Root\n\n[Missing](missing.md)\n"}, "missing local target")

    def test_missing_anchor(self):
        self.assert_failure({"README.md": "# Root\n\n[Missing](docs/README.md#absent)\n"}, "missing heading anchor")

    def test_missing_mapping(self):
        self.assert_failure({"docs/CONFORMANCE-MATRIX.md": "# Matrix\n"}, "must have exactly one mapping")

    def test_duplicate_definition(self):
        source = SOURCES["docs/SPECIFICATION-v0.1.md"] + "\n### TSE-001\n"
        self.assert_failure({"docs/SPECIFICATION-v0.1.md": source}, "duplicate definition TSE-001")

    def test_unknown_identifier(self):
        self.assert_failure({"README.md": "# Root\n\nTSE-999\n"}, "undefined identifier TSE-999")

    def test_procedure_binding(self):
        source = "# Validation\n\n### V-01\n\nNo source requirement.\n"
        self.assert_failure({"docs/VALIDATION-PLAN-v0.1.md": source}, "V-01 does not reference TSE-001")

    def test_invalid_json(self):
        for payload in ('{"key":}', '{"key": 1, "key": 2}', '{"value": NaN}', '{"value": Infinity}'):
            with self.subTest(payload=payload):
                source = "# Root\n\n```json\n" + payload + "\n```\n"
                self.assert_failure({"README.md": source}, "invalid illustrative JSON")

    def test_unclosed_fence(self):
        self.assert_failure({"README.md": "# Root\n\n```text\nopen\n"}, "unclosed code fence")

    def test_fenced_trailing_whitespace(self):
        source = "# Root\n\n```text\ntrailing \n```\n"
        self.assert_failure({"README.md": source}, "trailing whitespace")

    def test_unindexed_document(self):
        self.assert_failure({"docs/EXTRA.md": "# Extra\n"}, "document missing from index")

    def test_bad_link_syntax(self):
        for target in (" ", "https://["):
            with self.subTest(target=target):
                result, output = self.run_fixture({"README.md": f"# Root\n\n[Bad]({target})\n"})
                self.assertEqual(result, 1, output)
                self.assertTrue("empty link target" in output or "malformed link" in output, output)

    def test_duplicate_heading_anchors(self):
        errors = []
        _, _, anchors, _ = check_docs.inspect_markdown(
            "# Title\n\n## Repeat\n\n## Repeat\n", "fixture.md", errors
        )
        self.assertEqual(errors, [])
        self.assertEqual(anchors, {"title", "repeat", "repeat-1"})


if __name__ == "__main__":
    unittest.main()
