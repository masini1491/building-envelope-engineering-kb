---
title: "結構玻璃有限元素分析建模防呆"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 結構玻璃有限元素分析建模防呆

## 適用範圍

本頁提供 structural glass 使用 FEA 時的最低建模檢查項目，避免 AI 或工程師把漂亮的 contour plot 當成模型已被驗證。

## 模型定義

建模前明確定義：

- element type：frame / shell / solid / layered shell 等
- glass representation：monolithic、effective section、layered laminate
- interlayer representation：effective stiffness 或 explicit material model
- support condition：fixed / pinned / contact / spring / gap / slot
- geometric nonlinearity 是否需要
- contact / bearing 是否需要
- load cases / combinations / imposed movements

## 驗證層級

至少做：

1. hand calculation / simplified model sanity check
2. mesh / discretization sensitivity（若 local stress controlling）
3. reaction balance
4. deformation shape plausibility
5. stress-component interpretation
6. support / boundary-condition sensitivity
7. comparison with applicable standard / public technical method
8. test correlation when the behavior falls outside standard scope

## 全域模型與局部模型

大型 glass fin / façade model可用 global model取得：

- member forces
- deflection
- support reactions
- overall movement response

但 drilled hole、bolt bearing、clamp、shoe、small contact zone 等可能需要 local submodel / solid contact model。

不得直接用 coarse global shell / frame model 的 nominal stress 取代孔邊局部 principal stress。

## 線性模型防呆

若可能存在：

- large deflection
- contact opening / closing
- support slip
- buckling / stability
- sealant nonlinear response

則 linear static model可能只能作初步 screening，不得無條件視為 final design model。

## 文件化最低要求

公開 knowledge base 不保存專案模型，但方法文件應提醒正式 calculation package 至少記錄：

- software / version
- element formulation
- mesh strategy
- material properties and sources
- boundary conditions
- load cases
- combinations
- acceptance criteria
- model validation checks

## 不可推論事項

- FEA result = correct because solver converged
- finer mesh always = more accurate without correct physics
- global reaction distribution is automatically realistic
- effective-thickness beam model can predict local drilled-hole stresses

> FEA 是工程模型，不是證據本身；模型假設、verification 與 applicable test / standard 才決定結果可信度。