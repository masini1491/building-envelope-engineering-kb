---
title: "金屬複合板與蜂巢板基線"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 金屬複合板與蜂巢板基線

本頁整理 aluminum composite material（ACM/MCM）、aluminum honeycomb panel 與其他 sandwich panel 在建築外殼工程中的基本判斷架構。

## 先分清產品類型

不同產品不能只因外觀相似就視為同一系統：

- solid aluminum plate / sheet panel
- aluminum composite material（ACM / MCM）
- aluminum honeycomb sandwich panel
- foam-core / mineral-core / other sandwich panel

各類產品的面材、芯材、黏著方式、邊部封裝、局部補強、耐火與耐候性能可能完全不同。

## 夾芯板機械性能試驗族群

蜂巢／sandwich panel 常見材料或構造試驗包括：

- **ASTM C393/C393M-20** — Core Shear Properties of Sandwich Constructions by Beam Flexure
- **ASTM C365/C365M-22** — Flatwise Compressive Properties of Sandwich Cores
- **ASTM C273/C273M-20** — Shear Properties of Sandwich Core Materials
- **ASTM D7249/D7249M-20** — Facesheet Properties of Sandwich Constructions by Long Beam Flexure
- **ASTM D1781-98(2021)** — Climbing Drum Peel for Adhesives

這些試驗可提供 core shear、facesheet、flatwise compression 或 peel 等材料／bond performance evidence；**單一 coupon test 不能取代完成 panel 與 attachment system 的結構驗證。**

## 面板層級結構驗證

實際外牆 panel design 至少要確認：

1. panel dimensions / thickness
2. face-sheet alloy / temper / thickness
3. core type / geometry / density
4. adhesive / bonding process
5. perimeter extrusion / folded return / reinforcement
6. attachment spacing and local bearing / pull-out
7. wind pressure / suction
8. deflection / permanent deformation criteria
9. thermal movement
10. corner / edge / opening local effects
11. full-size structural test（若專案要求或分析模型不足）

## 防火試驗適用性防呆

### ASTM E84

**ASTM E84-26a** 測的是材料／產品／assembly 在特定 tunnel exposure 下的 relative surface flame spread 與 smoke developed characteristics。

ASTM 自身明確說明 E84：
- 不能只靠 flame spread index 把材料定義為 noncombustible；
- 不涵蓋所有實際 fire hazard / fire risk 因素；
- 對 melt / drip / delaminate 的材料，結果可能不能直接代表其他材料的行為。

因此：

> `ASTM E84 PASS` 不等於 exterior wall assembly 已通過 full-scale / assembly fire requirement。

### 外牆組件防火試驗

若專案法規或規範要求 NFPA 285 或其他 exterior-wall assembly fire test，判定對象通常是**具體 assembly**：面板、芯材、保溫、防水層、air gap、subframe、fire blocking、開口細節等共同組成。

不得只因同品牌／同芯材的另一個 wall build-up 有測試報告，就自動宣稱本案 configuration 被涵蓋。

## 替代審查

複合板或蜂巢板替代時，至少比對：

- product construction
- face sheet
- core
- adhesive
- panel thickness
- attachment system
- structural test / calculation basis
- coating
- corrosion / edge protection
- fire classification / assembly coverage
- water-management details
- warranty / fabrication limitations

## 不可推論事項

- `蜂巢板較厚 = 一定較強` 不成立。
- `peel strength 合格 = panel wind-load capacity 合格` 不成立。
- `E84 Class A = noncombustible` 不成立。
- `某產品有 NFPA 285 report = 任意外牆組合皆 covered` 不成立。

## 主要來源

- ASTM C393/C393M-20: https://store.astm.org/c0393_c0393m-20.html
- ASTM C365/C365M-22: https://store.astm.org/c0365_c0365m-22.html
- ASTM C273/C273M-20: https://store.astm.org/standards/c273
- ASTM D7249/D7249M-20: https://store.astm.org/d7249_d7249m-20.html
- ASTM D1781-98(2021): https://store.astm.org/d1781-98r21.html
- ASTM E84-26a: https://store.astm.org/e0084-26a.html

> 本頁不取代產品認證、專案 fire code review、結構計算或 full-size test。