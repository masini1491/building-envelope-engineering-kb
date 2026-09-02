# 結構連接／鋁擠型／結構玻璃 GitHub 專題參考

查證日期：2026-09-02

本頁是 [`README.md`](README.md) 的專題延伸，聚焦目前帷幕結構審查最需要的四類公開實作：

- bolt / fastener group mechanics；
- anchor / connected-material failure；
- aluminum extrusion / section mechanics；
- structural glass / point-supported glass。

所有 repository 仍屬 **NON-NORMATIVE REFERENCE**。本頁的「值得借鏡」只代表 software / mechanics / architecture 有研究價值，不代表其 code implementation 已成為本 KB 的 governing design method。

---

# 1. 螺栓／扣件群組（Bolt／Fastener Group）

## `wcfrobert/ezbolt`

Repository：https://github.com/wcfrobert/ezbolt

**分級：C — 高價值 supporting reference。**

README 將 EZbolt 定位為 Python bolt-force calculator，可對 bolt group 在 in-plane shear + torsion 下使用：

- Elastic Method；
- Elastic Center of Rotation；
- Instant Center of Rotation（ICR）；
- arbitrary bolt arrangement；
- arbitrary load orientation / eccentricity；
- individual bolt-force table；
- connection DCR / visualization。

其 Elastic Method 明確建立：

- bolt-group centroid；
- `Ix / Iy / J` 類幾何量；
- direct shear；
- torsional shear；
- vector superposition；
- resultant bolt force。

### 對本 KB 的直接價值

這與 [`../../knowledge/structural-design/connections/fastener-group-analysis.md`](../../knowledge/structural-design/connections/fastener-group-analysis.md) 的核心幾何 mechanics 高度相關，可研究：

`bolt coordinates`
→ `group centroid`
→ `direct load`
→ `eccentric moment / torsion`
→ `per-fastener vector demand`
→ `governing fastener`

特別適合作為未來 fastener-group solver 的**獨立 regression / architecture reference**。

### 不可直接沿用的部分

EZbolt 的 ICR routing 來自 AISC steel-connection context，並包含 AISC-specific force-deformation / coefficient logic。

帷幕工程不得因此直接把：

- ICR coefficient；
- bolt capacity；
- AISC table logic；
- connection DCR；

套到鋁擠型、螺絲、薄壁 screw chase、anchor bracket 或 stainless fastener connection。

對 façade connection，本 KB 優先借鏡的是**座標群組、力矩分配、結果資料結構與驗證案例**，而不是 steel-bolt capacity rule。

---

## `EdwardAstill/connecty`

Repository：https://github.com/EdwardAstill/connecty

**分級：D — experimental / architecture reference。**

README 將 Connecty 定位為 structural engineering 的 weld / bolt connection analysis，可處理：

- direct / torsional / bending stress；
- weld geometry；
- 3D load components；
- DXF geometry；
- elastic / ICR-style analysis；
- AISC-style checks；
- stress visualization。

其 bolt theory 文件還討論：

- load transfer to bolt-group centroid；
- in-plane shear；
- ICR；
- out-of-plane bolt tension；
- neutral-axis approach；
- prying action。

### 值得借鏡

對帷幕 bracket / fastener-group 工具，可研究：

- 6-component load object：`Fx/Fy/Fz/Mx/My/Mz`；
- load point / eccentricity transfer；
- shear solver 與 tension solver 分開；
- prying 作為額外 demand，而非默默混入 bolt force；
- DXF geometry → connection model；
- demand calculation 與 code capacity check 分層。

### 為何只列 D

目前 theory 文件可見仍有明顯開發中的草稿文字與簡化假設；例如 coordinate-system 註記尚未完全整理，prying implementation 也有自行簡化的 effective-width assumption。

因此它很適合研究**software decomposition**，但目前不適合作任何 façade design value 或正式 connection verification 的 secondary authority。

---

# 2. 鋁截面／局部力學（Aluminum Section／Local Mechanics）

## `EdwardAstill/sectiony`

Repository：https://github.com/EdwardAstill/sectiony

**分級：C — supporting reference。**

README 將 Sectiony 定位為 structural cross-section properties / stress analysis Python library，並提供：

- `A`；
- centroid；
- `Ix / Iy / Ixy`；
- `J`；
- `Sx / Sy`；
- principal second moments / principal angle；
- shear center；
- warping constant `Cw`；
- stress distribution；
- JSON serialization；
- open line-group mechanics。

### 對帷幕鋁擠型的價值

與既有 `section-properties` 專案相比，可再提供另一個獨立實作思路，尤其值得比較：

- unsymmetrical section；
- `Ixy`；
- principal axes；
- shear center；
- torsion / warping metadata；
- geometry serialization；
- line group 用於 weld / connection path 的抽象。

### 重要限制

**Section properties ≠ aluminum member capacity ≠ local extrusion capacity。**

即使 `A / I / S / J / Cw` 計算正確，仍不能自動回答：

- local flange / web bending；
- screw-chase pull-out；
- thread stripping；
- hook / lip failure；
- local crippling；
- bearing / tear-out；
- welded heat-affected strength；
- code-specific slender-element limit。

截至本輪搜尋，尚未找到一個具有足夠公開 provenance、可列為高品質 reference 的 **façade aluminum extrusion local-failure solver**。

這個缺口應保持為 research gap，而不是以 generic section solver 取代。

---

# 3. 結構玻璃（Structural Glass）

