"""Check TUN documentation structure and draft traceability (no runtime tests)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".venv", "node_modules", "__pycache__", "dist", "build"}
ID_RE = re.compile(r"\b(?:TSE-\d{3}|EC-\d{2}|V-\d{2})\b")
LINK_RE = re.compile(r"\[[^\]\n]+\]\(([^)\n]+)\)")
HEADING_RE = re.compile(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$")


def slug(text: str) -> str:
    text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text).replace("`", "")
    text = re.sub(r"[^\w\-\s]", "", text.lower(), flags=re.UNICODE)
    return re.sub(r"\s", "-", text)


def no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_nonfinite(value: str):
    raise ValueError(f"non-finite value is not JSON: {value}")


def inspect_markdown(text: str, name: str, errors: list[str]):
    prose, headings, blocks = [], [], []
    fence = None
    language = ""
    block_lines = []
    opening_line = 0
    for line_number, line in enumerate(text.splitlines(), 1):
        if line.rstrip() != line:
            errors.append(f"{name}:{line_number}: trailing whitespace")
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if match and match[1][0] == fence[0] and len(match[1]) >= len(fence) and not match[2].strip():
                blocks.append((language, "\n".join(block_lines), opening_line))
                fence = None
                block_lines = []
            else:
                block_lines.append(line)
            continue
        if match:
            fence = match[1]
            language = match[2].strip().lower()
            opening_line = line_number
            continue
        prose.append(line)
        heading = HEADING_RE.match(line)
        if heading:
            headings.append((len(heading[1]), heading[2]))
    if fence:
        errors.append(f"{name}:{opening_line}: unclosed code fence")
    if sum(level == 1 for level, _ in headings) != 1:
        errors.append(f"{name}: expected exactly one level-one title")
    anchors = set()
    for _, heading in headings:
        base = slug(heading)
        candidate, suffix = base, 0
        while candidate in anchors:
            suffix += 1
            candidate = f"{base}-{suffix}"
        anchors.add(candidate)
    return "\n".join(prose), headings, anchors, blocks


def definition_blocks(text: str, prefix: str) -> dict[str, str]:
    pattern = re.compile(rf"(?m)^#{{2,6}} ({prefix}-\d+)\s*$")
    matches = list(pattern.finditer(text))
    return {
        match[1]: text[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(text)]
        for index, match in enumerate(matches)
    }


def check(root: Path) -> int:
    root = root.resolve()
    errors: list[str] = []
    documents = {}
    for path in sorted(root.rglob("*.md")):
        if any(part in SKIP for part in path.relative_to(root).parts):
            continue
        name = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{name}: cannot read UTF-8: {exc}")
            continue
        documents[name] = (path, text, inspect_markdown(text, name, errors))

    local_links = 0
    json_blocks = 0
    index_targets: set[str] = set()
    for name, (path, _, (prose, _, _, blocks)) in documents.items():
        for match in LINK_RE.finditer(prose):
            raw = match[1].strip()
            if not raw:
                errors.append(f"{name}: empty link target")
                continue
            target = raw[1:raw.index(">")] if raw.startswith("<") and ">" in raw else raw.split()[0]
            try:
                parsed = urlsplit(target)
            except ValueError as exc:
                errors.append(f"{name}: malformed link {target}: {exc}")
                continue
            if parsed.scheme or parsed.netloc:
                continue
            target_path = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if not target_path.is_relative_to(root):
                errors.append(f"{name}: link escapes repository: {target}")
                continue
            if not target_path.is_file():
                errors.append(f"{name}: missing local target: {target}")
                continue
            local_links += 1
            target_name = target_path.relative_to(root).as_posix()
            if name == "docs/README.md":
                index_targets.add(target_name)
            if parsed.fragment and target_name in documents:
                if unquote(parsed.fragment) not in documents[target_name][2][2]:
                    errors.append(f"{name}: missing heading anchor: {target}")
        for language, body, line in blocks:
            if language == "json":
                json_blocks += 1
                try:
                    json.loads(body, object_pairs_hook=no_duplicate_keys, parse_constant=reject_nonfinite)
                except (ValueError, json.JSONDecodeError) as exc:
                    errors.append(f"{name}:{line}: invalid illustrative JSON: {exc}")

    required = {
        "TSE": "docs/SPECIFICATION-v0.1.md",
        "EC": "docs/COMPONENTS-v0.1.md",
        "V": "docs/VALIDATION-PLAN-v0.1.md",
    }
    definitions = {}
    for prefix, name in required.items():
        if name not in documents:
            errors.append(f"missing source document: {name}")
            definitions[prefix] = {}
            continue
        _, text, (_, headings, _, _) = documents[name]
        ids = [heading for _, heading in headings if re.fullmatch(rf"{prefix}-\d+", heading)]
        for identifier, count in Counter(ids).items():
            if count != 1:
                errors.append(f"{name}: duplicate definition {identifier}")
        definitions[prefix] = definition_blocks(text, prefix)
        if not ids:
            errors.append(f"{name}: no {prefix} definitions")

    known_ids = set().union(*(set(group) for group in definitions.values()))
    for name, (_, _, (prose, _, _, _)) in documents.items():
        for identifier in set(ID_RE.findall(prose)) - known_ids:
            errors.append(f"{name}: undefined identifier {identifier}")
        if name.startswith("docs/") and name != "docs/README.md" and name not in index_targets:
            errors.append(f"docs/README.md: document missing from index: {name}")

    matrix_name = "docs/CONFORMANCE-MATRIX.md"
    matrix = documents.get(matrix_name)
    rows = []
    if matrix:
        for line in matrix[1].splitlines():
            if re.match(r"^\| \[TSE-\d{3}\]", line):
                ids = ID_RE.findall(line)
                if len(ids) != 3 or not ids[0].startswith("TSE-") or not ids[1].startswith("EC-") or not ids[2].startswith("V-"):
                    errors.append(f"{matrix_name}: malformed mapping row: {line}")
                    continue
                rows.append(tuple(ids))
    else:
        errors.append(f"missing source document: {matrix_name}")

    mapped_rules = Counter(row[0] for row in rows)
    for identifier in definitions["TSE"]:
        if mapped_rules[identifier] != 1:
            errors.append(f"{matrix_name}: {identifier} must have exactly one mapping")
    for rule, component, scenario in rows:
        if rule not in definitions["TSE"]:
            errors.append(f"{matrix_name}: unknown requirement {rule}")
        if rule not in set(ID_RE.findall(definitions["EC"].get(component, ""))):
            errors.append(f"{matrix_name}: {component} does not reference {rule}")
        if rule not in set(ID_RE.findall(definitions["V"].get(scenario, ""))):
            errors.append(f"{matrix_name}: {scenario} does not reference {rule}")
    unused_scenarios = set(definitions["V"]) - {row[2] for row in rows}
    if unused_scenarios:
        errors.append(f"{matrix_name}: unmapped procedures: {', '.join(sorted(unused_scenarios))}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Documentation check failed: {len(errors)} issue(s).", file=sys.stderr)
        return 1
    print(
        f"Documentation checks passed: {len(documents)} Markdown files, "
        f"{local_links} local links, {json_blocks} illustrative JSON block(s), "
        f"{len(definitions['TSE'])} requirements, {len(definitions['EC'])} components, "
        f"{len(definitions['V'])} planned procedures."
    )
    print("No runtime conformance procedures were executed; external URLs and diagram rendering were not tested.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    args = parser.parse_args()
    return check(args.root)


if __name__ == "__main__":
    raise SystemExit(main())
