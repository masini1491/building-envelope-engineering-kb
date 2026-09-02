---
title: "Calculation Status 與 Traceability"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# Calculation Status 與 Traceability

## Status model

建議 engineering calculation / verification 使用：

- `PASS`
- `WARNING`
- `FAIL`
- `INCOMPLETE`

### INCOMPLETE

資料不足時必須用 `INCOMPLETE`，不得視為 PASS。

典型例子：

- 有 `I` 但沒有 `S` 或 extreme-fiber distance，僅能做 deflection verification；
- support condition unknown；
- composite action unknown；
- allowable stress missing；
- axis definition unclear；
- governing standard / edition 尚未確認且會影響結果。

## WARNING 不是 safety factor

若 workflow 使用 utilization warning threshold，例如 0.90，這只是設計管理提醒，不是規範 safety factor，也不得改變 capacity。

任何 threshold 必須：

- 可設定；
- 可關閉；
- 與 structural capacity / allowable value 分開保存。

## Calculation trace

每個結果至少應能回溯：

### Inputs

- load case / pressure
- tributary geometry
- span
- support model
- material / E
- allowable stress
- deflection criterion
- section properties
- axis definition

### Derived values

- line / point load
- allowable deflection
- reactions
- shear / moment
- trial / actual deflection
- required `I` / `S`

### Method

- analytical formula / beam solver / FEA / other
- assumptions
- source standard / criteria
- edition / revision when relevant

### Result

- required value
- actual value
- utilization / ratio
- governing case
- governing axis
- status
- warnings / missing inputs

## Auditability rule

不得只輸出 `PASS` / `FAIL` 而不保留 calculation trace。

若不同方法或 reference result 不一致，不得偷偷調整公式讓數字硬對上；應先檢查：

- units
- boundary condition
- load distribution
- tributary definition
- section properties
- axis
- rounding
- criteria / standard edition

## Data integrity

任何未確認資料都應保留 provenance / status，例如：

- `estimated`
- `CAD`
- `supplier`
- `user`

以及：

- `provisional`
- `confirmed`

不得靜默把 provisional data 升級成 confirmed。

> 這套 status / traceability model 可供未來 calculator、spreadsheet 或 AI review 共用。