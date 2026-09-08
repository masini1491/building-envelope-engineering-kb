# 帷幕牆／建築外殼 GitHub 專案參考索引

查證日期：2026-09-09

本目錄整理與 curtain wall / façade / structural glass / building performance / BIM / FEA / inspection 相關的公開 GitHub repository，以及對本知識庫的 AI retrieval／knowledge-management architecture 具有直接參考價值的跨領域支援工具。

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
- **C — 支援工具**：section / FEA / BIM / CAD / reporting / interoperability，以及對 retrieval／knowledge-management architecture 有參考價值的 general-purpose AI tooling。
- **D — 觀察／教育用途**：architecture 有參考價值，但工程成熟度、provenance 或 validation 不足。

分級不是 approved-software list。

## 跨領域人工智慧／知識基礎設施參考

### 騰訊 WeKnora 知識平台

- **分級**：C — 支援工具。
- **查證版本**：`Tencent/WeKnora@3e6010e7cd3937f289cc1dbadc829e71eb1163f4`（2026-09-09）。
- **用途定位**：open-source LLM knowledge platform；可作 RAG、document ingestion、agent、wiki、retrieval traceability 與 knowledge-management infrastructure 的 architecture reference。
- **值得參考的實作概念**：
  - heading-aware chunking 依 Markdown heading 切分，並把 section breadcrumb 帶入 retrieval context；
  - parent-child retrieval 以較小 child chunk 做精準 matching，再把較大的 parent context 交給 LLM；
  - chunk / wiki revision history、diff、rollback 與 reindex，使 source revision 與 retrieval state 可被追溯；
  - document parsing／ingestion trace、runtime task visibility 與 observability，可用來辨識 pipeline failure 發生在哪一層。
- **對本 KB 的架構啟發**：physical document structure、retrieval granularity 與 LLM answer-context granularity 不必綁成同一層；未來若導入 vector index／RAG，應讓 retrieval artifact 能追溯到生成它的 canonical source revision，而不是把 embedding/index 本身當新 authority。
- **不可推論**：WeKnora 不提供 curtain-wall／building-envelope engineering authority；其 chunk size、overlap、模型設定或產品預設不得直接升格成本 KB 的 universal retrieval rule，更不得作工程 acceptance evidence。
- **授權注意**：project 主體以 MIT License 發布，但若未來複製／衍生 code 或 component，仍需依 repository 的 third-party notices／component licenses 逐項確認；目前本 KB 只引用 architecture concept 與 public repository provenance，不搬入其 code。

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