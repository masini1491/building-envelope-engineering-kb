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
- `structural-design/`：耐風、直料、橫料、anchor、glass、silicone，以及 `preliminary-sizing/` 前期 required section property / support / traceability 方法
- `engineering-notes/`：標準無法單獨回答的實務問題
- `stone/`：天然石材外牆與繫件系統
- `cladding/`：金屬複合板、蜂巢板及其他外牆面板系統
- `skylights/`：採光罩與斜面玻璃
- `building-physics/`：thermal、thermal bridge、condensation
- `fire/`：perimeter fire barrier、fire-resistive joint 與外牆防火 routing
- `case-knowledge/`：只用於公開來源可追溯案例，或完全去識別且無法反推出專案身分的通用 lesson pattern

機器可讀的通用 engineering data models 放在 repository 根目錄 `schemas/`，目前包含 material、load case、section properties 與 deflection criterion。Schema 不保存專案實例，只定義可供 AI / calculator / spreadsheet 共用的資料結構。

每個技術結論應連回 `references/` 中可追溯的公開 evidence；不要在多個頁面複製同一 canonical 結論。

若知識最初來自非公開專案文件，public repository 只保留重新泛化、去識別且可由公開技術來源支持的方法論；不得留下專案名稱、尺寸、荷載、圖號、節點、截圖或私人 provenance。
