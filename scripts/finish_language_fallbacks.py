#!/usr/bin/env python3
"""Replace the final temporary `工程主題：...` headings with reviewed zh-TW headings."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = {
    "## 工程主題：Test vs analysis": "## 試驗與分析的區分",
    "### 工程主題：3003-H14 → 3004-H12": "### 3003-H14 → 3004-H12 材料轉換觀察",
    "## 工程主題：Current version snapshot（2026-09-02）": "## 現行版本快照（2026-09-02）",
    "## 工程主題：1. Fastener-group centroid": "## 1. 緊件群形心（Fastener-group centroid）",
    "## 工程主題：2. Direct force": "## 2. 直接力（Direct force）",
    "## 工程主題：3. In-plane eccentric shear / torsion": "## 3. 面內偏心剪力／扭矩",
    "## 工程主題：4. Eccentric tension / overturning": "## 4. 偏心拉力／傾覆作用",
    "## 工程主題：5. Combined tension + shear": "## 5. 拉力＋剪力組合",
    "## 工程主題：6. Connected-material checks": "## 6. 被連接材料檢核",
    "## 工程主題：7. Screw-group specific guard": "## 7. 螺絲群特定防呆",
    "## 工程主題：8. Recommended calculation output": "## 8. 建議計算輸出",
    "### 工程主題：1. Document control / authority": "### 1. 文件控制／權威性",
    "## 工程主題：2. Design responsibility / required scope": "## 2. 設計責任／必要範圍",
    "## 工程主題：3. Governing references": "## 3. 適用參考依據",
    "## 工程主題：4. Loads / actions": "## 4. 荷載／作用",
    "## 工程主題：5. Strength / safety criteria": "## 5. 強度／安全判定基準",
    "## 工程主題：6. Serviceability / movement criteria": "## 6. 服務性／位移判定基準",
    "## 工程主題：7. Required calculation coverage": "## 7. 必要計算涵蓋範圍",
    "## 工程主題：8. Required calculation trace / submittal evidence": "## 8. 必要計算追溯／送審證據",
    "## 工程主題：Bite／thickness routing": "## Bite／厚度（thickness）設計 routing",
    "## 工程主題：Stack joint／splice": "## Stack joint／splice 位移與接頭行為",
}


def main() -> int:
    changed_files = 0
    remaining = []
    for path in sorted((ROOT / "knowledge").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        new = text
        for old, replacement in REPLACEMENTS.items():
            new = new.replace(old, replacement)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed_files += 1
        if "工程主題：" in new:
            for line_no, line in enumerate(new.splitlines(), 1):
                if line.startswith("#") and "工程主題：" in line:
                    remaining.append(f"{path.relative_to(ROOT)}:{line_no}: {line}")
    print(f"Final fallback cleanup changed files: {changed_files}")
    print(f"Remaining fallback headings: {len(remaining)}")
    for item in remaining:
        print(f"  {item}")
    return 1 if remaining else 0


if __name__ == "__main__":
    raise SystemExit(main())
