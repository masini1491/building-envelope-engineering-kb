---
title: "補強材結構分析"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 補強材結構分析

## 角色

Stiffener 的功能是將 panel skin 的面外荷載轉成較有效率的 beam / frame action，降低 panel deformation，並把反力傳至 perimeter frame 或其他支承。

但 stiffener 是否真正有效，取決於：

- section stiffness
- spacing
- orientation
- attachment stiffness
- load transfer length
- end support
- panel-to-stiffener compatibility

因此「加了補強料」不等於結構自動改善。

## Modeling choices

常見簡化包括：

- beam element stiffener + shell panel
- shell / solid stiffener geometry
- equivalent transformed section（僅在 composite action 有證據時）

若使用 beam + shell，至少要保存：

- beam section properties
- beam centroid / offset relative to panel mid-surface
- connection type to shell
- end releases / support
- material

## Composite-action guard

Panel skin 與 stiffener 可透過 adhesive、stud、rivet、screw、weld 或其他方式連接。不同連接會有不同 slip / peel / shear-transfer behavior。

除非 interface 已有足夠證據，不得直接：

`I_effective = I_panel + I_stiffener`

或把 panel + stiffener 建成完全 tied 的 composite section。

## Stiffener demand

至少檢查：

- bending
- shear
- local buckling
- torsion where applicable
- end reaction
- connector force
- local bearing / wall deformation

若補強料是 open thin-walled extrusion / channel，torsion 與 local deformation 可能不可忽略。

## End condition

Stiffener 的 end condition 對效果很敏感：

- free-ended reinforcement
- bearing to perimeter return
- mechanically fastened end
- welded end
- continuous through support

不能用「stiffener length = panel height」就推定兩端 fixed。

## Spacing / load-sharing

多支相同 stiffener 不代表每支平均承受 `total load / n`。Panel plate action、edge support、stiffener spacing、relative stiffness 與 connection stiffness 都會改變 load distribution。

若需要精確 reaction，應由 plate/shell model 或經驗證 analytical model取得。

## AI 防呆

不得：

- 把 stiffener 數量直接當 load-sharing 比例
- 把 adhesive bond 默認 rigid
- 把 beam centroid 忽略 offset 接到 shell mid-plane
- 把 free-ended stiffener 當 fixed-ended
- 只驗證 stiffener stress，不驗證 connector / panel local response

## 相關頁面

- [Metal Panel Analysis](metal-panel-analysis.md)
- [Panel-to-Stiffener Connection](panel-to-stiffener-connection.md)
- [Plate / Shell FEA Modeling](plate-fea-modeling.md)

> 補強料的 effectiveness 必須由完整 load path 證明，不得只以截面 `I` 大小判定。