## `FethersGlazingSystems/finestra`

Repository：https://github.com/FethersGlazingSystems/finestra

**分級：A/C — 直接玻璃結構分析 reference，但 scope 有限。**

README 將專案定位為「Structural analysis for glass in buildings」，目前公開內容主要針對 rectangular glass panel：

- uniform load；
- concentrated load；
- four-edge simply-supported flat plate；
- Navier solution；
- stress / deflection prediction；
- Jupyter / Panel web UI；
- AS 1288-2021-based permissible design limits。

### 值得借鏡

- plate-theory calculation core 與 web UI 分離；
- ULS / SLS result separation；
- stress ratio / deflection ratio output；
- concentrated-load function 作為 walkable / local-load research入口；
- engineering notebook → browser calculator workflow。

### 重要防呆

本 KB 不採用其 AS 1288 criteria 作台灣 project default，也不因此視為 ASTM E1300 implementation。

更重要的是：其 README 所描述的核心模型是**四邊簡支矩形平板**，因此不能拿來代表：

- point-supported glass；
- drilled glass；
- bolted glass；
- glass fin；
- notch / hole stress concentration；
- local bearing around fittings；
- laminated-glass nonlinear/post-breakage behaviour。

因此它補的是「可追溯 plate-analysis implementation」參考，沒有填掉 point-supported glass 的 research gap。

---

# 4. 本輪明確確認仍存在的研究缺口（Research Gaps）

## 混凝土／後置式錨栓（Concrete／Post-installed Anchor）

本輪以 repository name / code search 搜尋：

- anchor design；
- anchor bolt；
- concrete breakout；
- ACI 318 anchor；
- façade anchor；

沒有找到一個同時具備以下條件的公開 repository：

1. scope 清楚；
2. current code edition provenance 清楚；
3. concrete breakout / pullout / pryout / edge / spacing / group effect 等 failure modes 有完整 routing；
4. 有 validation tests；
5. 不以 hard-coded unknown factor 或 spreadsheet-like black box 為核心。

因此目前**不建立 façade anchor calculator 推薦項目**。

實際 anchor review 仍應回到本 KB canonical connection / anchor method + governing code / approval / manufacturer evidence。

---

## 薄鋁板螺絲拔出／牙紋剝離（Screw Pull-out／Thread Stripping in Thin Aluminum）

本輪搜尋 screw pullout、thread stripping、aluminum extrusion 等關鍵字，沒有找到足夠可靠且直接針對 façade thin-wall aluminum screw connection 的公開 implementation。

因此不得拿：

- generic machine-design thread formula；
- steel bolt calculator；
- arbitrary internet pullout equation；

取代 AAMA TIR-A9 / Aluminum Design Manual / manufacturer data / project validation 所需的正式 routing。

這仍是本 KB 很值得自己建立**可追溯 calculator module**的領域。

---

## 結構矽利康（Structural Silicone）

本輪沒有找到足夠成熟的 open-source structural-sealant glazing calculator。

GitHub code search 可以找到引用 Dow manual / ASTM C24 family 的文章型 repository，但目前不足以列為 calculator / engineering implementation reference。

因此 structural silicone 仍維持：

`ASTM C1184 / C1401 / C1135`
+ manufacturer engineering review
+ project-specific joint geometry / adhesion / compatibility / movement validation

為主要 evidence path。

**不能為了有 GitHub implementation 而降低 evidence hierarchy。**

---

## 點支承／鑽孔玻璃／玻璃肋（Point-supported／Drilled Glass／Glass Fin）

本輪以 point-supported glass、spider glass、drilled glass、glass fin、finite element 等組合搜尋，未找到一個足以列為高品質 façade-specific implementation reference 的公開 repository。

這點本身很重要：

> generic shell / plate FEA package 能建立有孔板模型，不代表已建立 point-supported structural glass design method。

真正需要的至少還包括：

- glass material / flaw / strength basis；
- hole / edge geometry；
- fitting contact；
- washer / sleeve / polymer interface；
- local bearing；
- preload；
- friction / slip；
- nonlinear contact；
- mesh convergence at local stress concentration；
- laminated-glass interlayer model；
- support restraint；
- post-breakage state；
- applicable acceptance criteria。

因此目前仍以本 KB `knowledge/structural-glass/` methodology + validated general FEA backend 為正確 routing，而不是指定某個 GitHub point-supported-glass calculator。

---

# 5. 對未來自研 calculator 的建議

這次搜尋反而顯示一個很實用的方向：公開 GitHub 已有很多「局部能力很強」的 building blocks，但缺少 façade-specific evidence layer。

較合理的自研組合是：

`ezdxf / CAD / BIM`
→ connection / section geometry
→ `section-properties / sectiony`
→ section mechanics
→ 自研 façade fastener / local-extrusion rules
→ `ezbolt` 類 bolt-group mechanics 作交叉驗證
→ `PyNite / COMPAS FEA2` 類 solver backend
→ structural-glass validated model
→ `handcalcs` 類 traceable rendering
→ governing standard / project design basis reconciliation
→ `PASS / WARNING / FAIL / INCOMPLETE`

其中 façade-specific capacity rule、factor、allowable 與 acceptance criterion 必須由本 KB 自己維護 provenance，不能交給第三方 generic solver 默認。

> 「找不到可靠 open-source calculator」不是資料庫缺陷；在 high-stakes engineering domain，清楚標記 research gap 比收錄錯誤工具更有價值。