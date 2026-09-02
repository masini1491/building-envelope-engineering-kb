#!/usr/bin/env python3
"""Lightweight repository integrity checks for the public engineering KB."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]

ALLOWED_VERIFICATION = {
    "VERIFIED_PRIMARY",
    "VERIFIED_PROJECT",
    "HIGH_CONFIDENCE",
    "FIELD_OBSERVATION",
    "UNVERIFIED",
    "CONFLICTING_EVIDENCE",
}

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
MARKDOWN_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
CJK_RE = re.compile(r"[\u3400-\u9fff]")

# LANGUAGE.md permits standards, material designations, machine identifiers and
# stable status/schema tokens to remain in their original form. These patterns
# are intentionally narrow so ordinary human-facing English headings still fail.
LANGUAGE_HEADING_ALLOWLIST = [
    re.compile(r"^(?:ASTM|CNS|AAMA|FGIA|ISO|ACI|AISC|AWS|NAFS|FEA)(?:[ /+&.0-9A-Z_-]*)$"),
    re.compile(r"^(?:A[24]-\d{2}|\d{4}-[HT]\d+)$"),
    re.compile(r"^(?:PASS|WARNING|FAIL|INCOMPLETE|NOT_APPLICABLE)$"),
    re.compile(r"^\d+\.\s+`[a-z0-9_]+`$"),
]


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_json(errors: list[str]) -> None:
    for path in sorted(ROOT.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            fail(errors, f"JSON parse failed: {path.relative_to(ROOT)}: {exc}")
            continue

        if path.parent.name == "schemas" and path.name.endswith(".schema.json"):
            schema_id = data.get("$id", "")
            if "example.invalid" in schema_id:
                fail(errors, f"Invalid placeholder $id: {path.relative_to(ROOT)} -> {schema_id}")

            try:
                from jsonschema import Draft202012Validator
            except ImportError:
                Draft202012Validator = None

            if Draft202012Validator is not None:
                try:
                    Draft202012Validator.check_schema(data)
                except Exception as exc:  # noqa: BLE001
                    fail(errors, f"JSON Schema invalid: {path.relative_to(ROOT)}: {exc}")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    result: dict[str, str] = {}
    for raw in text[4:end].splitlines():
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def validate_frontmatter(errors: list[str]) -> None:
    knowledge = ROOT / "knowledge"
    if not knowledge.exists():
        return

    for path in sorted(knowledge.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if not fm:
            continue
        status = fm.get("verification_status")
        if status and status not in ALLOWED_VERIFICATION:
            fail(
                errors,
                f"Unknown verification_status: {path.relative_to(ROOT)} -> {status}",
            )


def normalize_link_target(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1]
    if " " in raw and not raw.startswith(("http://", "https://")):
        # Markdown optional title: path "title"
        raw = raw.split(" ", 1)[0]
    return unquote(raw.split("#", 1)[0])


def validate_markdown_links(errors: list[str]) -> None:
    for path in sorted(ROOT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK_RE.finditer(text):
            raw = match.group(1).strip()
            if not raw or raw.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = normalize_link_target(raw)
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                fail(errors, f"Link escapes repository: {path.relative_to(ROOT)} -> {raw}")
                continue
            if not resolved.exists():
                fail(errors, f"Broken relative link: {path.relative_to(ROOT)} -> {raw}")


def validate_public_reference_policy(errors: list[str]) -> None:
    refs = ROOT / "references"
    if not refs.exists():
        return
    forbidden_dir_names = {"project-knowledge", "private-project", "private-projects"}
    for path in refs.rglob("*"):
        if path.is_dir() and path.name.lower() in forbidden_dir_names:
            fail(errors, f"Private-project reference directory is not allowed: {path.relative_to(ROOT)}")


def language_heading_allowed(heading: str) -> bool:
    compact = re.sub(r"[*_]", "", heading).strip()
    return any(pattern.fullmatch(compact) for pattern in LANGUAGE_HEADING_ALLOWLIST)


def validate_language_policy(errors: list[str]) -> None:
    """Enforce LANGUAGE.md for human-facing headings under knowledge/.

    The check deliberately targets headings, where language drift is easy to
    detect with low false-positive risk. Prose may contain technical English and
    formal standard names, so prose remains a review concern rather than a hard
    CI rule.
    """

    knowledge = ROOT / "knowledge"
    if not knowledge.exists():
        return

    for path in sorted(knowledge.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
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
                fail(
                    errors,
                    f"Temporary language fallback heading is not allowed: "
                    f"{path.relative_to(ROOT)}:{line_no} -> {heading}",
                )
                continue

            if CJK_RE.search(heading) or language_heading_allowed(heading):
                continue

            fail(
                errors,
                f"Human-facing heading must be zh-TW-first per LANGUAGE.md: "
                f"{path.relative_to(ROOT)}:{line_no} -> {heading}",
            )


def main() -> int:
    errors: list[str] = []
    validate_json(errors)
    validate_frontmatter(errors)
    validate_markdown_links(errors)
    validate_public_reference_policy(errors)
    validate_language_policy(errors)

    if errors:
        print("Repository validation failed:\n")
        for item in errors:
            print(f"- {item}")
        return 1

    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
