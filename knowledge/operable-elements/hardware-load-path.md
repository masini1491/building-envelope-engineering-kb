---
title: "活動窗五金受力路徑"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 活動窗五金受力路徑

## 角色

Hinge、friction stay、pivot、lock、keeper、restrictor、stopper 等 operable hardware 不是 isolated component。其 demand 來自 sash / glass / wind / operating load，並透過 fastener 與 local extrusion 回到 outer frame。

## Generic load path

`glass / sash load`

→ `sash member`

→ `hardware body`

→ `hardware fasteners`

→ `local extrusion / reinforcement`

→ `outer frame`

→ `curtain-wall framing`

每一層都應有獨立 verification。

## Hardware reactions

Hardware reaction distribution 受下列因素影響：

- number and spacing of hinges / stays / locks
- sash size and stiffness
- center of gravity
- wind-pressure direction
- eccentricity between load path and hardware plane
- frame deformation
- opening configuration
- corner stiffness

因此不得直接假設：

`total force / number of hardware points`

## Dead-load path

玻璃與 sash 自重通常形成持續作用，常由 hinge / pivot / lower support 等主要承受。

應明確區分：

- dead-load supporting hardware
- wind-load restraint hardware
- locking hardware
- movement / guidance hardware

同一個 hardware point 可能同時承担多種 action，但不能因數量相同就假設 load share 相同。

## Wind-load path

正、負風壓可能造成：

- hardware shear reversal
- lock / keeper tension or compression change
- hinge-side reaction redistribution
- sash torsion
- local frame prying

因此 positive / negative case 應保留，不宜過早只取 absolute maximum。

## Eccentricity

五金本體通常與 sash / outer frame 的 centroidal load path 有偏心。可能需要考慮：

- out-of-plane lever arm
- fastener-group torsion
- local bracket bending
- prying

這些 demand 應再路由至 fastener-group 與 local-extrusion analysis。

## Product rating vs installed demand

Manufacturer catalogue / hardware rating 若存在，仍須確認：

- hardware model
- installation orientation
- fastener type
- substrate / extrusion thickness
- reinforcement
- sash mass / size limits
- number of hardware points
- cycle / corrosion class where relevant

不可只看單一 catalogue load 就宣告整個 connection PASS。

## Recommended calculation output

至少保存：

1. hardware type / function
2. support coordinates
3. load cases
4. reaction components per point
5. eccentricity / lever arm
6. fastener-group demand
7. local extrusion / reinforcement demand
8. hardware product rating source
9. assumptions / limitations
10. governing case

## AI guard

不得：

- 平均分配所有 hardware reactions
- 用 hardware body capacity 取代 screw / local extrusion check
- 用 fastener capacity 取代 hardware body verification
- 忽略 positive / negative load reversal
- 忽略 sash dead-load eccentricity
- 將某一 proprietary hardware arrangement 泛化為所有 opening types

## Related

- [Sash / Frame Structural Analysis](sash-frame-analysis.md)
- [Hinge / Lock / Stay Connections](hinge-lock-stay-connections.md)
- [Fastener Group Analysis](../structural-design/connections/fastener-group-analysis.md)
- [Local Extrusion Failure](../structural-design/connections/local-extrusion-failure.md)

> 本頁描述 load path，不提供 proprietary hardware capacity。