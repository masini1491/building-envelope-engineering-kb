---
title: "面板與補強材連接分析"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 面板與補強材連接分析

## 角色

Panel-to-stiffener connection 是 panel skin 與 stiffener 之間真正傳遞 shear / peel / bearing / local force 的介面。若這一層未驗證，stiffener 的 nominal section stiffness 不能直接視為已參與整體受力。

## 常見連接類型

- adhesive bond
- structural tape / bonded strip（僅在產品／設計基準允許時）
- stud
- rivet
- screw
- weld
- clip / mechanical engagement
- mixed connection

不同類型應分別處理，不能只用一個通用「connector capacity」。

## 荷載傳遞

至少要回答：

1. connection 要傳遞的是 in-plane shear、normal peel/tension，還是兩者？
2. force 是連續 distributed 還是 discrete fastener force？
3. 是否有 eccentricity / offset？
4. 是否允許 slip？
5. 是否有 thermal differential movement？
6. stiffener end force 如何進入 perimeter support？

## 離散緊件

使用 stud / screw / rivet 時，至少檢查：

- fastener shear / tension
- tension-shear interaction where applicable
- panel bearing
- stiffener bearing
- pull-out / thread stripping where applicable
- tear-out / edge distance
- local sheet deformation
- group effect / eccentricity when applicable

相關方法可路由至 `structural-design/connections/`。

## 黏著／膠合介面

黏著連接至少需要：

- actual adhesive/product system
- substrate preparation
- bond width / thickness
- temperature / environment
- long-term / creep effects
- shear / peel design basis
- compatibility / durability
- quality-control process

AI 不得自行把 adhesive interface 定義成 rigid tie，也不得只靠短期 coupon strength 宣稱 façade panel connection 已完成驗證。

## 焊接連接

若 stiffener 以 weld 與 panel / return 連接，需另外考慮：

- weld type / geometry
- heat-affected region
- panel distortion
- local stress
- corrosion / finish repair

鋁材焊接不可直接套用 steel weld strength equation。

## 連接件間距

Spacing 同時影響：

- interface shear transfer
- local panel deformation
- stiffener participation
- peel concentration
- oil-canning / read-through risk

所以 connector spacing 不只是 strength 問題，也可能控制完成面品質。

## FEA 表示方式

在 panel FEA 中，interface 可依 evidence 採：

- rigid tie
- discrete connector
- spring / connector element
- contact / slip model
- bonded cohesive representation

但模型選擇必須有來源。`tied` 只是 solver option，不是 engineering evidence。

## AI 防呆

不得：

- 因 panel 與 stiffener 接觸就假設 full composite
- 把 fastener-body PASS 當成 interface PASS
- 忽略 pull-out / bearing / local sheet deformation
- 把 adhesive short-term coupon strength 當 long-term façade design strength
- 把 connector spacing 從非公開專案照搬成通用 spacing

## 相關頁面

- [Fastener Group Analysis](../../structural-design/connections/fastener-group-analysis.md)
- [Screw Pull-out and Thread Engagement](../../structural-design/connections/screw-pullout-and-thread-engagement.md)
- [Local Extrusion Failure](../../structural-design/connections/local-extrusion-failure.md)
- [Weld Group Analysis](../../structural-design/connections/weld-group-analysis.md)

> 本頁只定義 interface design workflow；具體 resistance 必須回到實際 connector / adhesive / weld design basis。