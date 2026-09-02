# Façade Automation／BIM GitHub 專案參考

查證日期：2026-09-02

本頁收錄與帷幕牆幾何、panelization、CAD/BIM、自動提料、跨軟體資料交換直接相關的公開 GitHub repository。全部屬 **NON-NORMATIVE REFERENCE**。

## 直接帷幕工程／幾何

### `AlumeshetMaxim/curtain-wall-ai-automation-toolkit-0`

https://github.com/AlumeshetMaxim/curtain-wall-ai-automation-toolkit-0

可研究 CAD drawing processing、glass/profile naming、MTO/BOM、revision comparison、PDF publishing、STEP validation、fabrication-package checking 與 AI-assisted development。適合借鏡 workflow / module decomposition，不應把 sample rule 當工程 design authority。

### `Payette/SkinDesigner`

https://github.com/Payette/SkinDesigner

Grasshopper façade panelization tool。適合研究 façade surface → panel family / repeated geometry / panel layout；不代表 structural、tolerance、fabrication 或 connection validation 已完成。

### `ilyasab3/FacadeFE`

https://github.com/ilyasab3/FacadeFE

Grasshopper façade FE model preparation。可研究 panel geometry / profile properties / boundary conditions / loads → FE nodes/elements → external solver input，尤其是 panel wind-load mapping。公開版本為 early implementation，不作 solver validation evidence。

### `1006867586/curtainwall-tool`

https://github.com/1006867586/curtainwall-tool

套裁、鋼材快查、五金提料等 browser utility。適合參考 façade engineer 日常 UX、cutting optimisation、hardware quantity aggregation；數據與公式需另行驗證。

## Revit／Rhino／AEC integration

### `mcneel/rhino.inside-revit`

https://github.com/mcneel/rhino.inside-revit

研究 Rhino / Grasshopper geometry 與 Revit integration、parametric façade → BIM object adapter。幾何成功傳遞不代表 fabrication tolerance、analysis axis 或 connection intent 已驗證。

### `DynamoDS/DynamoRevit`

https://github.com/DynamoDS/DynamoRevit

Revit visual-programming integration。適合 batch parameter extraction / modification、model QA 與 repetitive BIM operation 架構。

### `pyrevitlabs/pyRevit`

https://github.com/pyrevitlabs/pyRevit

Revit RAD environment。可參考公司內部 façade BIM 工具列、batch QA、drawing automation；不應把工程 criterion 寫成無 provenance 的 magic constants。

### `IfcOpenShell/IfcOpenShell`

https://github.com/IfcOpenShell/IfcOpenShell

IFC parsing / geometry / query / manipulation / `ifccsv` / `ifcdiff` / IDS audit。可研究 `IfcCurtainWall` / quantity / property extraction 與 BIM → engineering pipeline。IFC property 存在不等於工程值已驗證。

### `specklesystems/speckle-sharp-connectors`

https://github.com/specklesystems/speckle-sharp-connectors

AEC data interoperability。可研究 AutoCAD / Rhino / Revit / CSi / Tekla 等 host-object adapter、converter、object identity 與 metadata transfer。資料交換成功不代表 semantic equivalence。

### `mozman/ezdxf`

https://github.com/mozman/ezdxf

DXF read / modify / write 與 entity inspection。對未來 `aluminum extrusion DXF → geometry cleanup → section properties` 很有價值；輸入輪廓仍需驗證 closed / non-overlap / actual fabrication geometry。

## 建議研究鏈

`Rhino / Grasshopper / Revit / DXF`
→ geometry + metadata
→ normalized façade object
→ section / structural model
→ calculation / QA
→ controlled BIM / drawing output

> CAD/BIM automation 是資料與流程層，不自行建立 engineering authority。