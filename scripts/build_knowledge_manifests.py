#!/usr/bin/env python3
"""Build/check sharded page-level knowledge routing manifests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PURPOSE = (
    "Page-level routing metadata only. Match slug/path, then open the target page "
    "for engineering content and verification status."
)


def build_domain_manifest(root: Path, domain: str) -> dict[str, object]:
    domain_root = root / "knowledge" / domain
    pages: list[dict[str, str]] = []

    for path in sorted(domain_root.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        under_domain = path.relative_to(domain_root)
        is_router = path.name == "README.md"
        slug = path.parent.name if is_router else path.stem

        item: dict[str, str] = {
            "path": rel,
            "slug": slug,
            "kind": "router" if is_router else "page",
        }
        if under_domain.parent != Path("."):
            item["section"] = under_domain.parent.as_posix()
        pages.append(item)

    return {
        "schema_version": 1,
        "domain": domain,
        "purpose": PURPOSE,
        "pages": pages,
    }


def expected_manifests(root: Path = ROOT) -> dict[str, dict[str, object]]:
    knowledge_root = root / "knowledge"
    result: dict[str, dict[str, object]] = {}

    for path in sorted(knowledge_root.iterdir()):
        if not path.is_dir():
            continue
        domain = path.name
        rel = f"indexes/knowledge-pages/{domain}.json"
        result[rel] = build_domain_manifest(root, domain)

    return result


def render_manifest(data: dict[str, object]) -> str:
    pages = data["pages"]
    if not isinstance(pages, list):
        raise TypeError("pages must be a list")

    lines = [
        "{",
        '  "schema_version": 1,',
        f'  "domain": {json.dumps(data["domain"], ensure_ascii=False)},',
        f'  "purpose": {json.dumps(data["purpose"], ensure_ascii=False)},',
        '  "pages": [',
    ]
    for index, item in enumerate(pages):
        suffix = "," if index < len(pages) - 1 else ""
        lines.append(
            "    "
            + json.dumps(item, ensure_ascii=False, separators=(",", ":"))
            + suffix
        )
    lines.extend(["  ]", "}"])
    return "\n".join(lines) + "\n"


def load_knowledge_index(root: Path) -> dict[str, object] | None:
    path = root / "indexes" / "knowledge-index.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None
    return data if isinstance(data, dict) else None


def check(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    expected = expected_manifests(root)
    manifest_root = root / "indexes" / "knowledge-pages"

    for rel, data in expected.items():
        path = root / rel
        expected_text = render_manifest(data)
        if not path.exists():
            errors.append(f"Missing generated knowledge manifest: {rel}")
            continue
        actual = path.read_text(encoding="utf-8")
        if actual != expected_text:
            errors.append(
                f"Stale generated knowledge manifest: {rel} "
                "(run: python scripts/build_knowledge_manifests.py)"
            )

    if manifest_root.exists():
        expected_paths = set(expected)
        actual_paths = {
            path.relative_to(root).as_posix()
            for path in manifest_root.glob("*.json")
        }
        for rel in sorted(actual_paths - expected_paths):
            errors.append(f"Stale generated knowledge manifest file: {rel}")

    index_data = load_knowledge_index(root)
    if index_data is None:
        errors.append("Cannot validate manifest routing: indexes/knowledge-index.json is missing/invalid")
        return errors

    domains = index_data.get("domains", [])
    if not isinstance(domains, list):
        errors.append("Cannot validate manifest routing: knowledge-index domains must be an array")
        return errors

    indexed_manifests: dict[str, str] = {}
    for item in domains:
        if not isinstance(item, dict):
            continue
        domain = str(item.get("id", "")).strip()
        manifest = str(item.get("manifest", "")).strip()
        if domain:
            indexed_manifests[domain] = manifest

    for rel, data in expected.items():
        domain = str(data["domain"])
        actual_rel = indexed_manifests.get(domain, "")
        if actual_rel != rel:
            errors.append(
                f"knowledge-index manifest mismatch: {domain!r} -> "
                f"{actual_rel!r}, expected {rel!r}"
            )

    extra_domains = sorted(set(indexed_manifests) - {str(data["domain"]) for data in expected.values()})
    for domain in extra_domains:
        errors.append(f"knowledge-index manifest points to non-existent domain: {domain!r}")

    return errors


def write(root: Path = ROOT) -> None:
    manifest_root = root / "indexes" / "knowledge-pages"
    manifest_root.mkdir(parents=True, exist_ok=True)
    expected = expected_manifests(root)

    for rel, data in expected.items():
        path = root / rel
        path.write_text(render_manifest(data), encoding="utf-8")

    expected_paths = set(expected)
    for path in manifest_root.glob("*.json"):
        rel = path.relative_to(root).as_posix()
        if rel not in expected_paths:
            path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if committed knowledge manifests do not match current knowledge paths/index routing.",
    )
    args = parser.parse_args()

    if args.check:
        errors = check(ROOT)
        if errors:
            for item in errors:
                print(f"- {item}")
            return 1
        print("Knowledge page manifests are current.")
        return 0

    write(ROOT)
    print("Knowledge page manifests updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
