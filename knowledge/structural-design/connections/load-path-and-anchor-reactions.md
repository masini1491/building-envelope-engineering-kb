---
title: "帷幕牆 Load Path／繫件／Anchor Reaction 基線"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 帷幕牆 Load Path／繫件／Anchor Reaction 基線

## 核心概念

帷幕牆受力不能只看單一構件，必須沿完整 load path 檢查：

`glass / panel → gasket / setting block / structural silicone / pressure plate → mullion / transom → bracket / cleat / fastener → anchor → slab / beam / column`

每一層都可能形成 governing failure mode。

## Reaction workflow

1. 取得 governing positive / negative design pressure。
2. 依 panel / glass / framing geometry 建立 tributary load。
3. 求 mullion / transom support reactions。
4. 將反力分解到 bracket / anchor group。
5. 考慮 eccentricity、lever arm、slot、shim、stand-off distance。
6. 檢查 bolt / screw tension、shear、bearing、tear-out、local plate bending。
7. 檢查 cast-in / post-installed anchor 的 concrete failure modes。
8. 確認主體結構承載與 edge distance / embedment / reinforcement interaction。

## Eccentricity guard

帷幕 bracket 很少是完全零偏心的理想點支承。實際常有：

- slab edge 到 mullion centerline 的水平偏心
- bracket stand-off
- shim pack
- slotted hole
- vertical adjustment
- multiple fasteners sharing load

因此 anchor group force 不應只用 `總剪力 ÷ bolt 數量`。

## Movement vs restraint

很多 curtain wall connection 同時要達到兩個看似相反的目標：

- 在風壓／自重方向提供足夠 restraint
- 在 thermal / inter-story movement 方向允許受控滑動

設計時要明確定義：
- fixed point
- sliding point
- dead-load support
- wind-load restraint
- slot direction
- installation tolerance

不要把所有長孔都當成「一定能自由滑動」；實際 clamping force、washer、bolt pretension、surface friction 都可能影響。

## Anchor family routing

- cast-in anchor / anchor rod：依實際產品、鋼材規格與 concrete design basis
- post-installed mechanical anchor：ACI 318 Chapter 17 + ACI 355.2 / approved evaluation report as applicable
- post-installed adhesive anchor：ACI 318 Chapter 17 + ACI 355.4 / approved evaluation report as applicable

ASTM F1554 是 anchor bolt / rod 類材料與產品規格，不能拿來當 mechanical expansion anchor 的 capacity standard。

## Fastener guard

- A2-70 / A2-80 / project-specific A2-90 是 fastener property information，不等於 connection capacity。
- connection capacity 還受 diameter、thread engagement、hole geometry、bearing material、edge distance、eccentricity、pretension、corrosion 與 installation quality 影響。

## Do not assume

- `2 bolts = each takes 50%` 不得無條件成立。
- `slotted hole = zero force in slot direction` 不成立。
- `anchor catalogue allowable load` 不得脫離 concrete strength、edge distance、spacing、embedment、seismic condition 與 installation condition直接套用。
- 只要 bracket 本體夠強，不代表 connection system 已完成檢核。

## Sources / routing

- 內政部建築研究所《帷幕牆系統結構耐風設計手冊》
- ACI 318 Chapter 17
- ACI 355.2 / ACI 355.4
- applicable anchor manufacturer evaluation report / ETA / ICC-ES report / project approval

> 本頁是 load-path design framework，不取代 project-specific connection calculation。