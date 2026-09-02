# 帷幕牆／建築外殼 GitHub 專案參考索引

查證日期：2026-09-02

本目錄整理與 curtain wall / façade / structural glass / building performance / BIM / FEA / inspection 相關的公開 GitHub repository。

所有 repository 一律屬 **NON-NORMATIVE REFERENCE**：可用來研究 software architecture、data model、solver integration、testing、automation、traceability 或公開實作狀態，但**不得因程式可執行、README 宣稱符合某標準、有 CI / star / paper，就把其中公式、係數、材料值或 PASS 判定升格成正式工程依據。**

正式工程仍應回到 governing law / code / current standard / project design basis / manufacturer evidence / validated engineering model。

## 分類索引

- [`facade-automation-and-bim.md`](facade-automation-and-bim.md) — curtain-wall automation、Grasshopper façade panelization、Rhino/Revit、Dynamo、pyRevit、IFC、Speckle、DXF。
- [`building-performance.md`](building-performance.md) — glazing thermal/optical、EnergyPlus workflow、daylight、HAM、CFD、glass material research。
- [`structural-analysis-and-calculation.md`](structural-analysis-and-calculation.md) — section mechanics、frame / FEA、structural glass、bolt group、traceable calculation rendering。
- [`structural-connections-and-glass.md`](structural-connections-and-glass.md) — connections / aluminum local mechanics / structural glass 專題，以及 anchor、screw pull-out、structural silicone、point-supported glass 等 research gaps。
- [`inspection-and-monitoring.md`](inspection-and-monitoring.md) — façade computer vision、defect benchmark、condition monitoring / SHM 與負面軟體案例。

## 使用分級

在各專題頁可依需要用下列概念評估：

- **A — 直接相關**：主要目的直接涉及 curtain wall / façade / structural glass。
- **B — 建築外殼性能**：glazing / window / energy / daylight / HAM / CFD。
- **C — 支援工具**：section / FEA / BIM / CAD / reporting / interoperability 等 general-purpose tools。
- **D — 觀察／教育用途**：architecture 有參考價值，但工程成熟度、provenance 或 validation 不足。

分級不是 approved-software list。

## 收錄規則

新增 GitHub repository 前至少確認：

1. repository 可公開存取；
2. README / source code 足以支持對用途的描述；
3. 不因名稱相似就收錄；
4. 明確區分 engineering authority 與 software reference value；
5. 若要複製／衍生 code，另查 license；
6. repo 宣稱實作 standard / code 時，必須回 current primary source 獨立驗證；
7. hard-coded unknown factor、placeholder、default PASS 應記錄為風險並降低可信度；
8. 不把第三方 copyrighted standard table / text 搬入本 KB；
9. archived / early-stage repo 可以保留 architecture value，但要明示限制；
10. 若要依賴 output，需重新確認 repository version、assumptions 與 validation status。

## 目前共通研究缺口（Research gaps）

高價值但仍缺乏成熟公開 implementation 的領域包括：

- curtain-wall performance-test DAQ / automation；
- structural silicone engineering calculator；
- façade-specific concrete anchor / thin-aluminum screw pull-out solver；
- aluminum extrusion local-failure solver；
- point-supported / drilled glass validated FEA workflow；
- structural-glass post-breakage / redundancy implementation；
- shop-drawing semantic QA；
- stack-joint / fabrication tolerance / installation survey automation；
- sensor-calibrated curtain-wall SHM。

> 找不到可靠 open-source implementation 時，保留 research gap 比硬收低品質 calculator 更有價值。