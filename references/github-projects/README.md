# 帷幕牆／建築外殼相關 GitHub 專案參考清單

查證日期：2026-09-02

本頁整理 GitHub 上與帷幕牆、結構玻璃、門窗熱工、建築外殼性能、結構分析、BIM／IFC 與工程自動化相關的公開 repository，供後續研究、架構借鏡、程式實作與交叉驗證時使用。

## 使用定位

這些 GitHub repository 一律屬於**非規範性參考（NON-NORMATIVE REFERENCE）**。

不得因專案：

- 名稱看起來與帷幕牆直接相關；
- 程式可成功執行；
- README 宣稱支援某 ASTM / ISO / AAMA / code；
- 有測試、CI、star、paper 或學術引用；

就把其中的公式、係數、allowable、材料性質、standard table、load combination 或 PASS / FAIL 判定直接升格成正式工程依據。

工程使用仍應回到：

1. 台灣現行法規／主管機關要求；
2. current CNS / ASTM / AAMA-FGIA / ISO 等正式標準；
3. project specification / approved design basis；
4. manufacturer / material certificate；
5. 經驗證的 project-specific engineering model。

GitHub 專案最適合拿來參考：

- software architecture；
- data model；
- API / workflow；
- solver integration；
- testing strategy；
- engineering traceability；
- CAD / BIM / MTO / reporting automation；
- 可再由正式來源獨立驗證的數值方法。

## 分級

- **A — 直接相關**：repository 的主要目的直接涉及 curtain wall / façade / structural glass。
- **B — 建築外殼性能**：與 glazing、window、energy、daylight、HAM 等外殼性能直接相關。
- **C — 支援工具**：不是帷幕專用，但對截面、FEA、BIM／IFC 等工作有高度參考價值。
- **D — 觀察／教育用途**：概念值得看，但目前成熟度、工程適用性或 provenance 不足，不宜當 production reference。

---

# A — 直接帷幕牆／結構玻璃專案

## `AlumeshetMaxim/curtain-wall-ai-automation-toolkit-0`

Repository：https://github.com/AlumeshetMaxim/curtain-wall-ai-automation-toolkit-0

**定位：直接相關／工程自動化。**

README 明確定位為 CAD、BIM、façade engineering 與 curtain wall workflow 的 open-source automation toolkit，涵蓋：

- CAD drawing processing；
- glass / profile naming；
- MTO / BOM；
- revision comparison；
- PDF publishing；
- DWG data extraction；
- Excel schedule checks；
- STEP validation；
- Rhino Make2D；
- fabrication package checking；
- AI-assisted development。

### 值得借鏡

- 帷幕工程 automation module 的拆分方式；
- MTO / BOM 與 revision comparison workflow；
- CAD / Excel / PDF / STEP 串接；
- public sample data 與 privacy / sanitization 的做法；
- 如何把實務工作拆成可由 AI 協助開發的小工具。

### 限制

README 自述仍在 early stage。適合參考 workflow / architecture，不應把 sample rule 或輸出當工程設計值。

---

## `normanrichardson/structuralglass`

Repository：https://github.com/normanrichardson/structuralglass

**定位：直接相關／結構玻璃 Python package。**

README 將使用者明確定義為 façade / enclosure designers and engineers，功能包含：

- glass layers；
- interlayers；
- annealed / heat-strengthened / fully tempered glass types；
- equivalent-thickness models；
- laminated-glass shear-transfer treatment；
- four-side-supported face loading；
- ASTM E1300 / NCSEA-related design utilities。

### 值得借鏡

- structural-glass domain object 如何拆分；
- ply / interlayer / glass-type 資料模型；
- effective-thickness strategy pattern；
- engineering package 對 assumptions 與 disclaimer 的處理。

### 重要防呆

本 KB 不繼承此 repo 的預設材料值、interlayer properties、glass strength 或 E1300 implementation。任何數值都必須重新對 current governing source 驗證。

---

## `Mahdi-Soheyli/ML-Facade-Project`

Repository：https://github.com/Mahdi-Soheyli/ML-Facade-Project

