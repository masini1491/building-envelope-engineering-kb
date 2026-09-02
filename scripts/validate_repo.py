#!/usr/bin/env python3
"""Repository integrity and information-architecture checks for the public engineering KB."""

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
LATIN_RE = re.compile(r"[A-Za-z]")

LANGUAGE_HEADING_ALLOWLIST = [
    re.compile(r"^(?:ASTM|CNS|AAMA|FGIA|ISO|ACI|AISC|AWS|NAFS|FEA)(?:[ /+&.0-9A-Z_-]*)$"),
    re.compile(r"^(?:A[24]-\d{2}|\d{4}-[HT]\d+)$"),
    re.compile(r"^(?:PASS|WARNING|FAIL|INCOMPLETE|NOT_APPLICABLE)$"),
    re.compile(r"^\d+\.\s+`[a-z0-9_]+`$"),
    re.compile(r"^`[^`]+`$"),
    re.compile(r"^CC BY 4\.0$"),
]

# These prefixes are stable identifiers / abbreviations explicitly allowed by LANGUAGE.md.
# They may remain before the Chinese explanation without being treated as an English-first prose heading.
LANGUAGE_PREFIX_ALLOWLIST = [
    re.compile(r"^(?:ASTM|CNS|AAMA|FGIA|ISO|ACI|AISC|AWS|NAFS|FEA)\b"),
    re.compile(r"^(?:A[24]-\d{2}|\d{4}-[HT]\d+)\b"),
    re.compile(r"^(?:PASS|WARNING|FAIL|INCOMPLETE|NOT_APPLICABLE)\b"),
    re.compile(r"^(?:AI)\b"),
    re.compile(r"^(?:A2|C\d{3,4})\b"),
    re.compile(r"^(?:I\s+與\s+S)\b"),
]

FORBIDDEN_KNOWLEDGE_DIRS = {
    "knowledge/standards",
    "knowledge/engineering-notes",
}

