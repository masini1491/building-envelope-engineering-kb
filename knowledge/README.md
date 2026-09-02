# Knowledge

本目錄保存已整理、可供工程師與 AI 直接使用的技術結論。

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
- `structural-design/`：耐風、耐震、荷載生成、直料／橫料、多件擠型共同作用、continuous mullion / splice / sleeve、雙軸彎曲、glass-edge relative displacement、fastener group、screw pull-out / thread engagement、局部擠型、焊道群、anchor，以及 `preliminary-sizing/` 前期 required section property / support / traceability 方法
- `operable-elements/`：活動窗／可開啟外牆構件的 sash/frame、hinge/lock/stay、五金緊件、局部擠型與 whole-product performance / life-cycle routing
- `engineering-notes/`：標準無法單獨回答的實務問題
- `stone/`：天然石材外牆與繫件系統
- `cladding/`：金屬複合板、蜂巢板及其他外牆面板系統；`structural-analysis/` 另整理 metal panel、stiffener、panel-to-stiffener connection 與 plate / shell FEA methodology
- `skylights/`：採光罩與斜面玻璃
- `building-physics/`：thermal、thermal bridge、condensation
- `fire/`：perimeter fire barrier、fire-resistive joint 與外牆防火 routing
- `case-knowledge/`：只用於公開來源可追溯案例，或完全去識別且無法反推出專案身分的通用 lesson pattern

## Structural calculation routing

目前已建立的 structural methodology 主線包括：

### Load generation

- `structural-design/load-generation/README.md`
- `structural-design/load-generation/facade-tributary-loads.md`
- `structural-design/load-generation/transom-wind-load-distribution.md`
- `structural-design/load-generation/glass-dead-load-and-setting-blocks.md`

### Framing

- `structural-design/framing/mullion-transom-design-baseline.md`
- `structural-design/framing/continuous-mullion-analysis.md`
- `structural-design/framing/splice-and-sleeve-modeling.md`
- `structural-design/framing/multi-part-extrusion-load-sharing.md`
- `structural-design/framing/biaxial-bending-and-resultant-deflection.md`
- `structural-design/framing/glass-edge-relative-deflection.md`

### Connections

- `structural-design/connections/load-path-and-anchor-reactions.md`
- `structural-design/connections/fastener-group-analysis.md`
- `structural-design/connections/screw-pullout-and-thread-engagement.md`
- `structural-design/connections/local-extrusion-failure.md`
- `structural-design/connections/weld-group-analysis.md`

### Seismic façade components / connections / movement

- `structural-design/seismic/README.md`
- `structural-design/seismic/taiwan-facade-component-seismic-force.md`
- `structural-design/seismic/seismic-connection-load-path.md`
- `structural-design/seismic/seismic-movement-compatibility.md`

### Metal panel / stiffener / FEA

- `cladding/structural-analysis/README.md`
- `cladding/structural-analysis/metal-panel-analysis.md`
- `cladding/structural-analysis/stiffener-analysis.md`
- `cladding/structural-analysis/panel-to-stiffener-connection.md`
- `cladding/structural-analysis/plate-fea-modeling.md`

### Operable windows / vents

- `operable-elements/README.md`
- `operable-elements/sash-frame-analysis.md`
- `operable-elements/hardware-load-path.md`
- `operable-elements/hinge-lock-stay-connections.md`
- `operable-elements/performance-and-life-cycle.md`

這些頁面刻意把「需求 mechanics」和「規範 capacity」分開。若 allowable / resistance / safety treatment 沒有可驗證來源，AI 應輸出 `INCOMPLETE`，不得從既有專案計算書、舊版手冊或記憶自動補值。

機器可讀的通用 engineering data models 放在 repository 根目錄 `schemas/`，目前包含 material、load case、section properties、deflection criterion、`support-joint.schema.json` 的逐自由度 boundary-condition model、`plate-fea-model.schema.json` 的 solver-independent FEA metadata，以及 `seismic-component.schema.json` 的 façade component seismic input / provenance model。Schema 不保存專案實例，只定義可供 AI / calculator / spreadsheet 共用的資料結構。

每個技術結論應連回 `references/` 中可追溯的公開 evidence；不要在多個頁面複製同一 canonical 結論。

若知識最初來自非公開專案文件，public repository 只保留重新泛化、去識別且可由公開技術來源支持的方法論；不得留下專案名稱、尺寸、荷載、圖號、節點、截圖或私人 provenance。
