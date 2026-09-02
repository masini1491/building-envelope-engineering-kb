---
title: "活動窗整窗性能與 Life-cycle Routing"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
---

# 活動窗整窗性能與 Life-cycle Routing

## 角色

活動窗的 engineering calculation 與整窗 performance test 是互補關係。

Calculation 可回答：

- member / hardware demand
- connection strength
- local extrusion behavior
- predicted deflection

Performance test 則可觀察：

- assembly structural behavior
- air / water performance
- operability
- permanent deformation / distress
- repeated-use durability where required

兩者不能互相取代。

## NAFS routing

截至 2026-09-02，FGIA Store 將 **AAMA/WDMA/CSA 101/I.S.2/A440-26 (NAFS)** 列為 Active。

NAFS 適用於 windows、doors、skylights 的產品性能分類／規範 routing。使用時應依產品型式、尺寸、performance class / grade、test specimen 與 applicable configuration 判斷 coverage。

不得將某一 tested product 的 rating 無條件套用到：

- 不同 sash dimensions
- 不同 glass make-up
- 不同 hardware quantity / spacing
- 不同 reinforcement
- 不同 anchorage
- 不同 mullion / curtain-wall integration condition

## AAMA 910 routing

截至 2026-09-02，FGIA Store 將 **AAMA 910-24 — Life Cycle Specifications and Test Methods for AW Class Windows and Doors** 列為 Active。

其用途是 life-cycle / durability related performance routing，與一次 static structural strength calculation 不同。

因此：

`static strength PASS`

不代表：

`cycle durability PASS`

也不代表長期 operating force / locking / sealing performance 已驗證。

## ASTM E330 routing

ASTM **E330/E330M-14(2021)** 目前為 Active，適用於 exterior windows、doors、skylights、curtain walls 的 uniform static air pressure structural performance test。

它可以作 assembly structural performance test，但不是：

- hardware fatigue test
- screw pull-out equation
- frame member design specification
- operating-cycle test

## Pre-test / post-test function

若 project specification 要求 operability before / after pressure loading，應明確保存：

- test sequence
- pressure levels
- duration
- pre-load operating condition
- post-load operating condition
- observed permanent deformation / damage
- acceptance source

AI 不得自行把「未破壞」等同「可正常操作」。

## Modification / substitution review

活動窗替代／改版至少應重新比對：

- sash dimensions / mass
- glass / infill
- profile / reinforcement
- corner construction
- hinge / stay / lock / restrictor model
- quantity / spacing
- fasteners
- frame anchorage
- gasket / seal configuration
- product rating / test coverage

若改動超出 test / certification coverage，應標示 `verification required`。

## Calculation + test traceability

推薦輸出：

```text
Design assumptions
↓
Sash/frame calculation
↓
Hardware reactions
↓
Fastener/local extrusion checks
↓
Whole-product test requirement
↓
Test evidence / scope
↓
Final status
```

若只有 calculation、沒有專案要求的 product test evidence，狀態可為：

`CALCULATION_PASS / TEST_PENDING`

而不是單一 `PASS`。

## AI guard

不得：

- 用 NAFS rating 取代 hardware connection calculation
- 用 E330 PASS 取代 life-cycle durability
- 用 AAMA 910 當單純 wind-pressure strength equation
- 假設任何尺寸／五金改動仍在原 test coverage
- 把無破壞等同 operability 合格

## Public sources

- FGIA Store — AAMA/WDMA/CSA 101/I.S.2/A440-26
- FGIA Store — AAMA 910-24
- ASTM E330/E330M-14(2021)

> 本頁只保存 public performance-routing logic，不保存非公開產品測試報告或專案 acceptance values。