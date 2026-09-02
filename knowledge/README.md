# 技術知識（Knowledge）

本目錄保存已整理、可供工程師與 AI 直接使用的技術結論。人類可讀內容依 [`../LANGUAGE.md`](../LANGUAGE.md) 以繁體中文（台灣）為主；正式標準名稱、牌號與必要英文工程術語保留原文。

目前主題：

- `standards/`：規範的工程摘要與 cross-reference
- `materials/`：鋁、鋼、不鏽鋼等材料
- `glazing/`：建築玻璃產品與一般玻璃結構設計標準 routing
- `structural-glass/`：glass fin、laminated effective thickness、point-supported glass、glass-to-glass structural silicone、movement、FEA、walkable glass、post-breakage / redundancy
- `sealants/`：structural silicone、weatherseal 與接縫設計
- `gaskets/`：EPDM / dense / cellular / silicone gasket 等
- `fasteners/`：螺絲、螺栓、property class、設計與耐蝕
- `anchors/`：cast-in / post-installed anchor 與設計標準分流
- `finishes/`：烤漆、陽極處理等
- `corrosion-protection/`：熱浸鍍鋅與其他防蝕
- `structural-design/`：耐風、耐震、荷載生成、直料／橫料、多件擠型共同作用、continuous mullion / splice / sleeve、雙軸彎曲、glass-edge relative displacement、fastener group、screw pull-out / thread engagement、局部擠型、焊道群、anchor、structural review / failure-mode coverage，以及 `preliminary-sizing/` 前期 required section property / support / traceability 方法
- `operable-elements/`：活動窗／可開啟外牆構件的 sash/frame、hinge/lock/stay、五金緊件、局部擠型與 whole-product performance / life-cycle routing
- `engineering-notes/`：標準無法單獨回答的實務問題
- `stone/`：天然石材外牆與繫件系統
- `cladding/`：金屬複合板、蜂巢板及其他外牆面板系統；`structural-analysis/` 另整理 metal panel、stiffener、panel-to-stiffener connection 與 plate / shell FEA methodology
- `skylights/`：採光罩與斜面玻璃
- `building-physics/`：thermal、thermal bridge、condensation
- `fire/`：perimeter fire barrier、fire-resistive joint 與外牆防火 routing
- `case-knowledge/`：只用於公開來源可追溯案例，或完全去識別且無法反推出專案身分的通用 lesson pattern

## 結構計算路由

### 荷載生成（Load generation）

- `structural-design/load-generation/README.md`
- `structural-design/load-generation/facade-tributary-loads.md`
- `structural-design/load-generation/transom-wind-load-distribution.md`
- `structural-design/load-generation/glass-dead-load-and-setting-blocks.md`

### 框架／桿件（Framing）

- `structural-design/framing/mullion-transom-design-baseline.md`
- `structural-design/framing/continuous-mullion-analysis.md`
- `structural-design/framing/splice-and-sleeve-modeling.md`
- `structural-design/framing/multi-part-extrusion-load-sharing.md`
- `structural-design/framing/biaxial-bending-and-resultant-deflection.md`
- `structural-design/framing/glass-edge-relative-deflection.md`

### 連接（Connections）

- `structural-design/connections/load-path-and-anchor-reactions.md`
- `structural-design/connections/fastener-group-analysis.md`
- `structural-design/connections/screw-pullout-and-thread-engagement.md`
- `structural-design/connections/local-extrusion-failure.md`
- `structural-design/connections/weld-group-analysis.md`

### 外牆耐震構件／連接／位移

- `structural-design/seismic/README.md`
- `structural-design/seismic/taiwan-facade-component-seismic-force.md`
- `structural-design/seismic/seismic-connection-load-path.md`
- `structural-design/seismic/seismic-movement-compatibility.md`

### 結構審查／failure-mode coverage

- `structural-design/review/README.md`
- `structural-design/review/project-specification-extraction.md`
- `structural-design/review/structural-calculation-review-checklist.md`
- `structural-design/review/failure-mode-map.md`
- `structural-design/review/coverage-and-completeness.md`

### 前期尺寸需求（Preliminary sizing）

- `structural-design/preliminary-sizing/README.md`
- `structural-design/preliminary-sizing/design-vs-test-pressure.md`
- `structural-design/preliminary-sizing/required-section-properties.md`
- `structural-design/preliminary-sizing/support-and-composite-action.md`
- `structural-design/preliminary-sizing/calculation-status-and-traceability.md`

### 金屬面板／stiffener／FEA

- `cladding/structural-analysis/README.md`
- `cladding/structural-analysis/metal-panel-analysis.md`
- `cladding/structural-analysis/stiffener-analysis.md`
- `cladding/structural-analysis/panel-to-stiffener-connection.md`
- `cladding/structural-analysis/plate-fea-modeling.md`

### 活動窗／可開啟構件

- `operable-elements/README.md`
- `operable-elements/sash-frame-analysis.md`
- `operable-elements/hardware-load-path.md`
- `operable-elements/hinge-lock-stay-connections.md`
- `operable-elements/performance-and-life-cycle.md`

這些頁面刻意把「需求 mechanics」和「規範 capacity」分開。若 allowable / resistance / safety treatment 沒有可驗證來源，AI 應輸出 `INCOMPLETE`，不得從既有專案計算書、舊版手冊或記憶自動補值。

## 機器可讀 Schemas

通用 engineering data models 放在 repository 根目錄 `schemas/`。目前包括：

- `material.schema.json`
- `load-case.schema.json`
- `section-properties.schema.json`
- `deflection-criterion.schema.json`
- `support-joint.schema.json`：逐自由度 boundary-condition model
- `plate-fea-model.schema.json`：solver-independent FEA metadata
- `seismic-component.schema.json`：façade component seismic input / provenance model
- `structural-coverage.schema.json`：failure-mode coverage / completeness model
- `project-design-basis.schema.json`：project specification → structural design basis extraction model

Schema 不保存專案實例，只定義可供 AI / calculator / spreadsheet 共用的資料結構。正式 calculator 實作前仍應依 `AGENTS.md` 的 schema discipline 檢查 provenance、unit、scope 與 incomplete-state handling。

## 證據／公開安全規則

每個技術結論應優先連回 `references/` 中可公開追溯的 evidence；不要在多個頁面複製同一 canonical 結論或 current-edition snapshot。

若知識最初來自非公開專案文件，public repository 只保留重新泛化、去識別且可由公開技術來源支持的方法論；不得留下專案名稱、尺寸、荷載、圖號、節點、截圖或私人 provenance。