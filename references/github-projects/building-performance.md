# 建築外殼性能 GitHub 專案參考

查證日期：2026-09-02

本頁聚焦 glazing thermal / optical、energy、daylight、HAM、CFD 等建築外殼性能工具。全部屬 **NON-NORMATIVE REFERENCE**。

## 玻璃熱工／光學（Glazing thermal／optical）

### `LBNL-ETA/pyWinCalc`

https://github.com/LBNL-ETA/pyWinCalc

可研究 glazing layers / gaps / gases / optical data、ISO 15099 thermal calculation、SHGC、BSDF、IGSDB 與 frame-related data model。適合借鏡 calculation engine API 與 unit discipline，不取代 project-specific thermal bridge / condensation model。

### `LBNL-ETA/Windows-CalcEngine`

https://github.com/LBNL-ETA/Windows-CalcEngine

較底層的 window / shading thermal-optical routines。可研究 core engine 與 language wrapper 分層、build/dependency discipline。

## 能源／日照（Energy／daylight）

### `ladybug-tools/honeybee-energy`

https://github.com/ladybug-tools/honeybee-energy

研究 envelope / aperture / construction set 與 EnergyPlus / OpenStudio integration，適合 façade option study、WWR、glazing performance workflow。不是 façade component structural checker。

### `ladybug-tools/honeybee-radiance`

https://github.com/ladybug-tools/honeybee-radiance

Radiance daylight / radiation integration。適合 glazing / shading / façade geometry 的 daylight / solar analysis pipeline；不提供 structural capacity。

## 熱濕耦合／計算流體力學（Hygrothermal／CFD）

### `srouchier/hamopy`

https://github.com/srouchier/hamopy

1D Heat / Air / Moisture finite-element package。適合研究 transient boundary condition、porous material、moisture storage / flow 與 sensitivity study。對金屬帷幕多維熱橋與 cavity airflow 的適用性需另判斷。

### `ladybug-tools/butterfly`

https://github.com/ladybug-tools/butterfly

OpenFOAM CFD workflow API，可從 parametric environment 建立 CFD case。可研究 façade-local wind / external flow / cavity-flow solver adapter，但 **CFD pressure ≠ code-prescribed façade design pressure**；正式使用需另外建立 domain、mesh、turbulence model、BC 與 validation evidence。

## 玻璃材料研究

### `drcassar/glasspy`

https://github.com/drcassar/glasspy

玻璃材料科學 dataset / ML toolkit。適合研究 material-property dataset、prediction pipeline 與 uncertainty-aware research；不是 architectural structural-glass code checker。

> Performance simulation output 必須連回實際 boundary condition、material data、standard method 與 project design basis；軟體可執行不等於工程假設正確。