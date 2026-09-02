---
title: "建築外殼不鏽鋼材料基線"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
---

# 建築外殼不鏽鋼材料基線

不鏽鋼在建築外殼工程可能用於螺栓、螺帽、華司、連接件、板件、角鐵、裝飾板與其他配件。材料規範需依 product form 分開，不應只寫「SUS304」或「A2」就結束。

## Product-form routing

- **ASTM A240/A240M** — Chromium and Chromium-Nickel Stainless Steel Plate, Sheet, and Strip for Pressure Vessels and General Applications
  - 適合 routing plate / sheet / strip 類產品。

- **ASTM A276/A276M** — Stainless Steel Bars and Shapes
  - 適合 routing bars / shapes 類產品。

- **ISO 3506 series** — Corrosion-resistant stainless steel fasteners
  - 螺栓／螺絲／螺柱與螺帽等 fastener property classes 應走 fastener standard，而不是用 A240/A276 代替。

## 304 / 316 與 A2 / A4

工程口語常簡化：

- A2 ≈ 304 family
- A4 ≈ 316 family

但這只能當快速理解，不應宣告完全等價。

`A2` / `A4` 是 ISO 3506 fastener steel grade groups；`304` / `316` 是不鏽鋼 grade designation family。實際 fastener 可使用符合該 group composition / processing requirement 的不同鋼種。

## Corrosion routing

選不鏽鋼不應只看 nominal grade，還應確認：

1. exposure environment
2. chloride / coastal exposure
3. crevice / trapped water
4. contact with aluminum / carbon steel / galvanized steel
5. galvanic isolation detail
6. surface finish / pickling / passivation（需要時）
7. welding heat tint / post-weld treatment
8. fastener galling risk

## Do not assume

- `SUS304 = A2` 不應寫成完全等價。
- `SUS316 = A4` 同理。
- 304 一定足夠所有外牆環境不成立；應依 exposure 與專案耐蝕要求判斷。
- stainless steel 與 aluminum 接觸不代表一定失效，但需要評估 galvanic couple、water retention 與 isolation details。

## Primary sources

- ASTM A240/A240M standard page: https://store.astm.org/
- ASTM A276/A276M standard page: https://store.astm.org/
- ISO 3506 series: https://www.iso.org/

> 本頁為材料 routing；精確化學成分、機械性質與設計值應回到正式標準、MTR / MTC 與專案規範。