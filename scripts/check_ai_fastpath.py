#!/usr/bin/env python3
"""Deterministic checks for AI routing fast-path integrity and growth signals."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

INDEX_ALLOWED_KEYS = {"schema_version", "purpose", "domains"}
DOMAIN_ALLOWED_KEYS = {"id", "path", "entrypoint", "router", "aliases", "manifest"}
MANIFEST_ALLOWED_KEYS = {"schema_version", "domain", "purpose", "pages"}
PAGE_ALLOWED_KEYS = {"path", "slug", "kind", "section"}

# Review signals calibrated to this KB's current routing surfaces. They are warnings,
# not universal correctness limits.
SIZE_REVIEW_SIGNALS = {
    "CHAT_INIT.md": 16 * 1024,
    "indexes/knowledge-index.json": 12 * 1024,
}
MANIFEST_SIZE_REVIEW = 16 * 1024


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    message: str


def add(findings: list[Finding], level: str, code: str, message: str) -> None:
    findings.append(Finding(level, code, message))


def load_json(path: Path, root: Path, findings: list[Finding], code: str) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        add(findings, "FAIL", code, f"{path.relative_to(root)}: {exc}")
        return None


def validate(root: Path) -> list[Finding]:
    findings: list[Finding] = []

    chat_init = root / "CHAT_INIT.md"
    index_path = root / "indexes" / "knowledge-index.json"
    manifest_root = root / "indexes" / "knowledge-pages"

    for path in (chat_init, index_path, manifest_root):
        if not path.exists():
            add(findings, "FAIL", "FASTPATH_REQUIRED_PATH", f"missing {path.relative_to(root)}")

    if not index_path.is_file():
        return findings

    index = load_json(index_path, root, findings, "FASTPATH_INDEX_JSON")
    if not isinstance(index, dict):
        return findings

    extra_index_keys = sorted(set(index) - INDEX_ALLOWED_KEYS)
    if extra_index_keys:
        add(
            findings,
            "FAIL",
            "FASTPATH_INDEX_AUTHORITY_SURFACE",
            f"knowledge-index contains non-routing top-level keys: {extra_index_keys}",
        )

    if index.get("schema_version") != 2:
        add(findings, "FAIL", "FASTPATH_INDEX_SCHEMA", "knowledge-index schema_version must be 2")

    domains = index.get("domains")
    if not isinstance(domains, list) or not domains:
        add(findings, "FAIL", "FASTPATH_DOMAINS", "knowledge-index domains must be a non-empty array")
        return findings

    seen_domain_ids: set[str] = set()
    seen_aliases: dict[str, str] = {}
    seen_manifest_paths: set[str] = set()
    seen_page_paths: set[str] = set()

    for raw_domain in domains:
        if not isinstance(raw_domain, dict):
            add(findings, "FAIL", "FASTPATH_DOMAIN_OBJECT", "each domain must be an object")
            continue

        extra_domain_keys = sorted(set(raw_domain) - DOMAIN_ALLOWED_KEYS)
        if extra_domain_keys:
            add(
                findings,
                "FAIL",
                "FASTPATH_DOMAIN_AUTHORITY_SURFACE",
                f"domain contains non-routing keys: {extra_domain_keys}",
            )

        domain_id = str(raw_domain.get("id", "")).strip()
        domain_path = str(raw_domain.get("path", "")).strip()
        entrypoint = str(raw_domain.get("entrypoint", "")).strip()
        router = str(raw_domain.get("router", "")).strip()
        manifest_rel = str(raw_domain.get("manifest", "")).strip()
        aliases = raw_domain.get("aliases", [])

        if not domain_id or domain_id in seen_domain_ids:
            add(findings, "FAIL", "FASTPATH_DOMAIN_ID", f"missing/duplicate domain id: {domain_id!r}")
            continue
        seen_domain_ids.add(domain_id)

        if not isinstance(aliases, list) or not aliases:
            add(findings, "FAIL", "FASTPATH_ALIAS_LIST", f"{domain_id}: aliases must be non-empty")
        else:
            for alias in aliases:
                if not isinstance(alias, str) or not alias.strip():
                    add(findings, "FAIL", "FASTPATH_ALIAS_VALUE", f"{domain_id}: empty/non-string alias")
                    continue
                key = alias.strip().casefold()
                owner = seen_aliases.get(key)
                if owner and owner != domain_id:
                    add(
                        findings,
                        "WARN",
                        "FASTPATH_ALIAS_COLLISION",
                        f"alias {alias!r} appears in both {owner!r} and {domain_id!r}",
                    )
                else:
                    seen_aliases[key] = domain_id

        expected_manifest = f"indexes/knowledge-pages/{domain_id}.json"
        if manifest_rel != expected_manifest:
            add(
                findings,
                "FAIL",
                "FASTPATH_MANIFEST_ROUTE",
                f"{domain_id}: manifest={manifest_rel!r}, expected {expected_manifest!r}",
            )
        if manifest_rel in seen_manifest_paths:
            add(findings, "FAIL", "FASTPATH_MANIFEST_DUPLICATE", f"duplicate manifest route: {manifest_rel}")
        seen_manifest_paths.add(manifest_rel)

        manifest_path = root / manifest_rel
        if not manifest_path.is_file():
            add(findings, "FAIL", "FASTPATH_MANIFEST_MISSING", f"{domain_id}: missing {manifest_rel}")
            continue

        manifest = load_json(manifest_path, root, findings, "FASTPATH_MANIFEST_JSON")
        if not isinstance(manifest, dict):
            continue

        extra_manifest_keys = sorted(set(manifest) - MANIFEST_ALLOWED_KEYS)
        if extra_manifest_keys:
            add(
                findings,
                "FAIL",
                "FASTPATH_MANIFEST_AUTHORITY_SURFACE",
                f"{manifest_rel}: non-routing top-level keys {extra_manifest_keys}",
            )
        if manifest.get("schema_version") != 1:
            add(findings, "FAIL", "FASTPATH_MANIFEST_SCHEMA", f"{manifest_rel}: schema_version must be 1")
        if manifest.get("domain") != domain_id:
            add(
                findings,
                "FAIL",
                "FASTPATH_MANIFEST_DOMAIN",
                f"{manifest_rel}: domain={manifest.get('domain')!r}, expected {domain_id!r}",
            )

        pages = manifest.get("pages")
        if not isinstance(pages, list) or not pages:
            add(findings, "FAIL", "FASTPATH_MANIFEST_PAGES", f"{manifest_rel}: pages must be non-empty")
            continue

        page_by_path: dict[str, dict[str, Any]] = {}
        seen_route_keys: set[tuple[str, str]] = set()

        for page in pages:
            if not isinstance(page, dict):
                add(findings, "FAIL", "FASTPATH_PAGE_OBJECT", f"{manifest_rel}: page must be object")
                continue

            extra_page_keys = sorted(set(page) - PAGE_ALLOWED_KEYS)
            if extra_page_keys:
                add(
                    findings,
                    "FAIL",
                    "FASTPATH_PAGE_AUTHORITY_SURFACE",
                    f"{manifest_rel}: page has non-routing keys {extra_page_keys}",
                )

            page_path = str(page.get("path", "")).strip()
            slug = str(page.get("slug", "")).strip()
            kind = str(page.get("kind", "")).strip()
            section = str(page.get("section", "")).strip()

            if not page_path or not slug or kind not in {"router", "page"}:
                add(
                    findings,
                    "FAIL",
                    "FASTPATH_PAGE_FIELDS",
                    f"{manifest_rel}: invalid page fields path={page_path!r}, slug={slug!r}, kind={kind!r}",
                )
                continue

            if domain_path and not page_path.startswith(domain_path + "/"):
                add(
                    findings,
                    "FAIL",
                    "FASTPATH_PAGE_DOMAIN",
                    f"{manifest_rel}: page outside domain path: {page_path}",
                )

            if not (root / page_path).is_file():
                add(findings, "FAIL", "FASTPATH_PAGE_TARGET", f"{manifest_rel}: missing target {page_path}")

            if page_path in seen_page_paths:
                add(findings, "FAIL", "FASTPATH_PAGE_DUPLICATE", f"page routed by multiple manifests: {page_path}")
            seen_page_paths.add(page_path)
            page_by_path[page_path] = page

            route_key = (section, slug)
            if route_key in seen_route_keys:
                add(
                    findings,
                    "FAIL",
                    "FASTPATH_SLUG_COLLISION",
                    f"{manifest_rel}: duplicate (section, slug) route {route_key!r}",
                )
            seen_route_keys.add(route_key)

        if entrypoint not in page_by_path:
            add(
                findings,
                "FAIL",
                "FASTPATH_ENTRYPOINT",
                f"{domain_id}: entrypoint is not present in its manifest: {entrypoint}",
            )

        if router:
            router_page = page_by_path.get(router)
            if not router_page or router_page.get("kind") != "router":
                add(
                    findings,
                    "FAIL",
                    "FASTPATH_ROUTER_KIND",
                    f"{domain_id}: declared router is missing or not kind=router: {router}",
                )
            if entrypoint != router:
                add(
                    findings,
                    "WARN",
                    "FASTPATH_ROUTER_HOP_REVIEW",
                    f"{domain_id}: router differs from entrypoint; review whether an extra routing hop is necessary",
                )

    if manifest_root.is_dir():
        indexed = {str(domain.get("manifest", "")).strip() for domain in domains if isinstance(domain, dict)}
        actual = {path.relative_to(root).as_posix() for path in manifest_root.glob("*.json")}
        for rel in sorted(actual - indexed):
            add(findings, "FAIL", "FASTPATH_MANIFEST_UNINDEXED", f"unindexed manifest: {rel}")

    for rel, limit in SIZE_REVIEW_SIGNALS.items():
        path = root / rel
        if path.is_file() and path.stat().st_size > limit:
            add(
                findings,
                "WARN",
                "FASTPATH_GROWTH_REVIEW",
                f"{rel} is {path.stat().st_size} bytes (> {limit}); review always-on retrieval cost",
            )

    if manifest_root.is_dir():
        for path in sorted(manifest_root.glob("*.json")):
            if path.stat().st_size > MANIFEST_SIZE_REVIEW:
                add(
                    findings,
                    "WARN",
                    "FASTPATH_MANIFEST_GROWTH_REVIEW",
                    f"{path.relative_to(root)} is {path.stat().st_size} bytes (> {MANIFEST_SIZE_REVIEW}); review routing cohesion",
                )

    return findings


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else ROOT
    required_root = root / "indexes" / "knowledge-index.json"
    if not required_root.exists():
        print(f"AI Fast Path Check: repository root not found: {root}", file=sys.stderr)
        return 2

    findings = validate(root)
    order = {"FAIL": 0, "WARN": 1}
    findings.sort(key=lambda finding: (order.get(finding.level, 9), finding.code, finding.message))

    for finding in findings:
        print(f"{finding.level} {finding.code}: {finding.message}")

    fails = sum(item.level == "FAIL" for item in findings)
    warns = sum(item.level == "WARN" for item in findings)
    print(f"AI Fast Path Check: {fails} FAIL, {warns} WARN")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
