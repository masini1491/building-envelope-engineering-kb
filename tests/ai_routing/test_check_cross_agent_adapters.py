from __future__ import annotations

import importlib.util
import tempfile
import unittest
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "check_cross_agent_adapters",
    ROOT / "scripts" / "check_cross_agent_adapters.py",
)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class CrossAgentAdapterTests(unittest.TestCase):
    def make_root(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        for relative in validator.CROSS_AGENT_ADAPTERS:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            source = (ROOT / relative).read_text(encoding="utf-8")
            path.write_text(source, encoding="utf-8")
        return root

    def test_current_adapters_pass(self) -> None:
        self.assertEqual([], validator.validate(self.make_root()))

    def test_missing_adapter_fails(self) -> None:
        root = self.make_root()
        (root / "GEMINI.md").unlink()
        findings = validator.validate(root)
        self.assertTrue(any(item.code == "CROSS_AGENT_ADAPTER_MISSING" for item in findings))

    def test_authority_boundary_is_required(self) -> None:
        root = self.make_root()
        path = root / "CLAUDE.md"
        text = path.read_text(encoding="utf-8").replace(
            "不會讓此 host 自動成為 canonical executor",
            "提供相容性",
        )
        path.write_text(text, encoding="utf-8")
        findings = validator.validate(root)
        self.assertTrue(any(item.code == "CROSS_AGENT_ADAPTER_AUTHORITY" for item in findings))

    def test_claude_host_specific_contract_is_required(self) -> None:
        root = self.make_root()
        path = root / "CLAUDE.md"
        text = path.read_text(encoding="utf-8").replace(
            "一般 Claude Code task 應先由 `CHAT_INIT.md` 進入最低充分 routing",
            "一般 Claude Code task 依既有規則處理",
        )
        path.write_text(text, encoding="utf-8")
        findings = validator.validate(root)
        self.assertTrue(any(item.code == "CROSS_AGENT_ADAPTER_HOST_CONTRACT" for item in findings))


if __name__ == "__main__":
    unittest.main()
