---
title: "支承條件與複合作用（Composite Action）"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 支承條件與複合作用（Composite Action）

## Support model 必須 explicit

帷幕 framing 的 preliminary sizing 不得把所有構件預設成 simply supported 或 fixed-fixed。

至少應明確記錄：

- support locations
- translational restraint
- rotational restraint
- sliding / pinned / fixed / semi-rigid assumption
- splice / sleeve behavior（若有）
- whether support stiffness is modeled or idealized

若 support condition 不明，結果應標記 `INCOMPLETE` 或 `PROVISIONAL`，而不是由 AI 自行猜測。

## Male / Female mullion composite action

unitized / interlocking framing 常有 male / female profiles 或多件式組合截面。

不得無條件假設 full composite action，也不得只因兩件 profile 互相卡合就直接：

`I_effective = I_male + I_female`

有效組合 stiffness / section property 應至少來自以下其中之一：

1. 使用者／設計者輸入已驗證 effective properties；
2. 經驗證的 company / project engineering rule；
3. 有明確 mechanical model 支持的 composite-action calculation；
4. test / FEA / other validated evidence。

## 為什麼不能直接相加

實際 interaction 可能受：

- interlock geometry
- contact / clearance
- screw / fastener spacing
- friction
- seal / gasket constraint
- splice behavior
- local deformation
- load direction
- positive / negative pressure

影響，因此 full composite、partial composite、independent action 可能得到不同結果。

## Axis definition

Section property 必須配合截面 local axes 與實際 load direction。

不要依變數名稱自動猜：

- `Ix = wind direction`
- `Iy = dead-load direction`
- `x = strong axis`

應保存 CAD / calculation axis definition，並明確指定每個 load case 的 bending axis。

## Status recommendation

對 support / composite assumption 可使用：

- `confirmed`
- `provisional`
- `unknown`

`unknown` 不得產生無條件 PASS。

## 相關頁面

- [Mullion / Transom Design Baseline](../framing/mullion-transom-design-baseline.md)
- [Required Section Properties](required-section-properties.md)

> 本頁保存建模 guardrails，不提供任何特定 curtain-wall system 的預設支承或 composite factor。