FORBIDDEN_ONE_TIME_SCRIPTS = {
    "scripts/finish_language_fallbacks.py",
    "scripts/localize_remaining_headings.py",
    "scripts/normalize_markdown_language.py",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def load_json(path: Path, errors: list[str]) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(errors, f"JSON parse failed: {path.relative_to(ROOT)}: {exc}")
        return None


def validate_json(errors: list[str]) -> None:
    for path in sorted(ROOT.rglob("*.json")):
        data = load_json(path, errors)
        if data is None:
            continue

        if path.parent.name == "schemas" and path.name.endswith(".schema.json"):
            if not isinstance(data, dict):
                fail(errors, f"Schema root must be object: {path.relative_to(ROOT)}")
                continue
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

    canonical_owners: dict[str, Path] = {}

    for path in sorted(knowledge.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if not fm:
            continue

        status = fm.get("verification_status")
        if status and status not in ALLOWED_VERIFICATION:
            fail(errors, f"Unknown verification_status: {path.relative_to(ROOT)} -> {status}")

        canonical_key = fm.get("canonical_key", "").strip()
        is_owner = fm.get("canonical_owner", "").lower() == "true"
        if canonical_key and is_owner:
            if canonical_key in canonical_owners:
                other = canonical_owners[canonical_key]
                fail(
                    errors,
                    "Duplicate canonical owner: "
                    f"{canonical_key} -> {other.relative_to(ROOT)} and {path.relative_to(ROOT)}",
                )
            else:
                canonical_owners[canonical_key] = path


def normalize_link_target(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1]
    if " " in raw and not raw.startswith(("http://", "https://")):
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


def validate_architecture(errors: list[str]) -> None:
    for rel in sorted(FORBIDDEN_KNOWLEDGE_DIRS):
        if (ROOT / rel).exists():
            fail(errors, f"Retired catch-all/standards knowledge directory must not return: {rel}")

    for rel in sorted(FORBIDDEN_ONE_TIME_SCRIPTS):
        if (ROOT / rel).exists():
            fail(errors, f"One-time migration script must not return to main: {rel}")


def validate_indexes(errors: list[str]) -> None:
    knowledge_index = ROOT / "indexes" / "knowledge-index.json"
    standards_index = ROOT / "indexes" / "standards-index.json"

    if not knowledge_index.exists():
        fail(errors, "Missing indexes/knowledge-index.json")
    else:
        data = load_json(knowledge_index, errors)
        if isinstance(data, dict):
            domains = data.get("domains", [])
            if not isinstance(domains, list):
                fail(errors, "knowledge-index.json: domains must be an array")
            else:
                ids: set[str] = set()
                indexed_dirs: set[str] = set()
                for item in domains:
                    if not isinstance(item, dict):
                        fail(errors, "knowledge-index.json: each domain must be an object")
                        continue
                    domain_id = str(item.get("id", "")).strip()
                    path_text = str(item.get("path", "")).strip()
                    router_text = str(item.get("router", "")).strip()
                    if not domain_id or domain_id in ids:
                        fail(errors, f"knowledge-index.json: missing/duplicate domain id -> {domain_id!r}")
                    ids.add(domain_id)
                    if path_text:
                        indexed_dirs.add(path_text)
                        if not (ROOT / path_text).is_dir():
                            fail(errors, f"knowledge-index.json: missing domain path -> {path_text}")
                    if router_text and not (ROOT / router_text).is_file():
                        fail(errors, f"knowledge-index.json: missing router -> {router_text}")

                knowledge_root = ROOT / "knowledge"
                actual_dirs = {
                    str(path.relative_to(ROOT))
                    for path in knowledge_root.iterdir()
                    if path.is_dir()
                }
                if indexed_dirs != actual_dirs:
                    missing = sorted(actual_dirs - indexed_dirs)
                    stale = sorted(indexed_dirs - actual_dirs)
                    if missing:
                        fail(errors, f"knowledge-index.json: unindexed top-level domains -> {missing}")
                    if stale:
                        fail(errors, f"knowledge-index.json: stale domain paths -> {stale}")

    if not standards_index.exists():
        fail(errors, "Missing indexes/standards-index.json")
    else:
        data = load_json(standards_index, errors)
        if isinstance(data, dict):
            standards = data.get("standards", [])
            if not isinstance(standards, list):
                fail(errors, "standards-index.json: standards must be an array")
            else:
                ids: set[str] = set()
                indexed_files: set[str] = set()
                for item in standards:
                    if not isinstance(item, dict):
                        fail(errors, "standards-index.json: each standard must be an object")
                        continue
                    standard_id = str(item.get("id", "")).strip()
                    path_text = str(item.get("path", "")).strip()
                    if not standard_id or standard_id in ids:
                        fail(errors, f"standards-index.json: missing/duplicate standard id -> {standard_id!r}")
                    ids.add(standard_id)
                    if not path_text or not (ROOT / path_text).is_file():
                        fail(errors, f"standards-index.json: missing dossier -> {path_text}")
                    else:
                        indexed_files.add(path_text)

                standards_root = ROOT / "references" / "standards"
                actual_files = {
                    str(path.relative_to(ROOT))
                    for path in standards_root.glob("*.md")
                }
                if indexed_files != actual_files:
                    missing = sorted(actual_files - indexed_files)
                    stale = sorted(indexed_files - actual_files)
                    if missing:
                        fail(errors, f"standards-index.json: unindexed dossiers -> {missing}")
                    if stale:
                        fail(errors, f"standards-index.json: stale dossier paths -> {stale}")


def normalize_human_heading(heading: str) -> str:
    compact = re.sub(r"[*_]", "", heading).strip()
    compact = re.sub(r"^(?:\d+\.|[A-Z]\.)\s+", "", compact)
    return compact


def language_heading_allowed(heading: str) -> bool:
    compact = normalize_human_heading(heading)
    return any(pattern.fullmatch(compact) for pattern in LANGUAGE_HEADING_ALLOWLIST)


def language_prefix_allowed(heading: str) -> bool:
    compact = normalize_human_heading(heading)
    return any(pattern.match(compact) for pattern in LANGUAGE_PREFIX_ALLOWLIST)


def heading_is_zh_tw_first(heading: str) -> bool:
    compact = normalize_human_heading(heading)
    if language_heading_allowed(compact):
        return True

    cjk = CJK_RE.search(compact)
    if not cjk:
        return False

    latin = LATIN_RE.search(compact)
    if not latin:
        return True

    if cjk.start() < latin.start():
        return True

    return language_prefix_allowed(compact)


def validate_language_policy(errors: list[str]) -> None:
    for path in sorted(ROOT.rglob("*.md")):
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
                    "Temporary language fallback heading is not allowed: "
                    f"{path.relative_to(ROOT)}:{line_no} -> {heading}",
                )
                continue

            if heading_is_zh_tw_first(heading):
                continue

            fail(
                errors,
                "Human-facing heading must be zh-TW-first per LANGUAGE.md: "
                f"{path.relative_to(ROOT)}:{line_no} -> {heading}",
            )


def main() -> int:
    errors: list[str] = []
    validate_json(errors)
    validate_frontmatter(errors)
    validate_markdown_links(errors)
    validate_public_reference_policy(errors)
    validate_architecture(errors)
    validate_indexes(errors)
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
