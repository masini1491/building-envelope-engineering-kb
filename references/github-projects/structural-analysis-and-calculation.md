# 結構分析／計算工具 GitHub 專案參考

查證日期：2026-09-02

本頁收錄對帷幕牆 section mechanics、frame / FEA、structural glass、traceable calculation presentation 有參考價值的公開 repository。全部屬 **NON-NORMATIVE REFERENCE**。

## 截面力學（Section mechanics）

### `robbievanleeuwen/section-properties`

https://github.com/robbievanleeuwen/section-properties

任意截面性質與 stress analysis。對鋁擠型 DXF/polygon → `A / centroid / Ixx / Iyy / Ixy / principal axes / warping` 很有參考價值。Section property 正確不代表 local extrusion / connection capacity 自動成立。

### `EdwardAstill/sectiony`

https://github.com/EdwardAstill/sectiony

另一套 cross-section mechanics reference，含 `Ixy`、principal axes、shear center、`J / Cw`、stress distribution 與 serialization。可作獨立 architecture / regression 參考。

## 桿件／有限元素分析（Frame／FEA）

### `JWock82/Pynite`

https://github.com/JWock82/Pynite

Python 3D structural FEA，含 members、loads、combinations、releases、springs、reactions、plates、reports。適合研究 continuous mullion / transom solver architecture；不包含 façade-specific aluminum / glass / connection code rules。

### `compas-dev/compas_fea2`

https://github.com/compas-dev/compas_fea2

Geometry-to-FEA framework，強調 frontend / backend adapter、node / element / section / material / problem / output abstraction。適合研究 solver-neutral façade analysis model；它不會替工程師決定正確 support model 或 failure modes。

## 結構玻璃

### `normanrichardson/structuralglass`

https://github.com/normanrichardson/structuralglass

結構玻璃 Python package，含 glass ply / interlayer / effective-thickness 等 domain object 與 E1300-related utility。值得借鏡 object model / strategy pattern；任何材料值、interlayer property 或 code implementation 仍需 current governing source 驗證。

### `FethersGlazingSystems/finestra`

https://github.com/FethersGlazingSystems/finestra

四邊簡支矩形玻璃 plate analysis、uniform / concentrated load、stress / deflection 與 web UI。適合研究 traceable plate-analysis implementation，但不代表 point-supported / drilled / glass-fin design method。

### `Mahdi-Soheyli/ML-Facade-Project`

https://github.com/Mahdi-Soheyli/ML-Facade-Project

E1300-style deterministic oracle + dataset / KNN ML + FastAPI + dashboard / Grasshopper integration。值得研究「engineering oracle 與 ML prediction 分離」；其 code/table 不作 authoritative E1300 implementation。

## 連接力學（Connection mechanics）

### `wcfrobert/ezbolt`

https://github.com/wcfrobert/ezbolt

Bolt-group centroid、direct shear、torsion、elastic / ICR mechanics。適合研究 group-coordinate solver 與 force-distribution regression；AISC-specific capacity / ICR logic不能直接套 façade screw / aluminum / anchor system。

### `EdwardAstill/connecty`

https://github.com/EdwardAstill/connecty

Experimental weld / bolt connection architecture，含 6-component loads、eccentricity、tension / shear solver、prying 等概念。適合 software decomposition，不作 façade design authority。

更深入的限制與 research gaps 見 [`structural-connections-and-glass.md`](structural-connections-and-glass.md)。

## 計算可追溯性／工程函式庫（Calculation traceability／engineering library）

### `connorferster/handcalcs`

https://github.com/connorferster/handcalcs

將 Python calculations 顯示為 symbolic formula → substitution → result，與本 KB 的 auditable calculation presentation 方向高度相容。它改善呈現，不會修正錯誤公式。

### `fib-international/structuralcodes`

https://github.com/fib-international/structuralcodes

可研究 structural-engineering package architecture、testing、documentation 與 versioning discipline。不能把其 output 自動視為台灣帷幕 governing requirement。

> General-purpose solver / library 提供 mechanics 或 software infrastructure；façade-specific design basis、capacity、factor、acceptance criterion 必須由本 KB 與 governing sources另行維護。