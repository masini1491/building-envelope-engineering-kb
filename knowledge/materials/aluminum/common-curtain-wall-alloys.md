---
title: "建築外殼常用鋁合金基線：3003-H14 / 3004-H12 / 6005-T5 / 6105-T5 / 6063-T5"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
document_type: "material-routing"
domain: "materials.aluminum"
canonical_key: "materials.aluminum.common-curtain-wall-alloys"
---

# 建築外殼常用鋁合金基線

本頁整理台灣帷幕／建築外殼工程常見的鋁板與鋁擠型牌號，作為材料選用與逐牌號頁面的入口。

## 產品形式分類

### 板材／片材

常見：

- 3003-H14
- 3004-H12

常見 governing family：

- ASTM B209/B209M — Aluminum and Aluminum-Alloy Sheet and Plate
- CNS 2253 — 鋁及鋁合金片、捲及板

CNS 2253 的 current status / revision provenance 由 [`../../../references/standards/cns-2253.md`](../../../references/standards/cns-2253.md) 維護；本頁不另存 edition snapshot。

材料替代比較見 [`3003-H14-vs-3004-H12.md`](3003-H14-vs-3004-H12.md)。

### 擠型材

常見：

- 6005-T5
- 6105-T5
- 6063-T5

常見 governing family：

- ASTM B221 / B221M — Aluminum and Aluminum-Alloy Extruded Bars, Rods, Wire, Profiles, and Tubes
- CNS 2257 — 鋁及鋁合金擠型材

CNS 2257 的 current status / revision provenance 由 [`../../../references/standards/cns-2257.md`](../../../references/standards/cns-2257.md) 維護。

個別頁面：

- [`6005-T5.md`](6005-T5.md)
- [`6105-T5.md`](6105-T5.md)
- [`6063-T5.md`](6063-T5.md)

## 台灣工程實務觀察

### 3003-H14 → 3004-H12 材料轉換

近年台灣帷幕／金屬外牆材料供應已有 3004-H12 進入原本常見 3003-H14 使用情境的實務觀察。

這類市場／專案趨勢屬 `FIELD_OBSERVATION`，不能自行升格成材料替代許可或 project-approved equivalence。

### 平整度／Oil canning

完成面平整度不是 alloy / temper 單一變數。至少還受：

- 板厚
- 面板尺寸／flat width
- coil / sheet leveling
- 殘留應力
- 裁切／折彎／補強
- coating / bake process
- subframe tolerance
- installation restraint
- thermal movement

影響。

詳見 [`../../cladding/aluminum-panel-flatness-and-oil-canning.md`](../../cladding/aluminum-panel-flatness-and-oil-canning.md)。

## 設計值防呆

本頁不保存未逐項核實的 yield / tensile / allowable 數值。

正式設計應依：

- current governing material standard；
- mill certificate；
- project design specification；
- applicable aluminum design standard；
- product form / thickness / temper / condition。

## 不可推論事項

- 6005、6005A、6105、6063 不可只因同屬 6xxx 系就視為 equivalent。
- T5 / T6、H12 / H14 不可互換。
- 材料標準合格不代表完成 panel 外觀、局部連接或結構 capacity 自動合格。
- ASTM / CNS / JIS related standard 不代表全文等價。

> 本頁是 material routing；標準版本 ownership 在 `references/standards/`，完成面問題在 `cladding/`。