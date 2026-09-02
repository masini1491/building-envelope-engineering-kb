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

> 完整 load path 中，哪些 failure modes 已被檢查？哪些被排除？哪些因資料不足仍是 `INCOMPLETE`？所有會改變 demand / capacity / utilization 的 factor 是否都能追溯？

## 建議審查順序

對 project-specific calculation review，優先流程為：

`project specification / approved criteria`

→ `Project Design Basis Sheet`

→ `drawings / geometry / material data`

→ `engineer's structural calculation`

→ `design-factor / hidden-multiplier audit`

→ `KB engineering methodology / failure-mode map`

→ `spec-to-calc compliance + engineering review`

這可以避免只檢查公式 mechanics，卻沒有先確認該專案真正要求的 load、criterion、factor、calculation scope 與 test acceptance。

## Review hierarchy

1. **Project specification extraction** — 先建立 Project Design Basis；不要直接從計算書猜 project criteria。
2. **Design basis** — governing standard / edition / project criterion 是否明確。
3. **Factor audit** — 所有 load factor、safety factor、allowable conversion、resistance treatment、test multiplier、project-specific factor 與 reported ratio definition 是否具名、具來源且方向正確。
4. **Load sources** — wind、dead、seismic、movement、maintenance / concentrated load 等是否完整。
5. **Load generation** — pressure / mass / imposed displacement 是否正確轉成 line / point / nodal demand。
6. **Structural model** — span、support DOF、splice、composite action、axis、connection stiffness 是否明示。
7. **Global member response** — framing / panel / glass / sash 的 force、stress、deflection。
8. **Connection transfer** — fastener group、weld group、bearing、pull-out、local section、anchor。
9. **Movement compatibility** — thermal / story drift / glass edge / stack joint / sealant / gasket。
10. **Special subsystems** — operable elements、metal panel stiffener、structural glass、special attachments。
11. **Performance verification** — analysis 與 mock-up / component / assembly test 的角色是否分清。
12. **Coverage status** — `PASS / WARNING / FAIL / INCOMPLETE / NOT_APPLICABLE` 是否有 traceable basis。

## Routing

- [Project Specification → Structural Design Basis Extraction](project-specification-extraction.md)
- [Design Factor／Safety Factor／隱藏倍率稽核](design-factor-and-hidden-multiplier-audit.md)
- [Structural Calculation Review Checklist](structural-calculation-review-checklist.md)
- [Façade Structural Failure-Mode Map](failure-mode-map.md)
- [Coverage / Completeness Status](coverage-and-completeness.md)

Machine-readable routing：

- `/schemas/project-design-basis.schema.json`
- `/schemas/design-factor.schema.json`
- `/schemas/structural-coverage.schema.json`

## 核心原則

### Calculation correctness ≠ calculation completeness

一個螺栓 shear equation 算得完全正確，如果 load path 還漏掉 eccentricity、bearing、pull-out 或 local extrusion failure，整個 connection calculation 仍不完整。

### A numerical PASS ≠ a traceable PASS

若最後 utilization / safety ratio 看似合格，但中間的 factor、allowable transformation、capacity reduction 或 ratio definition 無法追溯，該 PASS 不可靠。

尤其不得只因某 factor 看起來「比較保守」就略過審查；conservative-looking treatment 仍可能 double count、混用 design philosophy、污染 test / design routing，或遮蔽另一個 non-conservative assumption。

### Engineering PASS ≠ project-specification compliance PASS

例如一個 member 的 bending mechanics 可以正確，但若使用了錯誤的 project deflection criterion，則應分開輸出：

- `engineering_method: PASS`
- `project_specification_compliance: FAIL`

### PASS is local unless scope is explicit

任何 `PASS` 必須附帶 scope，例如：

- `member_flexure: PASS`
- `fastener_body_shear: PASS`
- `weld_group_demand: PASS`
- `factor_audit: PASS`

不能只寫一個沒有範圍的 `STRUCTURE: PASS`。

### Missing evidence is not a favorable assumption

若 criterion、allowable、factor source、support、composite action、connection geometry 或 load source 缺失，狀態應是 `INCOMPLETE`，而不是自行補入最方便的值。

## Public-safety rule

本 review framework 可由非公開專案規範與計算實務協助辨識常見 requirement / failure modes，但 public repository 只保存一般化 extraction / review framework 與公開可驗證方法；不得保存專案名稱、尺寸、荷載、criterion、factor、圖號、節點、截圖或私人 provenance。

Project Design Basis Sheet、factor ledger、spec-to-calc matrix 與 project-specific review result 均屬當次 project context，不應 commit 到 public repository。

> 本頁是 structural review router，不取代 governing code、專業結構設計或 project-specific calculation。