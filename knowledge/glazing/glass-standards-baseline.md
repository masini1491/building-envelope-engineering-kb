---
title: "建築玻璃標準基線"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
---

# 建築玻璃標準基線

本頁整理建築外殼常見平板玻璃的 ASTM governing standards。用途是讓 AI 先判斷「玻璃產品規格」與「結構耐風設計」分屬不同標準，不直接用產品標準推算承載力。

## 核心標準

- **ASTM C1036-25** — Standard Specification for Flat Glass
  - 基礎平板玻璃品質規格。
  - 涵蓋建築用透明／著色平板玻璃等品質要求。
  - ASTM 明確指出 reflective distortion 並非全部由本標準處理。

- **ASTM C1048-25** — Standard Specification for Heat-Strengthened and Fully Tempered Flat Glass
  - 熱增強（heat-strengthened）與全強化（fully tempered）平板玻璃產品規格。
  - 不應只因稱為 tempered 就自行套用任意強度倍數。

- **ASTM C1172-24e1** — Standard Specification for Laminated Architectural Flat Glass
  - 建築用夾層玻璃品質規格。
  - 可涉及 safety、security、hurricane/cyclic-wind、blast、sound reduction 等不同應用，但實際性能須依對應系統設計／試驗要求。
  - ASTM 本身指出 optical distortion evaluation 不在其主要 scope，並建議可用 mock-up 評估。

- **ASTM C1376-21a** — Standard Specification for Pyrolytic and Vacuum Deposition Coatings on Flat Glass
  - 鍍膜玻璃（pyrolytic / vacuum sputtering）之光學與外觀品質要求。
  - 不等於基材玻璃的所有品質／結構要求。

- **ASTM E1300-24** — Standard Practice for Determining Load Resistance of Glass in Buildings
  - 玻璃在建築中的 load resistance 設計方法。
  - 產品符合 C1036 / C1048 / C1172 不代表已完成 E1300 結構檢核。

## 工程 routing

遇到「這片玻璃能不能承受設計風壓？」時，AI 應分開檢查：

1. glass make-up：monolithic / laminated / insulating glass unit
2. glass treatment：annealed / heat-strengthened / fully tempered
3. nominal thickness / actual thickness
4. supported dimensions and edge support
5. load duration / load type
6. applicable load-resistance design method（例如 ASTM E1300）
7. project-specific allowable probability / safety requirements
8. coating / frit / holes / notches / edge condition 等是否另有影響

## 外觀／變形防呆

- 玻璃「符合產品規格」不代表建築師在任何視角下都不會看到 roller wave、anisotropy、bow / warp、coating nonuniformity 或 laminated optical effects。
- 外觀接受標準若是專案重要要求，應在 mock-up / visual acceptance criteria 階段明確處理。

## 不可推論事項

- `tempered = exactly 4× annealed strength` 不得當成通用設計規則。
- `laminated = two plies simply add thickness` 不得直接作為結構算法。
- `C1048 compliant = E1300 PASS` 不成立。
- 不得從標稱厚度自行猜 load resistance。

## 主要來源

- ASTM C1036-25: https://store.astm.org/c1036-25.html
- ASTM C1048-25: https://store.astm.org/c1048-25.html
- ASTM C1172-24e1: https://store.astm.org/c1172-24e01.html
- ASTM C1376-21a: https://store.astm.org/c1376-21a.html
- ASTM E1300-24 listing: https://store.astm.org/products-services/standards-and-publications/standards/building-standards.html

> 本頁是標準 routing，不取代正式玻璃規範、計算書、玻璃廠技術資料或專案 mock-up criteria。