---
title: "螺絲抗拔與 Thread Engagement 方法"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 螺絲抗拔與 Thread Engagement 方法

## 核心概念

帷幕牆 screw connection 的 failure mode 至少要區分：

1. screw 本體 tension / shear
2. connected material bearing
3. screw pull-out / thread stripping
4. local extrusion wall bending / tear-out
5. combined eccentric fastener-group demand

因此「螺絲本體強度 PASS」不代表 connection 已完成。

## Pull-out variables

Screw pull-out / thread stripping 通常受到下列因素影響：

- screw nominal diameter
- thread pitch / threads per inch
- thread form
- engagement length / connected material thickness
- parent material alloy / temper
- parent material yield / ultimate strength
- tapped hole vs thread-forming / self-drilling configuration
- installation quality / stripping damage

不能只用 screw property class 判斷 pull-out capacity。

## Thread engagement

對 machine screw / bolt into tapped extrusion，至少保存：

- nominal diameter
- pitch
- engaged thread length
- parent material
- hole preparation / tapping method
- whether full threads are effectively engaged

若某 design method 以「達到 fastener tensile capacity 所需最小 engagement」表示，這只是其中一種 design check；實際 equation / coefficient 必須回到 current standard / validated engineering method。

## Screw pull-out workflow

1. 求每支 screw 的 tensile demand。
2. 確認 actual thread / screw geometry。
3. 取得 parent material properties。
4. 選擇適用 current fastener design method。
5. 計算 nominal pull-out / stripping strength。
6. 套用該 design basis 所要求的 resistance / safety treatment。
7. 與 demand 比較。
8. 另外檢查 bearing、edge distance、local wall bending與 screw-body capacity。

## Eccentric group interaction

若 screw 位於偏心 fastener group，pull-out demand 不得直接取 `total tension / number of screws`；應先依 [Fastener Group Analysis](fastener-group-analysis.md) 求每一支 screw 的 actual tension / shear demand，再進入 pull-out check。

## AAMA TIR-A9 標準 routing

FGIA 目前將 **AAMA TIR-A9-14, Design Guide for Metal Cladding Fasteners** 列為 Active，並包含後續 errata / addendum。舊工程計算中可能出現 TIR-A9-1991 / 2000 表格或公式，但 public KB 不應直接把舊版表格當 current canonical values。

使用時必須：

- 確認 current edition
- 確認 fastener family / thread condition
- 確認 connected material applicability
- 不重製受版權保護的完整表格

## 安全係數防呆

若歷史計算書曾使用固定 `SF = x`，不能因此寫入 public KB 作為 universal safety factor。Safety / resistance treatment 必須由採用的 design standard、manufacturer engineering basis 或 project specification 提供。

## 不可推論事項

- `A2-70` 不等於已知 pull-out capacity。
- thread engagement 越長不代表 capacity 可無限制線性增加。
- connected plate thickness 不一定等於有效 full-thread engagement length。
- screw tension PASS 不代表 parent material threads PASS。
- 舊 TIR-A9 表格值不可在未確認 current applicability 下直接複製。

## 相關破壞模式

- [Fastener Group Analysis](fastener-group-analysis.md)
- [Local Extrusion Failure](local-extrusion-failure.md)
- [Load Path and Anchor Reactions](load-path-and-anchor-reactions.md)
- stainless fastener property-class routing under `knowledge/fasteners/`

## 公開來源 routing

- FGIA / AAMA TIR-A9-14 — Design Guide for Metal Cladding Fasteners（current store listing；版本使用前重新確認）。
- The Aluminum Association — Aluminum Design Manual（parent aluminum member / connection design routing）。
- actual screw manufacturer technical data / evaluation report where applicable。

> 本頁保存 failure-mode framework，不保存任何非公開專案 screw size、板厚、係數或 pull-out 數值。