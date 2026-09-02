---
title: "帷幕牆結構連接設計 Router"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
document_type: "router"
domain: "structural-design.connections"
canonical_key: "structural-design.connections.router"
---

# 帷幕牆結構連接設計 Router

本目錄處理 façade load path 中的 generic connection mechanics；anchor-to-concrete、structural glass connection、operable hardware 等 specialized subsystem 仍由各自 domain 維護。

## 主要頁面

- [`load-path-and-anchor-reactions.md`](load-path-and-anchor-reactions.md)：由構件反應到 connection / anchor reaction 的 load-path routing。
- [`fastener-group-analysis.md`](fastener-group-analysis.md)：fastener coordinates、centroid、direct + eccentric demand、group mechanics。
- [`weld-group-analysis.md`](weld-group-analysis.md)：任意 weld-group geometry、direct / eccentric load、mechanics 與 capacity 分離。
- [`screw-pullout-and-thread-engagement.md`](screw-pullout-and-thread-engagement.md)：螺絲本體、pull-out / thread stripping 與 engagement evidence。
- [`local-extrusion-failure.md`](local-extrusion-failure.md)：鋁擠型 wall / flange / lip / chase 等局部破壞模式。

## 相關 specialized domain

- [`../../../anchors/anchor-standards-baseline.md`](../../../anchors/anchor-standards-baseline.md)：cast-in / post-installed anchor standards 與 concrete failure routing。
- [`../secondary-support/`](../secondary-support/)：back brace、reaction handoff、supporting steel local effects。

> 連接元件 PASS、connected material PASS、anchor PASS 必須分開判斷；不可用單一 `connection OK` 掩蓋 failure-mode coverage。