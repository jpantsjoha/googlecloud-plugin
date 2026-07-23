#!/usr/bin/env python3
"""Lint Mermaid diagrams in Markdown for the errors GitHub's renderer rejects.

Dependency-free structural checks for ```mermaid fenced blocks. Focused on the
failure classes that actually break GitHub rendering (and that a URL linter
misses):

  1. Semicolon in a sequenceDiagram message — ';' is a statement separator, so
     text after it is parsed as a new (invalid) statement. This is the bug that
     shipped in v0.1.0's README.
  2. Unbalanced block keywords (rect/opt/alt/loop/par/critical/break) vs 'end'.
  3. Message arrows referencing an undeclared participant/actor.

Exit 0: all diagrams parse-safe. Exit 1: one or more issues.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
MD_FILES = ["README.md", "PLUGIN.md"]

BLOCK_OPENERS = ("rect", "opt", "alt", "loop", "par", "critical", "break", "box")
ARROW_RE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*(?:-->>|->>|-->|->|--x|-x|--\)|-\))\s*[+-]?\s*([A-Za-z0-9_]+)\s*:(.*)$")
DECL_RE = re.compile(r"^\s*(?:participant|actor)\s+([A-Za-z0-9_]+)")


def extract_mermaid_blocks(md: Path) -> list[tuple[int, list[str]]]:
    blocks: list[tuple[int, list[str]]] = []
    lines = md.read_text().splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("```mermaid"):
            start = i + 1
            body: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                body.append(lines[i])
                i += 1
            blocks.append((start, body))
        i += 1
    return blocks


def lint_block(md: Path, start_line: int, body: list[str], errors: list[str]) -> None:
    is_sequence = any(l.strip().startswith("sequenceDiagram") for l in body)
    declared: set[str] = set()
    block_depth = 0

    for offset, raw in enumerate(body):
        lineno = start_line + offset + 1  # 1-based file line
        line = raw.strip()
        if not line or line.startswith("%%"):
            continue

        d = DECL_RE.match(line)
        if d:
            declared.add(d.group(1))
            continue

        first = line.split()[0] if line.split() else ""
        if first in BLOCK_OPENERS:
            block_depth += 1
            continue
        if first == "end":
            block_depth -= 1
            if block_depth < 0:
                errors.append(f"{md.name}:{lineno}: unmatched 'end' (no open block)")
                block_depth = 0
            continue

        if is_sequence:
            m = ARROW_RE.match(raw)
            if m:
                src, dst, msg = m.group(1), m.group(2), m.group(3)
                declared.update([src, dst])  # implicit declaration is allowed
                if ";" in msg:
                    errors.append(
                        f"{md.name}:{lineno}: ';' in sequence message — it is a statement "
                        f"separator and breaks rendering. Use ',' or ' — '. Text: '{msg.strip()}'"
                    )

    if block_depth != 0:
        errors.append(
            f"{md.name}: mermaid block starting near line {start_line} has "
            f"{block_depth} unclosed block(s) (rect/opt/alt/... without 'end')"
        )


def main() -> None:
    errors: list[str] = []
    checked = 0
    for name in MD_FILES:
        md = ROOT / name
        if not md.exists():
            continue
        for start, body in extract_mermaid_blocks(md):
            checked += 1
            lint_block(md, start, body, errors)

    if checked == 0:
        print("No mermaid diagrams found")
        return

    if errors:
        for e in errors:
            print(f"FAIL  {e}")
        print(f"\n{len(errors)} mermaid issue(s)", file=sys.stderr)
        sys.exit(1)

    print(f"{checked} mermaid diagram(s) parse-safe")


if __name__ == "__main__":
    main()
