# 帷幕檢測／監測 GitHub 專案參考（Façade Inspection／Monitoring）

查證日期：2026-09-11

本頁整理 façade inspection、computer vision、condition monitoring / SHM、test automation 與 installation-survey tooling 相關公開 GitHub repository。全部屬 **NON-NORMATIVE REFERENCE**。

## 狀態監測（Condition monitoring）

### `CurtainWallMonitoringPlatform/CurtainWallWeb-Backend`

https://github.com/CurtainWallMonitoringPlatform/CurtainWallWeb-Backend

玻璃幕牆振動資料可視化監管平台後端。可研究 device → monitor → web API / visualization 的資料流與 SHM backend architecture。公開內容不足以支持 sensor accuracy、damage criterion 或 engineering condition rating，因此只作 architecture reference。

### `CurtainWallMonitoringPlatform/CurtainWallWeb-Frontend`

https://github.com/CurtainWallMonitoringPlatform/CurtainWallWeb-Frontend

可搭配 backend 觀察 monitoring UI；目前 engineering reference value 主要仍在整體 architecture，而非判定方法。

## 試驗自動化／資料擷取（Test automation／DAQ）

### `openDAQ/openDAQ`

https://github.com/openDAQ/openDAQ

**分級：C — 高價值支援工具。** 2026-09-11 查證 `main` snapshot：`1b2d24027fa30f80fb1837c1df8d3a02dec282a3`。

openDAQ 提供跨 DAQ device 的 generic API、property/configuration、measurement streaming 與 signal-processing framework，並支援 OPC UA structure/property transfer、WebSocket streaming，以及 MQTT／XCP 等整合方向。對 façade performance-test architecture，可研究：

`pressure / flow / displacement / event sensors`
→ `device abstraction`
→ `timestamped signal stream`
→ `processing / derived channels`
→ `test evidence export`

它不定義 ASTM/AAMA/CNS 試驗壓力、duration、calibration tolerance 或 acceptance criterion。

### `opentap/opentap`

https://github.com/opentap/opentap

**分級：C — 高價值支援工具。** OpenTAP 是 automated-test sequencing／execution framework，提供 extensible plugin architecture、CLI、result infrastructure 與 test-plan execution。

與 openDAQ 的角色可分層理解：

`openDAQ = instrumentation / acquisition abstraction`

`OpenTAP = test plan / sequence / execution orchestration`

兩者可作未來 full-scale façade laboratory automation 的 architecture reference，但不得把 test runner 的 `PASS` 當 governing standard 的工程判定。

## 點雲／安裝偏差量測（Point cloud／installation survey）

### `CloudCompare/CloudCompare`

https://github.com/CloudCompare/CloudCompare

**分級：C — 支援工具。** 可研究 point-cloud／mesh registration、ICP fine registration、cloud-to-cloud／cloud-to-mesh distance 與 deviation visualization。適合 façade installation survey、as-built geometry reconciliation 與 tolerance heatmap 的人工／半自動 workflow。

### `PDAL/PDAL`

https://github.com/PDAL/PDAL

**分級：C — 支援工具。** PDAL 適合把 point-cloud processing 寫成 deterministic pipeline，例如 reader → filter → transform／crop／classify → writer，並保留可重現的 processing configuration／metadata。可作批次 façade survey automation backend。

建議研究鏈：

`laser scan / point cloud`
→ registration / coordinate reconciliation
→ design/reference mesh
→ deviation field
→ tolerance mapping
→ engineering disposition

**幾何 deviation ≠ acceptance conclusion。** Scanner accuracy、control points、registration residual、coordinate transform、design-model revision、tolerance source 與 responsibility boundary 均需另行驗證。

## 電腦視覺／缺陷基準（Computer vision／defect benchmark）

### `Whitneyyyyy/DefectBench`

https://github.com/Whitneyyyyy/DefectBench

Building façade inspection multimodal benchmark，包含 defect classification / counting / localization / segmentation 等評估思路。適合研究 façade defect taxonomy、annotation schema 與 AI evaluation；影像辨識不能直接推出剩餘結構容量或維修等級。

### `ailton-santos/Deep_Facade_Inspector`

https://github.com/ailton-santos/Deep_Facade_Inspector

可研究 Drone/Image Capture → preprocessing → tiled detection → pathology classification → georeferenced report → maintenance workflow。核心 dataset / trained weights / proprietary detection algorithm 並非完整公開，因此只作 pipeline architecture reference。

## 負面軟體案例：`almona02/almona-portfolio-forge` 的 ASTM E1300 compliance code

https://github.com/almona02/almona-portfolio-forge

曾查見名為 ASTM E1300 compliance 的程式含 placeholder / simplified logic、default PASS 類行為。保留此案例的目的不是推薦使用，而是提醒：

- class / function / UI 名稱寫著標準編號，不等於真正實作該標準；
- `compliant = true` 不是 engineering proof；
- hard-coded unknown number / placeholder / default PASS 應視為 invalid / incomplete。

**不得以此 implementation 作玻璃工程設計依據。**

## 研究缺口（Research gaps）

仍值得研究／自研，但目前尚未由上述工具自動解決：

- façade-specific performance-test procedure adapter 與 standard-aware acceptance layer；
- pressure / flow / displacement / event 的 calibrated synchronization contract；
- sensor-calibrated curtain-wall SHM；
- defect detection → verified engineering condition rating；
- point-cloud deviation → project-specific installation tolerance disposition。

> Inspection AI、DAQ、test runner 與 survey tool 應輸出 observation / evidence；工程 acceptance 必須由 governing source 與可追溯 review contract另外決定。
