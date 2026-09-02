---
title: "金屬板／補強材結構分析"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 金屬板／補強材結構分析

本目錄處理 solid aluminum panel、folded tray panel、stiffened metal panel 與其他需要以 plate / shell / beam 模型評估的外牆面板。

核心 load path：

`wind pressure → panel skin → folded return / stiffener → stud / rivet / screw / adhesive / weld → perimeter frame / bracket → façade framing`

## 核心原則

1. Panel 本體、stiffener、panel-to-stiffener connection 與 perimeter attachment 是不同 failure modes。
2. FEA 彩色 contour 不是計算方法；模型必須能重建 geometry、material、boundary condition、load、connection assumption、mesh 與 result extraction。
3. Plate / shell stress 不得直接拿一個局部 peak node 當 governing design value，必須先判斷 mesh sensitivity、singularity 與所採 design basis。
4. 若 stiffener 與 panel 的連接無法證明 full composite，不能把兩者直接視為單一等效厚板。
5. Wind-load analysis 與 visual flatness / oil canning 是相關但不同問題。
6. 所有 allowable / resistance / deflection criterion 仍需 public standard、manufacturer data 或 project-approved source。

## 相關頁面與 routing

- [Metal Panel Analysis](metal-panel-analysis.md)
- [Stiffener Analysis](stiffener-analysis.md)
- [Panel-to-Stiffener Connection](panel-to-stiffener-connection.md)
- [Plate / Shell FEA Modeling](plate-fea-modeling.md)
- [Metal Composite and Honeycomb Panels](../metal-composite-and-honeycomb-panels.md)
- [Aluminum Panel Flatness and Oil Canning](../aluminum-panel-flatness-and-oil-canning.md)

## 試驗與分析的區分

ASTM E330/E330M-14(2021) 目前仍列為 Active，提供 exterior windows / curtain walls / doors 在 uniform static air pressure 下的 structural performance test method。它可用來驗證特定 specimen / assembly，但不等於一套 metal-panel FEA design equation。

因此：

`analysis model → predicted response`

與

`full-size / assembly test → observed performance`

應分別保存，必要時互相校核，但不能互相冒充。

## 公開來源 routing

- ASTM E330/E330M-14(2021) — uniform static air-pressure structural performance test。
- The Aluminum Association, Aluminum Design Manual 2020 — aluminum structural member / plate design routing。
- applicable product evaluation / manufacturer structural data for proprietary composite or honeycomb panels。

> 本目錄不保存非公開專案的 panel 尺寸、stiffener layout、mesh 圖、荷載或 FEA screenshot。