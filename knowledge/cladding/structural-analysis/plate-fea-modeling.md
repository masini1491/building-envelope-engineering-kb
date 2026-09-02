---
title: "Plate / Shell FEA 建模與結果判讀"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# Plate / Shell FEA 建模與結果判讀

## 目的

本頁定義 façade metal panel / stiffener plate-shell analysis 的最低可重現資訊。FEA 的價值不在於輸出彩色 contour，而在於模型假設、數值收斂與結果 interpretation 可被另一位工程師重建與檢查。

## 最低模型資訊

至少保存：

### Geometry

- panel dimensions
- thickness
- folds / returns / openings
- stiffener geometry / section
- offsets / eccentricities
- connector locations

### Elements

- shell / plate / beam / solid element type
- element formulation when material to interpretation
- nominal element size / mesh strategy
- local refinement region

### Material

- `E`
- `ν`
- yield / design strength if strength check is performed
- material provenance

### Boundary conditions

- restrained translations
- restrained rotations
- symmetry condition
- contact / gap
- support line / point
- connector representation

### Loads

- pressure magnitude and sign
- load case source
- distributed / point / line load
- gravity / dead load if included
- load combinations or factors, with source

### Interface assumptions

- panel-to-stiffener tie / slip / connector / spring
- stiffener end condition
- perimeter-frame interaction
- fastener stiffness if modeled

## Mesh convergence

至少對 governing result 做 mesh-sensitivity check。推薦記錄：

- baseline mesh size
- refined mesh size
- change in global deflection
- change in representative stress away from singularities
- change in connector reaction

若 mesh refinement 造成 peak stress 持續增加但 global response 收斂，應判斷是否為 idealized singularity，而不是用無限增大的 peak node stress直接做 acceptance。

## Stress result selection

應明確說明讀的是：

- membrane stress
- bending stress
- top / bottom surface stress
- principal stress
- von Mises stress
- section / beam stress
- averaged or unaveraged nodal result

不同 quantity 的工程意義不同；不得只寫「max stress」。

對 ductile metal yielding check 常可能關注 equivalent stress，但 local buckling、fatigue、weld、thin-sheet connection 或 code-specific checks 可能要求不同 response quantity。

## Linear vs nonlinear

### Linear static

適合 elastic small-deflection response 的第一層分析與 sanity check。

### Geometric nonlinear

當 out-of-plane deflection 與 thickness / geometry 相比已不可忽略，membrane action 或 large displacement 可能影響 response 時，應評估 geometric nonlinearity。

### Buckling

Eigenvalue buckling 可用於識別 mode / sensitivity，但不能單獨視為 actual nonlinear ultimate capacity。

若 buckling 是重要 failure mode，可能需要：

- initial imperfection
- geometric nonlinear analysis
- material nonlinear analysis
- validated test / design method

## Connection modeling

將 connector 建成 rigid tie 會提高 composite action 與 stiffness。若實際 fastener / adhesive 會 slip 或 deform，應以 discrete connector / spring / contact 等更適當模型處理，或進行 bounding analysis。

## Reactions

FEA 不只應讀 panel stress；還應輸出：

- perimeter support reaction
- stiffener end reaction
- individual / grouped connector demand when model supports it

這些反力應接續進 fastener / bracket / framing load path。

## Sanity checks

正式使用結果前至少做：

- total applied load vs total reaction equilibrium
- symmetry check when geometry / load symmetric
- simplified plate / beam analytical comparison when applicable
- deflected-shape plausibility
- load-path plausibility
- unit consistency

若 FEA 與簡化模型差異很大，不應先假設 FEA 一定正確；先查 boundary、units、offsets、connectivity、mesh、load application 與 result interpretation。

## Reporting minimum

一份可稽核 FEA 摘要至少包含：

1. model purpose
2. geometry / simplifications
3. material
4. element type
5. mesh
6. boundary conditions
7. interfaces / connectors
8. load cases
9. convergence / validation evidence
10. governing displacement
11. governing stress quantity and location interpretation
12. reactions
13. assumptions / exclusions
14. acceptance criterion source

## AI guard

不得：

- 只看到 contour screenshot 就接受結論
- 未知 units 時讀取結果
- 把 unaveraged singular node stress 當 universal governing value
- 將 linear static model 說成已證明 buckling safety
- 忽略 connector / interface stiffness
- 因 solver 顯示 PASS 就省略 criterion provenance

## Related

- [Metal Panel Analysis](metal-panel-analysis.md)
- [Stiffener Analysis](stiffener-analysis.md)
- [Panel-to-Stiffener Connection](panel-to-stiffener-connection.md)

> 本頁是 solver-independent FEA governance；不綁定特定商用軟體。