**定位：直接相關／E1300 教學 API + façade ML 架構。**

README 顯示其架構組合：

- wind-derived design pressure；
- ASTM E1300-24 style load-resistance oracle；
- KNN ML layer；
- FastAPI；
- browser dashboard；
- dataset generation；
- tests；
- Grasshopper HTTP client examples。

### 值得借鏡

- `engineering oracle → synthetic/research dataset → ML` 的隔離方式；
- API / dashboard / Grasshopper 的整合；
- deterministic calculation 與 ML prediction 分層；
- tests / dataset documentation / deployment architecture。

### 重要防呆

該 repo 自己也明示為 education / engineering exploration。不得把其 E1300 table data、oracle 或 wind logic 視為本 KB 的 authoritative implementation；正式工程仍須回到 ASTM 正式標準與 applicable building code。

---

## `1006867586/curtainwall-tool`

Repository：https://github.com/1006867586/curtainwall-tool

**定位：直接相關／帷幕提料與材料管理工具。**

目前 repository root 可見：

- `cutting.html`：線材套裁；
- `steel.html`：鋼材快查；
- `hardware.html`：五金提料；
- CSV / Excel-oriented take-off workflow。

首頁文字說明其用途包含原材套裁、材料利用率、型鋼重量與截面參數、五金清單與採購／計價資料輸出。

### 值得借鏡

- 幕牆工程師日常小工具 UI；
- cutting optimisation / take-off workflow；
- hardware catalog + quantity aggregation；
- lightweight browser-only engineering utility 的產品形式。

### 重要防呆

目前缺少完整 README / engineering provenance。其型鋼資料、重量、規格與任何計算結果只適合當 UX / workflow 參考；若要採用數據或公式必須另行驗證。

---

## `CurtainWallMonitoringPlatform/CurtainWallWeb-Backend`

Repository：https://github.com/CurtainWallMonitoringPlatform/CurtainWallWeb-Backend

**定位：直接相關／玻璃帷幕監測。**

README 標示為「玻璃幕牆振動資料可視化監管平台後端」，技術架構使用 Python / Django，並包含 device / monitor / setting 等模組。

### 值得借鏡

- curtain-wall condition monitoring / vibration data 的 web-backend 架構；
- device → monitor → visualization API 的資料流；
- 未來若研究 façade sensor / SHM / digital twin，可作概念入口。

### 限制

目前 README 主要是環境與目錄說明，工程感測方法、sensor accuracy、damage criterion 與 validation evidence 尚不足，因此列為 architecture reference，不作監測判定依據。

---

# B — 門窗／玻璃／建築外殼性能

## `LBNL-ETA/pyWinCalc`

Repository：https://github.com/LBNL-ETA/pyWinCalc

**定位：高價值 supporting reference／glazing thermal + optical calculation。**

由 Lawrence Berkeley National Laboratory 相關組織維護。README 說明其用途為計算 glazing systems 的 thermal / optical properties，內容包括：

- glazing system solid layers / gaps；
- gases / gas mixtures；
- optical calculations；
- ISO 15099 thermal calculations；
- SHGC-related calculations；
- BSDF shades；
- IGSDB data；
- CMA calculations including frames。

### 值得借鏡

- IGU / glazing thermal-optical data model；
- layer / gap / gas object design；
- standard method 與 calculation engine 分層；
- SI unit discipline；
- examples / validation-oriented API design。

### 限制

它不是帷幕結構設計工具，也不能取代 project-specific thermal bridge / condensation model。使用時仍需確認實際 method、standard、boundary conditions 與適用範圍。

---

## `LBNL-ETA/Windows-CalcEngine`

Repository：https://github.com/LBNL-ETA/Windows-CalcEngine

**定位：高價值 supporting reference／window + shading calculation engine。**

README 將其描述為：

> Thermal and optical routines for modeling properties of window and shading systems.

### 值得借鏡

- pyWinCalc 背後較底層的 thermal / optical routines；
- calculator engine 與 Python wrapper 分離的架構；
- reproducible build / dependency management；
- 若未來本 KB 延伸成 building-envelope calculation engine，可參考 library layering。

