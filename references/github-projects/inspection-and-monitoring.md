# Façade Inspection／Monitoring GitHub 專案參考

查證日期：2026-09-02

本頁整理 façade inspection、computer vision、condition monitoring / SHM 相關公開 GitHub repository。全部屬 **NON-NORMATIVE REFERENCE**。

## Condition monitoring

### `CurtainWallMonitoringPlatform/CurtainWallWeb-Backend`

https://github.com/CurtainWallMonitoringPlatform/CurtainWallWeb-Backend

玻璃幕牆振動資料可視化監管平台後端。可研究 device → monitor → web API / visualization 的資料流與 SHM backend architecture。公開內容不足以支持 sensor accuracy、damage criterion 或 engineering condition rating，因此只作 architecture reference。

### `CurtainWallMonitoringPlatform/CurtainWallWeb-Frontend`

https://github.com/CurtainWallMonitoringPlatform/CurtainWallWeb-Frontend

可搭配 backend 觀察 monitoring UI；目前 engineering reference value 主要仍在整體 architecture，而非判定方法。

## Computer vision／defect benchmark

### `Whitneyyyyy/DefectBench`

https://github.com/Whitneyyyyy/DefectBench

Building façade inspection multimodal benchmark，包含 defect classification / counting / localization / segmentation 等評估思路。適合研究 façade defect taxonomy、annotation schema 與 AI evaluation；影像辨識不能直接推出剩餘結構容量或維修等級。

### `ailton-santos/Deep_Facade_Inspector`

https://github.com/ailton-santos/Deep_Facade_Inspector

可研究 Drone/Image Capture → preprocessing → tiled detection → pathology classification → georeferenced report → maintenance workflow。核心 dataset / trained weights / proprietary detection algorithm 並非完整公開，因此只作 pipeline architecture reference。

## 負面軟體案例

### `almona02/almona-portfolio-forge` 的 ASTM E1300 compliance code

https://github.com/almona02/almona-portfolio-forge

曾查見名為 ASTM E1300 compliance 的程式含 placeholder / simplified logic、default PASS 類行為。保留此案例的目的不是推薦使用，而是提醒：

- class / function / UI 名稱寫著標準編號，不等於真正實作該標準；
- `compliant = true` 不是 engineering proof；
- hard-coded unknown number / placeholder / default PASS 應視為 invalid / incomplete。

**不得以此 implementation 作玻璃工程設計依據。**

## Research gaps

仍值得找但目前缺少成熟公開 implementation：

- full-scale façade performance-test DAQ；
- pressure / flow / displacement / event synchronization；
- sensor-calibrated curtain-wall SHM；
- defect detection → verified engineering condition rating；
- fabrication / installation survey automation。

> Inspection AI 與 monitoring tool 應輸出 observation / evidence，不應越權直接產生未經工程驗證的 capacity 或 safety conclusion。