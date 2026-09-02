---
title: "Structural Calculation Coverage / Completeness Status"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# Structural Calculation Coverage / Completeness Status

本頁定義 structural review 的狀態語意，避免 `PASS` 被錯用成「整套系統已完成」。

## Recommended statuses

- `PASS`：該**明確 scope** 的 demand / criterion 已有 traceable evidence，且結果符合要求。
- `WARNING`：結果可用，但存在需揭露的假設、敏感性、版本或適用範圍限制。
- `FAIL`：該明確 scope 的 demand 超過 governing criterion，或不符合必要要求。
- `INCOMPLETE`：缺少必要 input、criterion、model、capacity source 或 failure-mode check，無法完成判定。
- `NOT_APPLICABLE`：有工程理由可說明該 failure mode 對本 system / load case 不適用。

## Scope is mandatory

不可只寫：

`PASS`

應寫成例如：

- `mullion_major_axis_flexure: PASS`
- `transom_dead_load_deflection: WARNING`
- `fastener_group_tension_shear: PASS`
- `thread_pullout: INCOMPLETE`
- `seismic_story_drift_compatibility: NOT_APPLICABLE`（需附理由）

## Overall status logic

建議 future calculator / AI review 使用保守的 aggregation：

1. 任一 **applicable critical domain** 為 `FAIL` → overall = `FAIL`。
2. 無 `FAIL`，但任一 applicable critical domain 為 `INCOMPLETE` → overall = `INCOMPLETE`。
3. 無 `FAIL / INCOMPLETE`，但有 `WARNING` → overall = `WARNING`。
4. 所有 applicable critical domains 均 `PASS`，其餘有合理 `NOT_APPLICABLE` → overall = `PASS`。

這個 aggregation 不代表 governing code 的法律判定，而是 calculation-package completeness 的資訊模型。

## Required evidence fields

每個 coverage item 建議至少保存：

```yaml
domain: fastener_group
failure_mode: tension_shear_interaction
status: PASS
load_case: negative_wind
result: ...
criterion: ...
criterion_source: ...
method: ...
assumptions: ...
missing_inputs: []
notes: ...
```

## `NOT_APPLICABLE` guard

`NOT_APPLICABLE` 不能用來跳過不想算的項目。

至少需回答：

- 為何該 failure mode 不存在？
- 是由 geometry、load path、material、support condition 還是 system type 排除？
- 是否對所有 load cases 都不適用，或僅某一 case？

例如「沒有 weld」可以使 weld-group check `NOT_APPLICABLE`；但「目前沒有 weld capacity data」應是 `INCOMPLETE`，不是 N/A。

## `WARNING` guard

適合 `WARNING` 的情形可能包括：

- solver result 對 mesh 有輕微 sensitivity，但 governing conclusion 穩定；
- standard edition current status 已確認，但 project specification 引用舊版且尚待 reconciliation；
- bounding-case analyses 均 PASS，但 semi-rigid stiffness 尚未實測；
- manufacturer data 可支持 preliminary check，但 formal approval 尚未完成。

若 uncertainty 足以改變 PASS / FAIL，應提升為 `INCOMPLETE`，不能只放 warning。

## Coverage matrix

系統級 review 建議至少有：

| Domain | Failure mode | Applicable | Status | Governing case | Source | Notes |
|---|---|---:|---|---|---|---|
| Load | positive wind | yes | ... | ... | ... | ... |
| Framing | flexure | yes | ... | ... | ... | ... |
| Framing | deflection | yes | ... | ... | ... | ... |
| Connection | fastener group | yes | ... | ... | ... | ... |
| Connection | pull-out | yes/no | ... | ... | ... | ... |
| Movement | story drift | yes/no | ... | ... | ... | ... |

## Calculation package complete

只有當：

- design basis 已定義；
- load cases 已定義；
- structural model 已定義；
- applicable critical failure modes 均有結論；
- criteria / capacity 有 provenance；
- movement / connection / local failures 未被 global member PASS 掩蓋；
- calculation trace 可重建；

才適合稱為：

`calculation_package_status = COMPLETE`

否則應為：

`calculation_package_status = INCOMPLETE`

> `COMPLETE` 描述 coverage / traceability，不等同法規審查核准、第三方簽證或施工核可。