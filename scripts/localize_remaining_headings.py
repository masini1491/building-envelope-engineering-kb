#!/usr/bin/env python3
"""Second-pass localization for remaining pure-English Markdown headings."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CJK_RE = re.compile(r"[\u3400-\u9fff]")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

EXACT = {
    "Post-installed anchors": "後置式錨栓（Post-installed anchors）",
    "Curtain-wall design routing": "帷幕牆設計 routing",
    "Curtain wall / glazed wall thermal path": "帷幕牆／玻璃外牆熱傳路徑",
    "Condensation logic": "結露判斷邏輯",
    "Thermal bridge guard": "熱橋防呆",
    "Test vs calculation": "試驗與計算的區分",
    "Sandwich-panel mechanical test family": "夾芯板機械性能試驗族群",
    "Panel-level structural verification": "面板層級結構驗證",
    "Fire-test applicability guard": "防火試驗適用性防呆",
    "Exterior-wall assembly fire testing": "外牆組件防火試驗",
    "Substitution review": "替代審查",
    "Load path first": "荷載路徑優先",
    "Geometry model": "幾何模型",
    "Material model": "材料模型",
    "Analysis outputs": "分析輸出",
    "Serviceability vs strength": "服務性與強度",
    "Local peaks": "局部峰值",
    "Buckling / geometric nonlinearity": "挫屈／幾何非線性",
    "Flatness / oil canning guard": "平整度／oil canning 防呆",
    "Load transfer": "荷載傳遞",
    "Discrete fasteners": "離散緊件",
    "Adhesive / bonded interface": "黏著／膠合介面",
    "Welded connection": "焊接連接",
    "Connector spacing": "連接件間距",
    "FEA representation": "FEA 表示方式",
    "Geometry": "幾何",
    "Elements": "元素類型",
    "Material": "材料",
    "Boundary conditions": "邊界條件",
    "Interface assumptions": "介面假設",
    "Mesh convergence": "網格收斂",
    "Stress result selection": "應力結果選取",
    "Linear vs nonlinear": "線性與非線性",
    "Linear static": "線性靜力",
    "Geometric nonlinear": "幾何非線性",
    "Buckling": "挫屈",
    "Connection modeling": "連接建模",
    "Reactions": "反力",
    "Sanity checks": "合理性檢查（Sanity checks）",
    "Reporting minimum": "報告最低要求",
    "Modeling choices": "建模選擇",
    "Composite-action guard": "複合作用（Composite action）防呆",
    "Stiffener demand": "補強材需求",
    "End condition": "端部條件",
    "Spacing / load-sharing": "間距／荷載分配",
    "Current editions（2026-09-02）": "現行版本（2026-09-02）",
    "Taiwan cross-reference": "台灣交叉對照",
    "Engineering comparison": "工程比較",
    "Taiwan practice observation": "台灣工程實務觀察",
    "Flatness / oil canning concern": "平整度／oil canning 議題",
    "Recommended substitution review": "建議替代審查",
    "Governing standard": "適用標準",
    "Assembly-specific principle": "組件特定原則",
    "Movement / construction tolerance": "位移／施工公差",
    "Curtain-wall coordination": "帷幕牆整合協調",
    "Exterior-wall fire testing distinction": "外牆防火試驗區分",
    "Core ASTM standards": "核心 ASTM 標準",
    "Engineering routing": "工程 routing",
    "Input checklist": "輸入檢核表",
    "Engineering guard": "工程防呆",
    "Serviceability / edge clearance": "服務性／邊緣淨空",
    "Failure probability / project criteria": "破壞機率／專案判定基準",
    "Appearance / distortion guard": "外觀／變形防呆",
    "1. Sash / vent structural response": "1. 窗扇／vent 結構反應",
    "2. Hardware demand": "2. 五金需求",
    "3. Fastener / local extrusion": "3. 緊件／鋁擠型局部行為",
    "4. Whole-product performance": "4. 整體產品性能",
    "Generic load path": "一般荷載路徑",
    "Thickness and movement": "厚度與位移",
    "Dead load": "自重",
    "Sources / routing": "來源／routing",
    "Local-section model": "局部截面模型",
    "Bearing": "承壓（Bearing）",
    "Local wall bending": "局部壁板彎曲",
    "Screw pull-out / thread stripping": "螺絲抗拔／螺紋剝離",
    "Thread engagement": "螺紋咬合（Thread engagement）",
    "Thin-wall and geometry guard": "薄壁／幾何防呆",
    "HAZ / welding guard": "熱影響區（HAZ）／焊接防呆",
    "Pull-out variables": "抗拔影響變數",
    "Screw pull-out workflow": "螺絲抗拔流程",
    "Eccentric group interaction": "偏心群組交互作用",
    "1. Weld-group mechanics": "1. 焊道群力學",
    "2. Weld / base-metal strength": "2. 焊道／母材強度",
    "Primary sources / routing": "主要來源／routing",
    "Public sources / routing": "公開來源／routing",
    "Mullion": "直料（Mullion）",
    "Transom": "橫料（Transom）",
    "Data schemas": "資料 schema",
    "Status model": "狀態模型",
    "Calculation trace": "計算追溯",
    "Inputs": "輸入",
    "Derived values": "衍生值",
    "Method": "方法",
    "Result": "結果",
    "Auditability rule": "可稽核性規則",
    "Data integrity": "資料完整性",
    "Design Pressure": "設計風壓（Design Pressure）",
    "Test Pressure": "試驗壓力（Test Pressure）",
    "Deflection → Required I": "撓度 → 所需 I",
    "Bending strength → Required S": "彎曲強度 → 所需 S",
    "Actual verification": "實際截面驗證",
    "Governing envelope": "控制包絡",
    "Male / Female mullion composite action": "公／母直料複合作用（Composite action）",
    "Axis definition": "座標軸定義",
    "Status recommendation": "狀態建議",
    "Factor ledger": "係數台帳（Factor ledger）",
    "A. Demand reconciliation": "A. 需求對帳",
    "B. Capacity reconciliation": "B. 承載力對帳",
    "C. Result reconciliation": "C. 結果對帳",
    "1. Unexplained multiplier": "1. 無法解釋的倍率",
    "2. Double counting": "2. 重複計入（Double counting）",
    "3. Omitted required factor": "3. 漏掉必要係數",
    "4. Wrong-side application": "4. 係數套用側錯誤",
    "5. Ratio inversion": "5. 比值顛倒",
    "6. Design / test factor contamination": "6. 設計／試驗係數混用",
    "7. Mixed design philosophies": "7. 混用設計哲學",
    "8. Hidden factor inside spreadsheet / software": "8. 試算表／軟體內隱藏係數",
    "9. Convenient rounding / clipping": "9. 有利的四捨五入／截斷",
    "10. Factor changed between similar checks": "10. 相似檢核間係數不一致",
    "Machine-readable routing": "機器可讀 routing",
    "Design pressure ≠ test pressure": "設計風壓 ≠ 試驗壓力",
    "9. Performance test / acceptance": "9. 性能試驗／驗收",
    "10. Material / connection-specific requirements": "10. 材料／連接特定要求",
    "Project Design Basis Sheet": "專案設計基準表（Project Design Basis Sheet）",
    "Spec → Calc Coverage Matrix": "規範 → 計算涵蓋矩陣",
    "Engineering result": "工程結果",
    "Specification compliance": "規範符合性",
    "Conflict handling": "衝突處理",
    "Recommended extraction statuses": "建議抽取狀態",
    "1. Design basis": "1. 設計基準",
    "2. Design factor / safety factor / hidden multiplier audit": "2. 設計係數／安全係數／隱藏倍率稽核",
    "3. Geometry / system definition": "3. 幾何／系統定義",
    "4. Load sources": "4. 荷載來源",
    "5. Load generation": "5. 荷載生成",
    "6. Framing model": "6. Framing 模型",
    "7. Member global response": "7. 構件整體反應",
    "8. Glass / structural glass": "8. 玻璃／結構玻璃",
    "9. Transom / dead-load path": "9. 橫料／自重荷載路徑",
    "10. Fasteners": "10. 緊件",
    "11. Welds": "11. 焊道",
    "12. Brackets / local sections / anchors": "12. 支架／局部截面／錨栓",
    "13. Metal panels / stiffeners": "13. 金屬面板／補強材",
    "14. Operable windows / vents": "14. 活動窗／vents",
    "15. Seismic movement / thermal movement": "15. 地震位移／熱位移",
    "16. Test / analysis relationship": "16. 試驗／分析關係",
    "17. Calculation trace": "17. 計算追溯",
    "18. Final coverage review": "18. 最終涵蓋範圍審查",
    "1. Force path": "1. 受力路徑",
    "2. Movement path": "2. 位移路徑",
    "Connection demand": "連接需求",
    "Different component categories": "不同構件分類",
    "Movement must remain compatible": "位移必須保持相容",
    "Output requirements": "輸出要求",
    "Primary-source routing": "一手來源 routing",
    "Movement chain": "位移傳遞鏈",
    "Structural-model inputs": "結構模型輸入",
    "Relative movement, not only absolute movement": "相對位移，而非僅絕對位移",
    "Drift vs member deflection": "層間變位與構件撓度",
    "Stack joint / splice": "Stack joint／splice",
    "Glass edge / sealant routing": "玻璃邊緣／sealant routing",
    "Test routing": "試驗 routing",
    "Purpose": "目的",
    "Component-force structure": "構件地震力架構",
    "Height amplification matters": "高度放大效應很重要",
    "Component category selection": "構件分類選擇",
    "Weight definition guard": "重量定義防呆",
    "Force direction": "作用力方向",
    "Load combinations": "荷載組合",
    "Repository usage": "Repository 使用方式",
    "Related pages": "相關頁面",
    "Global model guard": "全域模型防呆",
    "Effective section properties": "等效截面性質",
    "Buckling / stability": "挫屈／穩定性",
    "Connection interaction": "連接交互作用",
    "Design routing": "設計 routing",
    "Stick system": "直橫料式系統（Stick system）",
    "Unitized system": "單元式系統（Unitized system）",
    "Semi-unitized / hybrid": "半單元式／混合式系統",
    "Structural comparison guard": "結構比較防呆",
    "Water management": "水管理",
    "Testing": "試驗",
}

# Machine-readable identifiers and standard/material-only headings may remain English.
ALLOW = [
    re.compile(r"^(?:ASTM|CNS|AAMA|FGIA|ISO|ACI|AISC|AWS|NAFS|FEA)(?:[ /+&.0-9A-Z_-]*)$"),
    re.compile(r"^(?:A[24]-\d{2}|\d{4}-[HT]\d+)$"),
    re.compile(r"^(?:PASS|WARNING|FAIL|INCOMPLETE|NOT_APPLICABLE)$"),
    re.compile(r"^\d+\.\s+`[a-z0-9_]+`$"),
]

PROSE_REPLACEMENTS = {
    "Façade failure modes often cascade rather than occur independently.": "建築外殼的破壞模式常呈連鎖發展，而不是彼此完全獨立。",
    "4. `A_w / I_x / I_y / I_xy / J` as applicable": "4. 依適用性列出 `A_w / I_x / I_y / I_xy / J`",
}


def has_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text))


def allowed(text: str) -> bool:
    compact = re.sub(r"[*_]", "", text).strip()
    return any(p.fullmatch(compact) for p in ALLOW)


def main() -> int:
    changed_files = 0
    unresolved: list[str] = []
    for path in sorted((ROOT / "knowledge").rglob("*.md")):
        original = path.read_text(encoding="utf-8")
        lines = original.splitlines()
        out: list[str] = []
        changed = False
        in_fence = False
        frontmatter = bool(lines and lines[0] == "---")
        frontmatter_done = not frontmatter
        for line_no, line in enumerate(lines, 1):
            if frontmatter and not frontmatter_done:
                out.append(line)
                if line_no > 1 and line == "---":
                    frontmatter_done = True
                continue
            if line.lstrip().startswith(("```", "~~~")):
                in_fence = not in_fence
                out.append(line)
                continue
            if in_fence:
                out.append(line)
                continue
            if line in PROSE_REPLACEMENTS:
                out.append(PROSE_REPLACEMENTS[line])
                changed = True
                continue
            m = HEADING_RE.match(line)
            if not m:
                out.append(line)
                continue
            hashes, heading = m.groups()
            if has_cjk(heading) or allowed(heading):
                out.append(line)
                continue
            translated = EXACT.get(heading)
            if translated is None:
                # Last-resort interface marker: preserve the technical English phrase
                # verbatim while making the human-facing heading explicitly Chinese.
                translated = f"工程主題：{heading}"
                unresolved.append(f"{path.relative_to(ROOT)}:{line_no}: {heading}")
            out.append(f"{hashes} {translated}")
            changed = True
        new = "\n".join(out) + ("\n" if original.endswith("\n") else "")
        if changed:
            path.write_text(new, encoding="utf-8")
            changed_files += 1
    print(f"Second-pass changed files: {changed_files}")
    print(f"Fallback-prefixed headings requiring future terminology refinement: {len(unresolved)}")
    for item in unresolved:
        print(f"  FALLBACK {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