### 限制

這是 window / shading performance calculation engine，不是 curtain-wall structural solver。

---

## `ladybug-tools/honeybee-energy`

Repository：https://github.com/ladybug-tools/honeybee-energy

**定位：建築能源／外殼性能模型。**

README 說明 Honeybee Energy 是 energy simulation extension，可表示跨 simulation engine 的 energy properties，並直接整合 EnergyPlus，亦可透過 OpenStudio translation workflow 使用。

### 值得借鏡

- building envelope → energy-model abstraction；
- construction set / material / aperture 等建築性能資料模型；
- façade option study / WWR / glazing performance 的自動化分析；
- EnergyPlus / OpenStudio integration architecture。

### 限制

適合 energy / environmental performance，不是 façade component structural verification。

---

## `ladybug-tools/honeybee-radiance`

Repository：https://github.com/ladybug-tools/honeybee-radiance

**定位：日照／採光／輻射 supporting reference。**

README 說明它把 Radiance daylight / radiation simulation 加入 Honeybee。

### 值得借鏡

- glazing / shading / façade geometry 與 daylight / solar radiation workflow；
- façade design option comparison；
- 與 parametric / environmental analysis pipeline 串接。

### 限制

不提供帷幕結構承載能力或玻璃 strength verification。

---

## `srouchier/hamopy`

Repository：https://github.com/srouchier/hamopy

**定位：建築外殼濕熱（HAM）分析 supporting reference。**

README 說明它是用 finite element 解一維 Heat / Air / Moisture transfer 的 Python package，原始應用即為 building materials 的 hygrothermal modelling，可處理：

- porous material；
- liquid / vapor storage and flow；
- time-dependent boundary conditions；
- coupled hygrothermal transfer；
- sensitivity analysis automation。

### 值得借鏡

- condensation / moisture-risk 研究方法；
- transient boundary-condition data model；
- sensitivity study architecture。

### 限制

主要是 1D HAM；對帷幕多維熱橋、金屬框複雜幾何與 cavity airflow 的適用性必須另行判斷。

---

# C — 結構分析／截面／BIM 支援工具

## `robbievanleeuwen/section-properties`

Repository：https://github.com/robbievanleeuwen/section-properties

**定位：高度相關 supporting reference／任意截面性質。**

README 說明此 Python package 以 finite element method 分析 arbitrary cross-sections，可取得：

- area；
- centroidal inertia；
- `Ixx / Iyy / Ixy`；
- composite section properties；
- warping analysis；
- stress from applied forces / moments。

### 為什麼對帷幕很重要

帷幕鋁擠型通常不是標準簡單截面。這個專案很適合研究：

- DXF / polygon → section-property pipeline；
- unsymmetrical section；
- principal axes；
- multi-material / composite section；
- warping / stress post-processing。

### 限制

截面性質計算正確不代表 member / local extrusion / connection capacity 自動成立；仍須按本 KB 的 structural load path 與 failure-mode framework 分開檢核。

---

## `JWock82/Pynite`

Repository：https://github.com/JWock82/Pynite

**定位：supporting reference／Python structural FEA。**

README 說明其能力包括：

- elastic 3D static analysis；
- frame members；
- point / distributed / nodal loads；
- load cases / combinations；
- reactions；
- shear / moment / deflection；
- springs / releases；
- quadrilateral / rectangular plate elements；
- model rendering / reports。

### 值得借鏡

- continuous mullion / transom solver architecture；
- support release / spring modeling；
- load-case objects；
- reaction extraction；
- plate model prototype；
- automated textbook-regression testing。

### 限制

這是 general-purpose structural library，不包含帷幕專屬 allowable、AAMA / ASTM acceptance、aluminum local limit states、glass design 或 connection design rules。

---

## `IfcOpenShell/IfcOpenShell`

Repository：https://github.com/IfcOpenShell/IfcOpenShell

**定位：supporting reference／BIM + IFC data extraction / validation。**

