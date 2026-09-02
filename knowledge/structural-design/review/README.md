---
title: "帷幕牆結構計算審查與 Failure-Mode Routing"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 帷幕牆結構計算審查與 Failure-Mode Routing

本目錄不是另一套計算公式，而是把 repository 既有 structural knowledge 串成一個**coverage / completeness review layer**。

目標是讓工程師或 AI 在面對一套 façade system、節點、計算書或 future calculator output 時，不只問：

> 某一條公式有沒有算對？

還要問：

> 完整 load path 中，哪些 failure modes 已被檢查？哪些被排除？哪些因資料不足仍是 `INCOMPLETE`？

## Review hierarchy

1. **Design basis** — governing standard / edition / project criterion 是否明確。
2. **Load sources** — wind、dead、seismic、movement、maintenance / concentrated load 等是否完整。
3. **Load generation** — pressure / mass / imposed displacement 是否正確轉成 line / point / nodal demand。
4. **Structural model** — span、support DOF、splice、composite action、axis、connection stiffness 是否明示。
5. **Global member response** — framing / panel / glass / sash 的 force、stress、deflection。
6. **Connection transfer** — fastener group、weld group、bearing、pull-out、local section、anchor。
7. **Movement compatibility** — thermal / story drift / glass edge / stack joint / sealant / gasket。
8. **Special subsystems** — operable elements、metal panel stiffener、structural glass、special attachments。
9. **Performance verification** — analysis 與 mock-up / component / assembly test 的角色是否分清。
10. **Coverage status** — `PASS / WARNING / FAIL / INCOMPLETE / NOT_APPLICABLE` 是否有 traceable basis。

## Routing

- [Structural Calculation Review Checklist](structural-calculation-review-checklist.md)
- [Façade Structural Failure-Mode Map](failure-mode-map.md)
- [Coverage / Completeness Status](coverage-and-completeness.md)

## 核心原則

### Calculation correctness ≠ calculation completeness

一個螺栓 shear equation 算得完全正確，如果 load path 還漏掉 eccentricity、bearing、pull-out 或 local extrusion failure，整個 connection calculation 仍不完整。

### PASS is local unless scope is explicit

任何 `PASS` 必須附帶 scope，例如：

- `member_flexure: PASS`
- `fastener_body_shear: PASS`
- `weld_group_demand: PASS`

不能只寫一個沒有範圍的 `STRUCTURE: PASS`。

### Missing evidence is not a favorable assumption

若 criterion、allowable、support、composite action、connection geometry 或 load source 缺失，狀態應是 `INCOMPLETE`，而不是自行補入最方便的值。

## Public-safety rule

本 review framework 可由非公開專案計算實務協助辨識常見 failure modes，但 public repository 只保存一般化分類與公開可驗證方法；不得保存專案名稱、尺寸、荷載、圖號、節點、截圖或私人 provenance。

> 本頁是 structural review router，不取代 governing code、專業結構設計或 project-specific calculation。