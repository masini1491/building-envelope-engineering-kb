---
title: "帷幕牆框架結構分析 Router"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
document_type: "router"
domain: "structural-design.framing"
canonical_key: "structural-design.framing.router"
---

# 帷幕牆框架結構分析 Router

本目錄處理 mullion / transom 與相關框架構件的 global member mechanics、支承模型、截面組合與服務性反應。

## 主要頁面

- [`mullion-transom-design-baseline.md`](mullion-transom-design-baseline.md)：直料／橫料結構設計基線。
- [`continuous-mullion-analysis.md`](continuous-mullion-analysis.md)：multi-span、support DOF、reaction 與 sensitivity。
- [`biaxial-bending-and-resultant-deflection.md`](biaxial-bending-and-resultant-deflection.md)：雙軸彎曲與合成變位。
- [`multi-part-extrusion-load-sharing.md`](multi-part-extrusion-load-sharing.md)：多件擠型 composite-action 與 common-axis mechanics。
- [`splice-and-sleeve-modeling.md`](splice-and-sleeve-modeling.md)：splice / sleeve 的 directional DOF 與 continuity model。
- [`glass-edge-relative-deflection.md`](glass-edge-relative-deflection.md)：玻璃邊緣相對支承變位與 glazing interface。

## 邊界

本目錄的 member-level 結果不取代：

- [`../connections/`](../connections/) 的局部連接與 extrusion failure；
- [`../secondary-support/`](../secondary-support/) 的主結構介面；
- [`../../structural-glass/`](../../structural-glass/) 的結構玻璃專屬 mechanics。

> Global framing PASS 不代表 connection、glass support、anchor 或 secondary support 自動 PASS。