README 說明其為 open-source IFC library，提供 C++ / Python API，並包含：

- IFC parsing / geometry；
- IfcConvert；
- IFC model query / manipulation；
- `ifccsv`；
- `ifcdiff`；
- clash detection；
- IDS model auditing；
- BIM authoring ecosystem。

### 值得借鏡

若未來要把帷幕資料從 BIM 送入 KB / calculator / QA workflow，可研究：

- `IfcCurtainWall` / element extraction；
- property set / quantity extraction；
- model-diff；
- model audit；
- IFC → CSV / JSON engineering pipeline。

### 限制

IFC geometry / property 存在不代表其值已通過工程驗證；BIM data ingestion 必須保留 source / revision / units / model assumptions。

---

## `drcassar/glasspy`

Repository：https://github.com/drcassar/glasspy

**定位：adjacent supporting reference／玻璃材料科學與 ML。**

README 將 GlassPy 定位為 glass materials 科學研究工具，包含 SciGlass data 與 GlassNet / VITRIFY / ViscNet 等 property-prediction model。

### 值得借鏡

- glass material dataset / ML pipeline；
- property prediction 與 uncertainty-aware research architecture；
- 若未來研究特殊玻璃組成／材料性質，可作材料科學入口。

### 限制

它不是 architectural structural-glass code checker；predictive material property 不可直接替代 ASTM / EN / project-certified architectural glass design properties。

---

# D — 觀察／教育用途

## `CurtainWallMonitoringPlatform/CurtainWallWeb-Frontend`

Repository：https://github.com/CurtainWallMonitoringPlatform/CurtainWallWeb-Frontend

目前 README 仍主要是 Nuxt 3 starter 說明；可與 Backend 一起觀察完整 monitoring UI，但現階段單獨的 engineering reference value 低於 backend。

---

## `almona02/almona-portfolio-forge` 的 ASTM E1300 compliance code

Repository：https://github.com/almona02/almona-portfolio-forge

GitHub code search 可找到 `src/compliance/ASTME1300.ts`，但目前實作包含明顯 placeholder / simplified logic，例如：

- 固定 base resistance；
- 厚度條件倍率；
- 某些 requirement default `passed: true`；
- 以整體 score 判 `compliant`；
- 自動產生看似 certification 的輸出。

### 為什麼仍值得記錄

它是一個很好的**負面工程軟體案例**：

> UI / class 名稱寫著 ASTM E1300，不代表它真的實作 ASTM E1300。

非常適合用來提醒未來 AI / calculator review：

- function / class 名稱不是 evidence；
- `compliant = true` 不是 engineering proof；
- placeholder number 若沒有 governing source，必須視為 invalid / incomplete。

**不得拿此 implementation 作玻璃工程計算依據。**

---

# 後續搜尋方向

值得持續搜尋但本輪尚未建立穩定 shortlist 的主題：

- AAMA / ASTM façade performance-test data acquisition；
- curtain-wall air / water chamber test automation；
- structural silicone joint calculator；
- façade anchor / fastener-group analysis；
- aluminum extrusion local failure；
- façade-specific wind-pressure tools；
- glass-fin / point-supported glass FEA；
- curtain-wall shop-drawing QA；
- Revit / Dynamo / Rhino / Grasshopper façade fabrication automation；
- façade defect / image inspection / computer vision；
- sensor-based curtain-wall SHM / digital twin。

# 維護規則

新增 GitHub 專案到本清單前，至少確認：

1. repository 可公開存取；
2. README / source code 能支持我們對用途的描述；
3. 沒有只因 repository 名稱相似就收錄；
4. 明確區分工程 authority 與 software reference value；
5. 若要複製／衍生 code，另查 license；
6. 若 repo 宣稱實作標準，必須另回 current official standard 驗證；
7. 若發現 hard-coded unknown factor / placeholder / default PASS，降低分級並記錄風險；
8. 不把第三方 repo 的 copyrighted tables / standard text 複製進本 KB。

> 本頁是公開 GitHub 專案的研究索引，不是 approved software list，也不是工程責任移轉清單。