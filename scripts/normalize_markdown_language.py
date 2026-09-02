#!/usr/bin/env python3
"""Normalize human-readable Markdown interfaces to Traditional Chinese (Taiwan).

This script is intentionally conservative: it translates repository-authored
headings and a small set of known English prose sentences, while preserving
standard names, identifiers, schema keys, formulas, paths, and code blocks.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CJK_RE = re.compile(r"[\u3400-\u9fff]")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
ENGLISH_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")

PATH_TITLES = {
    "knowledge/anchors/anchor-standards-baseline.md": "帷幕牆錨栓標準基線",
    "knowledge/building-physics/thermal-and-condensation-baseline.md": "建築外殼熱傳與結露基線",
    "knowledge/cladding/metal-composite-and-honeycomb-panels.md": "金屬複合板與蜂巢板基線",
    "knowledge/cladding/structural-analysis/README.md": "金屬板／補強材結構分析",
    "knowledge/cladding/structural-analysis/metal-panel-analysis.md": "金屬面板結構分析",
    "knowledge/cladding/structural-analysis/panel-to-stiffener-connection.md": "面板與補強材連接分析",
    "knowledge/cladding/structural-analysis/plate-fea-modeling.md": "板件有限元素分析建模方法",
    "knowledge/cladding/structural-analysis/stiffener-analysis.md": "補強材結構分析",
    "knowledge/corrosion-protection/hot-dip-galvanizing-astm-family.md": "熱浸鍍鋅 ASTM 標準族群",
    "knowledge/fasteners/stainless/iso-3506-a2-70-a2-90.md": "ISO 3506 不鏽鋼緊件 A2-70／A2-90 基線",
    "knowledge/finishes/aluminum-organic-coatings-aama-2603-2604-2605.md": "鋁材有機塗裝 AAMA 2603／2604／2605 基線",
    "knowledge/fire/perimeter-fire-barrier-and-joints.md": "帷幕外牆周邊防火阻隔與接縫",
    "knowledge/gaskets/elastomeric-gasket-baseline.md": "彈性體墊條基線",
    "knowledge/glazing/ASTM-E1300-design-routing.md": "ASTM E1300 建築玻璃耐荷重設計 routing",
    "knowledge/glazing/glass-standards-baseline.md": "建築玻璃標準基線",
    "knowledge/materials/steel/astm-a36.md": "ASTM A36/A36M 碳素結構鋼（Carbon Structural Steel）",
    "knowledge/operable-elements/hinge-lock-stay-connections.md": "活動窗 Hinge／Lock／Stay 連接設計方法",
    "knowledge/operable-elements/performance-and-life-cycle.md": "活動窗整窗性能與生命週期 routing",
    "knowledge/sealants/structural-silicone-bite-routing.md": "結構矽利康 bite／接縫幾何設計 routing",
    "knowledge/sealants/weatherseal-joint-design.md": "耐候密封（Weatherseal）接縫設計基線",
    "knowledge/structural-glass/README.md": "結構玻璃（Structural Glass）",
    "knowledge/structural-glass/glass-fin-design.md": "玻璃肋／玻璃直料設計（Glass Fin Design）",
    "knowledge/structural-glass/glass-to-glass-structural-silicone.md": "玻璃對玻璃結構矽利康（Glass-to-Glass Structural Silicone）",
    "knowledge/structural-glass/structural-glass-fea-modeling.md": "結構玻璃有限元素分析建模防呆",
    "knowledge/structural-glass/walkable-glass.md": "可步行結構玻璃（Walkable Glass）",
    "knowledge/structural-design/framing/continuous-mullion-analysis.md": "多跨直料（Continuous Mullion）結構分析方法",
    "knowledge/structural-design/framing/glass-edge-relative-deflection.md": "玻璃邊緣相對變形與 framing 相容性",
    "knowledge/structural-design/framing/splice-and-sleeve-modeling.md": "直料接頭／套筒（Splice／Sleeve）建模方法",
    "knowledge/structural-design/preliminary-sizing/calculation-status-and-traceability.md": "計算狀態與可追溯性",
    "knowledge/structural-design/preliminary-sizing/design-vs-test-pressure.md": "設計風壓（Design Pressure）與試驗壓力（Test Pressure）分流",
    "knowledge/structural-design/preliminary-sizing/required-section-properties.md": "所需截面性質初步尺寸評估",
    "knowledge/structural-design/preliminary-sizing/support-and-composite-action.md": "支承條件與複合作用（Composite Action）",
    "knowledge/structural-design/review/coverage-and-completeness.md": "結構計算涵蓋範圍／完整性狀態",
    "knowledge/structural-design/review/failure-mode-map.md": "建築外殼結構破壞模式圖（Failure-Mode Map）",
    "knowledge/structural-design/review/project-specification-extraction.md": "專案規範 → 結構設計基準抽取",
    "knowledge/structural-design/review/structural-calculation-review-checklist.md": "結構計算審查檢核表",
    "knowledge/structural-design/seismic/seismic-connection-load-path.md": "耐震連接荷載路徑",
    "knowledge/structural-design/seismic/seismic-movement-compatibility.md": "耐震位移相容性",
    "knowledge/structural-design/seismic/taiwan-facade-component-seismic-force.md": "台灣建築外殼構件地震力",
    "knowledge/systems/curtain-wall-system-types.md": "帷幕牆系統型式：直橫料式（Stick）／單元式（Unitized）／半單元式（Semi-Unitized）",
}

HEADING_MAP = {
    "Scope": "適用範圍",
    "Classification": "分類",
    "Building-envelope use": "建築外殼常見用途",
    "Governing material families": "適用材料標準",
    "Engineering notes": "工程備註",
    "Do not assume": "不可推論事項",
    "Sources": "來源",
    "Primary source": "主要來源",
    "Primary sources": "主要來源",
    "Primary / supporting source": "主要／輔助來源",
    "Primary / supporting sources": "主要／輔助來源",
    "Primary public sources": "主要公開來源",
    "Public sources": "公開來源",
    "Public-source routing": "公開來源 routing",
    "Current edition snapshot": "現行版本快照",
    "Current version snapshot": "現行版本快照",
    "Current standard routing": "現行標準 routing",
    "Current public standard routing": "現行公開標準 routing",
    "Current public standards baseline": "現行公開標準基線",
    "Current authority baseline": "現行權威來源基線",
    "Authority baseline": "權威來源基線",
    "Core standards": "核心標準",
    "Core standard": "核心標準",
    "Core routing": "核心 routing",
    "Routing": "相關頁面與 routing",
    "Related": "相關頁面",
    "Related knowledge": "相關知識",
    "Related knowledge to add": "後續待補知識",
    "Related standards / cross-reference": "相關標準／交叉對照",
    "Related public standards": "相關公開標準",
    "Related failure modes": "相關破壞模式",
    "Role": "角色",
    "Design workflow": "設計流程",
    "Recommended workflow": "建議流程",
    "Recommended calculation output": "建議計算輸出",
    "Recommended output": "建議輸出",
    "Recommended statuses": "建議狀態",
    "AI guard": "AI 防呆",
    "Design guard": "設計防呆",
    "Manufacturer-review guard": "製造商審查防呆",
    "Compatibility / staining / accessory notes": "相容性／污染／配件注意事項",
    "Project-specific verification": "專案特定驗證",
    "Product-form split": "產品形式分類",
    "Product-form routing": "產品形式 routing",
    "Sheet / plate": "板材／片材",
    "Extrusions": "擠型材",
    "Taiwan practice notes": "台灣工程實務備註",
    "Flatness concern": "平整度議題",
    "Design-value guard": "設計值防呆",
    "Standard freshness snapshot": "標準新鮮度快照",
    "Corrosion routing": "耐蝕性 routing",
    "CNS cross-reference caution": "CNS 交叉對照注意事項",
    "Performance testing routing": "性能試驗 routing",
    "Glass design": "玻璃設計",
    "Water-management principles": "水管理原則",
    "Mock-up / field-test note": "Mock-up／現場試驗注意事項",
    "Stone type specifications": "石材類型規範",
    "Sampling / variability guard": "取樣／變異性防呆",
    "Structural-glass load-path rule": "結構玻璃荷載路徑規則",
    "Public-repository rule": "公開 repository 規則",
    "ASTM E1300 scope guard": "ASTM E1300 適用範圍防呆",
    "Local verification items": "局部驗證項目",
    "Polymer sleeve / PTFE guard": "Polymer sleeve／PTFE 防呆",
    "Support philosophy": "支承策略",
    "Load-path separation": "荷載路徑分流",
    "Bite / thickness routing": "Bite／thickness routing",
    "Adhesion / compatibility": "黏著／相容性",
    "Movement guard": "位移防呆",
    "Why it matters": "重要性",
    "Design questions": "設計問題",
    "Redundancy is system-specific": "冗餘具系統特定性",
    "Analysis / testing routing": "分析／試驗 routing",
    "Model definition": "模型定義",
    "Verification hierarchy": "驗證層級",
    "Global vs local model": "全域模型與局部模型",
    "Linear-model guard": "線性模型防呆",
    "Documentation minimum": "文件化最低要求",
    "Interlayer guard": "中間膜防呆",
    "Deflection vs stress": "撓度與應力",
    "Multi-ply laminate": "多層膠合玻璃",
    "Post-breakage emphasis": "破裂後行為重點",
    "Inter-story standards routing": "層間變位標準 routing",
    "Clearance vs stress": "淨空與應力",
    "Support restraint guard": "支承拘束防呆",
    "Hardware reactions": "五金反力",
    "Dead-load path": "自重荷載路徑",
    "Wind-load path": "風荷載路徑",
    "Eccentricity": "偏心",
    "Product rating vs installed demand": "產品額定值與安裝需求",
    "Connection decomposition": "連接拆解",
    "Fastener-group analysis": "緊件群分析",
    "Pull-out / thread engagement": "抗拔／螺紋咬合",
    "Local extrusion behavior": "鋁擠型局部行為",
    "Hinge-specific notes": "鉸鏈特定注意事項",
    "Lock / keeper-specific notes": "鎖點／keeper 特定注意事項",
    "Friction stay / restrictor-specific notes": "Friction stay／restrictor 特定注意事項",
    "Hardware modification guard": "五金修改防呆",
    "NAFS routing": "NAFS 標準 routing",
    "AAMA 910 routing": "AAMA 910 標準 routing",
    "ASTM E330 routing": "ASTM E330 標準 routing",
    "Pre-test / post-test function": "試驗前／後功能",
    "Modification / substitution review": "修改／替代審查",
    "Calculation + test traceability": "計算＋試驗可追溯性",
    "Load cases": "荷載案例",
    "Glass / infill dead load": "玻璃／填充材自重",
    "Wind-load transfer": "風荷載傳遞",
    "Corner-joint behavior": "轉角接頭行為",
    "Frame analysis choices": "框架分析選擇",
    "Beam / frame model": "梁／框架模型",
    "Shell / solid model": "殼／實體模型",
    "Results to preserve": "應保存的結果",
    "Operability guard": "可操作性防呆",
    "Joint design basics": "接縫設計基礎",
    "Three-sided adhesion guard": "三面黏著防呆",
    "Structural silicone vs weatherseal": "結構矽利康與 weatherseal",
    "Compatibility / adhesion": "相容性／黏著",
    "Component-specific pressure": "構件特定風壓",
    "Load path": "荷載路徑",
    "Effective wind area guard": "有效受風面積防呆",
    "Wind tunnel routing": "風洞試驗 routing",
    "Force path": "受力路徑",
    "Movement path": "位移路徑",
    "Chapter 4 structural principle": "第四章結構原則",
    "External wall categories are not identical": "外牆分類不可視為相同",
    "Reaction workflow": "反力計算流程",
    "Eccentricity guard": "偏心防呆",
    "Movement vs restraint": "位移與拘束",
    "Anchor family routing": "錨栓類型 routing",
    "Fastener guard": "緊件防呆",
    "Fastener-group centroid": "緊件群形心",
    "Direct force": "直接力",
    "In-plane eccentric shear / torsion": "面內偏心剪力／扭矩",
    "Eccentric tension / overturning": "偏心拉力／傾覆",
    "Combined tension + shear": "拉力＋剪力組合",
    "Connected-material checks": "被連接材料檢核",
    "Screw-group specific guard": "螺絲群特定防呆",
    "Fillet-weld effective throat": "角焊道有效喉厚",
    "Arbitrary weld-group representation": "任意焊道群表示方式",
    "Weld-group effective area": "焊道群有效面積",
    "Centroid and section properties": "形心與截面性質",
    "Moment / torsion effects": "彎矩／扭矩效應",
    "Critical-point check": "臨界點檢核",
    "Resultant demand": "合成需求",
    "Base metal / connected part": "母材／被連接構件",
    "Steel vs aluminum routing": "鋼材與鋁材 routing",
    "Steel welding": "鋼結構焊接",
    "Aluminum welding": "鋁合金焊接",
    "Failure-mode checklist": "破壞模式檢核表",
    "Simplified mechanics are not final design": "簡化力學不等於正式設計",
    "Deflection guard": "撓度防呆",
    "Section-property guard": "截面性質防呆",
    "Transom-specific notes": "橫料特定注意事項",
    "Axis discipline": "座標軸規則",
    "Independent-axis linear analysis": "獨立軸線性分析",
    "Combined stress": "組合應力",
    "Resultant deflection": "合成撓度",
    "Corner / feature framing": "轉角／造型 framing",
    "Torsion guard": "扭轉防呆",
    "Joint labels are not mechanics": "接頭標籤不等於力學行為",
    "Member stiffness": "構件剛度",
    "Loads": "荷載",
    "Reactions are outputs, not assumptions": "反力是輸出，不是預設",
    "Strength checks": "強度檢核",
    "Deflection checks": "撓度檢核",
    "Sensitivity / bounding analysis": "敏感度／界限分析",
    "Section-property mechanics": "截面性質力學",
    "Relative-stiffness load sharing": "相對剛度荷載分配",
    "Male / female curtain-wall extrusion guard": "公／母帷幕鋁擠型防呆",
    "Independent / partial behavior": "獨立／部分共同作用",
    "Stress / deflection checks": "應力／撓度檢核",
    "Force-transfer questions": "傳力問題",
    "Sleeve as reinforcement": "Sleeve 作為補強",
    "Local connection demand": "局部連接需求",
    "Semi-rigid model": "半剛性模型",
    "Movement compatibility": "位移相容性",
    "Bounding cases": "界限案例",
    "Relative displacement": "相對位移",
    "Why maximum mullion deflection is not enough": "為何只看直料最大撓度不足",
    "Direction matters": "方向很重要",
    "Glass support assumption": "玻璃支承假設",
    "Criterion guard": "判定基準防呆",
    "Data-model recommendation": "資料模型建議",
    "Point loads": "集中荷載",
    "Positive / negative cases": "正／負壓案例",
    "Glass weight": "玻璃重量",
    "Setting-block position matters": "Setting block 位置很重要",
    "Structural silicone guard": "結構矽利康防呆",
    "Local check": "局部檢核",
    "Geometry-first workflow": "幾何優先流程",
    "Typical shape concept": "典型分配形狀概念",
    "Wind vs dead load": "風荷載與自重",
    "Simplified formulas guard": "簡化公式防呆",
    "Reactions are part of the output": "反力是輸出的一部分",
    "Source distinction": "來源區分",
    "Scope is mandatory": "必須明確定義範圍",
    "Overall status logic": "整體狀態邏輯",
    "Required evidence fields": "必要證據欄位",
    "`NOT_APPLICABLE` guard": "`NOT_APPLICABLE` 防呆",
    "`WARNING` guard": "`WARNING` 防呆",
    "Coverage matrix": "Coverage 矩陣",
    "Calculation package complete": "計算套件完整性",
    "Top-level load path": "頂層荷載路徑",
    "Failure-mode families": "破壞模式族群",
    "A. Load-definition failure": "A. 荷載定義失敗",
    "B. Load-transfer failure": "B. 荷載傳遞失敗",
    "C. Global framing failure": "C. 整體 framing 失敗",
    "D. Glass / glazing failure": "D. 玻璃／glazing 失敗",
    "E. Connection failure": "E. 連接失敗",
    "F. Welded-connection failure": "F. 焊接連接失敗",
    "G. Anchor / substrate failure": "G. 錨栓／基材失敗",
    "H. Metal-panel / stiffener failure": "H. 金屬面板／補強材失敗",
    "I. Operable-element failure": "I. 可開啟構件失敗",
    "J. Movement-compatibility failure": "J. 位移相容性失敗",
    "K. Verification / evidence failure": "K. 驗證／證據失敗",
    "Cascade concept": "連鎖失效概念",
    "Review question set": "審查問題集",
    "Relation to canonical pages": "與 canonical 頁面的關係",
    "Review hierarchy": "審查層級",
    "Calculation correctness ≠ calculation completeness": "計算正確 ≠ 計算完整",
    "A numerical PASS ≠ a traceable PASS": "數值 PASS ≠ 可追溯 PASS",
    "Engineering PASS ≠ project-specification compliance PASS": "工程 PASS ≠ 專案規範符合性 PASS",
    "PASS is local unless scope is explicit": "未明確範圍時，PASS 只代表局部",
    "Missing evidence is not a favorable assumption": "缺少證據不等於可採有利假設",
    "Public-safety rule": "公開安全規則",
    "Phase A — Literal extraction": "Phase A — 原文抽取",
    "Phase B — Authority / currentness verification": "Phase B — 權威性／現行性驗證",
    "Document control / authority": "文件控制／權威性",
    "Design responsibility / required scope": "設計責任／必要範圍",
    "Governing references": "適用參考依據",
    "Loads / actions": "荷載／作用",
    "Strength / safety criteria": "強度／安全判定基準",
    "Serviceability / movement criteria": "服務性／位移判定基準",
    "Required calculation coverage": "必要計算涵蓋範圍",
    "Required calculation trace / submittal evidence": "必要計算追溯／送審證據",
    "Guardrails": "防呆規則",
    "Safety-factor guard": "安全係數防呆",
    "AAMA TIR-A9 routing": "AAMA TIR-A9 標準 routing",
}

TEXT_REPLACEMENTS = {
    "Do not reduce the entire chain to one scalar `w` without provenance.": "不要在失去來源追溯的情況下，把整條鏈縮成單一純量 `w`。",
    "> Glass fin often requires specialist analysis beyond prescriptive façade-member checks. Use validated modeling assumptions and project-specific verification.": "> 玻璃肋通常需要超出一般外牆構件條文式檢核的專業分析；應採用經驗證的建模假設與專案特定驗證。",
    "> Project-specific structural sealant glazing should follow the selected sealant manufacturer's engineering review and approved substrate testing where required.": "> 專案特定的結構矽利康玻璃系統，應依所選矽利康製造商的工程審查，以及需要時的基材核准試驗辦理。",
    "> Post-breakage design is often project- and system-specific;本頁只提供 failure-mode routing，不提供通用 residual-capacity 數值。": "> 破裂後設計通常具有專案與系統特定性；本頁只提供 failure-mode routing，不提供通用 residual-capacity 數值。",
}

ALLOWED_ENGLISH_HEADINGS = {
    "ASTM",
    "CNS",
    "AAMA / FGIA",
    "AAMA / FGIA / ASTM",
    "FEA",
    "NAFS",
}


def has_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text))


def is_allowed_english_heading(text: str) -> bool:
    if text in ALLOWED_ENGLISH_HEADINGS:
        return True
    compact = re.sub(r"[`*_()]", "", text).strip()
    if re.fullmatch(r"(?:ASTM|CNS|AAMA|FGIA|ISO|ACI|AISC|AWS|NAFS|FEA)(?:[ /+&.0-9A-Z_-]*)", compact):
        return True
    return False


def is_probable_english_prose(line: str) -> bool:
    stripped = line.strip()
    if not stripped or has_cjk(stripped):
        return False
    if stripped.startswith(("- ", "* ", "|", "#", "http://", "https://", "`")):
        return False
    words = ENGLISH_WORD_RE.findall(stripped)
    return len(words) >= 10


def normalize_file(path: Path, write: bool) -> tuple[bool, list[str], list[str]]:
    rel = path.relative_to(ROOT).as_posix()
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()
    changed = False
    unresolved_headings: list[str] = []
    english_prose: list[str] = []

    target_title = PATH_TITLES.get(rel)
    in_fence = False
    h1_replaced = False
    in_frontmatter = bool(lines and lines[0].strip() == "---")
    frontmatter_done = not in_frontmatter

    out: list[str] = []
    for idx, line in enumerate(lines):
        if in_frontmatter and not frontmatter_done:
            if idx > 0 and line.strip() == "---":
                frontmatter_done = True
                out.append(line)
                continue
            if target_title and line.startswith("title:"):
                quote = '"' if '"' in line else "'" if "'" in line else ""
                new_line = f"title: {quote}{target_title}{quote}" if quote else f"title: {target_title}"
                if new_line != line:
                    changed = True
                out.append(new_line)
                continue
            out.append(line)
            continue

        if line.lstrip().startswith("```") or line.lstrip().startswith("~~~"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        if line in TEXT_REPLACEMENTS:
            new_line = TEXT_REPLACEMENTS[line]
            if new_line != line:
                changed = True
            out.append(new_line)
            continue

        match = HEADING_RE.match(line)
        if match:
            hashes, heading = match.groups()
            new_heading = heading
            if hashes == "#" and target_title and not h1_replaced:
                new_heading = target_title
                h1_replaced = True
            elif heading in HEADING_MAP:
                new_heading = HEADING_MAP[heading]
            new_line = f"{hashes} {new_heading}"
            if new_line != line:
                changed = True
            out.append(new_line)
            if not has_cjk(new_heading) and not is_allowed_english_heading(new_heading):
                unresolved_headings.append(f"{rel}:{idx + 1}: {new_heading}")
            continue

        out.append(line)
        if is_probable_english_prose(line):
            english_prose.append(f"{rel}:{idx + 1}: {line.strip()}")

    new_text = "\n".join(out) + ("\n" if original.endswith("\n") else "")
    if write and changed:
        path.write_text(new_text, encoding="utf-8")
    return changed, unresolved_headings, english_prose


def iter_markdown() -> list[Path]:
    result = []
    for path in ROOT.rglob("*.md"):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(".git/"):
            continue
        result.append(path)
    return sorted(result)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write conservative normalization changes")
    args = parser.parse_args()

    changed_files: list[str] = []
    unresolved: list[str] = []
    prose: list[str] = []
    for path in iter_markdown():
        changed, headings, english_lines = normalize_file(path, args.write)
        if changed:
            changed_files.append(path.relative_to(ROOT).as_posix())
        unresolved.extend(headings)
        prose.extend(english_lines)

    print(f"Markdown files needing/receiving normalization: {len(changed_files)}")
    for item in changed_files:
        print(f"  CHANGED {item}")

    print(f"Unresolved pure-English headings: {len(unresolved)}")
    for item in unresolved:
        print(f"  HEADING {item}")

    print(f"Probable English prose lines for manual review: {len(prose)}")
    for item in prose:
        print(f"  PROSE {item}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
