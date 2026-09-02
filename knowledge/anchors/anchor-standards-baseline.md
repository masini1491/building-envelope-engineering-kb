---
title: "錨栓／Anchor 標準基線"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
---

# 錨栓／Anchor 標準基線

建築外殼工程中的 anchor 不應被視為單一材料類別。最少要先區分：

- cast-in / headed anchor bolts
- mechanical post-installed anchors
- adhesive anchors
- embedded plates / welded studs / proprietary anchor channels

不同類型 governing standard 不同。

## ASTM F1554

**ASTM F1554/F1554M** 是 anchor bolts / anchor rods 的材料與機械性質規格之一，常見 Grades 36 / 55 / 105。

但 ASTM F1554 的 scope 明確指出：**mechanical expansion anchors 不在本標準範圍內。**

因此不可把所有後置式 expansion anchor 都寫成 `ASTM F1554`。

## Post-installed anchors

後置式錨栓的設計與資格評估通常要進入：

- **ACI 318 Chapter 17** — Anchoring to Concrete
- **ACI 355.2** — Qualification of Post-Installed Mechanical Anchors in Concrete
- **ACI 355.4** — Qualification of Post-Installed Adhesive Anchors in Concrete

實際產品亦可能透過 ICC-ES evaluation / ESR 等系統提供適用混凝土強度、裂縫／非裂縫、邊距、間距、安裝條件與 design data。

## Curtain-wall design routing

幕牆 anchor / bracket 設計至少分開檢查：

1. attachment type
2. substrate：concrete / steel / masonry / other
3. tension / shear / combined load
4. concrete breakout / pullout / pryout / steel strength / bond strength
5. edge distance / spacing / group effect
6. cracked / uncracked concrete
7. seismic qualification（需要時）
8. installation torque / hole cleaning / embedment / inspection requirements
9. base plate / bracket bearing and bending
10. weld / bolt / anchor channel 等完整 load path

## Do not assume

- `F1554 anchor bolt = expansion anchor` 錯誤。
- 只看螺桿鋼材強度不能代表整個 anchor capacity。
- 廠商型錄最大拉力不能直接當設計值；需確認對應 substrate、embedment、edge distance、safety/design method。
- adhesive anchor 不應用 mechanical anchor 的 qualification 規則代替。

## Primary sources

- ASTM F1554/F1554M standard page: https://store.astm.org/
- ACI 318 Building Code Requirements for Structural Concrete: https://www.concrete.org/
- ACI 355.2 / 355.4 qualification standards: https://www.concrete.org/
- ICC-ES evaluation services: https://icc-es.org/

> 本頁為 anchor 類型與 governing standard routing；實際設計值應依專案採用 code、產品 ESR/ETA/測試報告與結構計算確認。