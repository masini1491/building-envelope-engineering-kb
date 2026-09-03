#!/usr/bin/env python3
"""Fast changed-Markdown heading preflight aligned with repository language policy."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
CJK_RE = re.compile(r"[\u3400-\u9fff]")
LATIN_RE = re.compile(r"[A-Za-z]")

LANGUAGE_HEADING_ALLOWLIST = [
    re.compile(r"^(?:ASTM|CNS|AAMA|FGIA|ISO|ACI|AISC|AWS|NAFS|FEA)(?:[ /+&.0-9A-Z_-]*)$"),
    re.compile(r"^(?:A[24]-\d{2}|\d{4}-[HT]\d+)$"),
    re.compile(r"^(?:PASS|WARNING|FAIL|INCOMPLETE|NOT_APPLICABLE)$"),
    re.compile(r"^\d+\.\s+`[a-z0-9_]+`$"),
    re.compile(r"^`[^`]+`$"),
    re.compile(r"^CC BY 4\.0$"),
]

LANGUAGE_PREFIX_ALLOWLIST = [
    re.compile(r"^(?:ASTM|CNS|AAMA|FGIA|ISO|ACI|AISC|AWS|NAFS|FEA)\b"),
    re.compile(r"^(?:A[24]-\d{2}|\d{4}-[HT]\d+)\b"),
    re.compile(r"^(?:PASS|WARNING|FAIL|INCOMPLETE|NOT_APPLICABLE)\b"),
    re.compile(r"^(?:AI)\b"),
    re.compile(r"^(?:A2|C\d{3,4})\b"),
    re.compile(r"^(?:I\s+與\s+S)\b"),
]


def normalize_human_heading(heading: str) -> str:
    compact = re.sub(r"[*_]", "", heading).strip()
    return re.sub(r"^(?:\d+\.|[A-Z]\.)\s+", "", compact)


def heading_is_zh_tw_first(heading: str) -> bool:
    compact = normalize_human_heading(heading)
    if any(pattern.fullmatch(compact) for pattern in LANGUAGE_HEADING_ALLOWLIST):
        return True

    cjk = CJK_RE.search(compact)
    if not cjk:
        return False

    latin = LATIN_RE.search(compact)
    if not latin or cjk.start() < latin.start():
        return True

    return any(pattern.match(compact) for pattern in LANGUAGE_PREFIX_ALLOWLIST)


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"Cannot read Markdown file: {path}: {exc}"]

    in_fence = False
    in_frontmatter = text.startswith("---\n")
    frontmatter_done = not in_frontmatter

    for line_no, line in enumerate(text.splitlines(), 1):
        if in_frontmatter and not frontmatter_done:
            if line_no > 1 and line.strip() == "---":
                frontmatter_done = True
            continue

        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        match = MARKDOWN_HEADING_RE.match(line)
        if not match:
            continue
        heading = match.group(2).strip()

        if "工程主題：" in heading:
            errors.append(f"Temporary language fallback heading is not allowed: {path}:{line_no} -> {heading}")
        elif not heading_is_zh_tw_first(heading):
            errors.append(f"Human-facing heading must be zh-TW-first per LANGUAGE.md: {path}:{line_no} -> {heading}")

    return errors


def resolve_markdown_paths(raw_paths: list[str]) -> list[Path]:
    resolved: list[Path] = []
    seen: set[Path] = set()
    for raw in raw_paths:
        path = Path(raw)
        if not path.is_absolute():
            path = ROOT / path
        path = path.resolve()
        if path.suffix.lower() != ".md" or not path.is_file() or path in seen:
            continue
        seen.add(path)
        resolved.append(path)
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description="Check zh-TW-first headings in selected Markdown files.")
    parser.add_argument("paths", nargs="+", help="Changed Markdown paths to check")
    args = parser.parse_args()

    paths = resolve_markdown_paths(args.paths)
    if not paths:
        print("Markdown heading preflight skipped: no existing Markdown paths supplied.")
        return 0

    errors: list[str] = []
    for path in paths:
        errors.extend(check_file(path))

    if errors:
        print("Markdown heading preflight failed:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Markdown heading preflight passed for {len(paths)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
