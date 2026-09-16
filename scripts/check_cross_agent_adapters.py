#!/usr/bin/env python3
"""Validate thin cross-agent bootstrap adapters without granting execution authority."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CROSS_AGENT_ADAPTERS = {
    "CLAUDE.md": "Claude Code",
    "GEMINI.md": "Gemini CLI",
    ".github/copilot-instructions.md": "GitHub Copilot",
}
REQUIRED_POINTERS = ("`CHAT_INIT.md`", "`AGENTS.md`")
REQUIRED_PHRASES = (
    "不是第二份治理文件",
    "compatibility handoff，不形成平行 authority",
    "不會改變本 repository 的 `Project AI mode: ChatGPT-Only`",
    "不會讓此 host 自動成為 canonical executor",
    "不代表 task authorization、repository write authority、runtime execution authority、credential／deployment authority 或 completion evidence",
    "current canonical authority 為準",
)
MAX_LINES = 28


@dataclass(frozen=True)
class Finding:
    level: str
    code: str
    message: str


def validate(root: Path = ROOT) -> list[Finding]:
    findings: list[Finding] = []
    texts: dict[str, str] = {}

    for relative, host in CROSS_AGENT_ADAPTERS.items():
        path = root / relative
        if not path.is_file():
            findings.append(Finding("FAIL", "CROSS_AGENT_ADAPTER_MISSING", f"missing {relative}"))
            continue

        text = path.read_text(encoding="utf-8")
        texts[relative] = text

        if host not in text:
            findings.append(Finding("FAIL", "CROSS_AGENT_ADAPTER_HOST", f"{relative}: host identity missing: {host}"))

        for pointer in REQUIRED_POINTERS:
            if pointer not in text:
                findings.append(
                    Finding("FAIL", "CROSS_AGENT_ADAPTER_POINTER", f"{relative}: canonical pointer missing: {pointer}")
                )

        for phrase in REQUIRED_PHRASES:
            if phrase not in text:
                findings.append(
                    Finding("FAIL", "CROSS_AGENT_ADAPTER_AUTHORITY", f"{relative}: authority boundary missing: {phrase}")
                )

        if "```" in text or "~~~" in text:
            findings.append(
                Finding("FAIL", "CROSS_AGENT_ADAPTER_FENCE", f"{relative}: thin adapter must not contain fenced blocks")
            )

        if len(text.splitlines()) > MAX_LINES:
            findings.append(
                Finding(
                    "FAIL",
                    "CROSS_AGENT_ADAPTER_SIZE",
                    f"{relative}: {len(text.splitlines())} lines exceeds thin-adapter limit {MAX_LINES}",
                )
            )

    if len(texts) == len(CROSS_AGENT_ADAPTERS):
        normalized = [
            texts[relative].replace(host, "<HOST>")
            for relative, host in CROSS_AGENT_ADAPTERS.items()
        ]
        if len(set(normalized)) != 1:
            findings.append(
                Finding(
                    "FAIL",
                    "CROSS_AGENT_ADAPTER_DRIFT",
                    "adapter bodies must remain identical except for host identity",
                )
            )

    return findings


def main() -> int:
    findings = validate(ROOT)
    for finding in findings:
        print(f"{finding.level} {finding.code}: {finding.message}")

    fails = sum(item.level == "FAIL" for item in findings)
    print(f"Cross-agent adapter check: {fails} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
