---
title: "帷幕牆前期結構尺寸評估"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 帷幕牆前期結構尺寸評估

本目錄整理 curtain-wall preliminary structural sizing 的通用方法與資料模型。

目的是在實際 extrusion / connection detail 尚未完全定案時，以可追溯的 load、span、support、material 與 design criteria 先求得需要的 section performance；實際截面完成後，再以 actual section properties 做 verification。

## 核心原則

1. Preliminary sizing 不等於正式結構計算或簽證。
2. Design pressure 與 test pressure 必須分開。
3. Positive / negative pressure 應保留為獨立 load cases。
4. Deflection requirement 對應 required moment of inertia `I`。
5. Bending-strength requirement 對應 required section modulus `S`。
6. Support condition、axis definition、composite action 必須 explicit。
7. Missing data 應回傳 `INCOMPLETE`，不得默認 `PASS`。
8. 所有結果應保留 inputs、derived values、method、assumptions 與 governing case。

## Routing

- [Design Pressure vs Test Pressure](design-vs-test-pressure.md)
- [Required Section Properties](required-section-properties.md)
- [Support and Composite Action](support-and-composite-action.md)
- [Calculation Status and Traceability](calculation-status-and-traceability.md)
- [Mullion / Transom Design Baseline](../framing/mullion-transom-design-baseline.md)
- [Taiwan Design Wind Pressure Workflow](../wind/taiwan-design-wind-pressure-workflow.md)

## Data schemas

機器可讀資料模型位於 repository `/schemas/`：

- `material.schema.json`
- `load-case.schema.json`
- `section-properties.schema.json`
- `deflection-criterion.schema.json`

這些 schema 是 knowledge interchange / future calculator foundation，不是任何特定專案資料格式。

> 本目錄刻意不保存公司內部 criteria、專案名稱、project-specific loads、actual section values 或 proprietary calculation fixtures。