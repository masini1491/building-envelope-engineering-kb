# 技術知識（Knowledge）

本目錄保存已整理、可供工程師與 AI 直接使用的 canonical engineering knowledge。人類可讀內容依 [`../LANGUAGE.md`](../LANGUAGE.md) 以繁體中文（台灣）為主；標準正式名稱、材料牌號、schema key、公式符號與必要英文工程術語保留原文。

使用原則：**先選 domain，再讀該 domain router；不要從本頁直接掃所有 leaf pages。**

## Domain routing

- [`systems/`](systems/)：帷幕牆系統型式與 system-level 分類。
- [`design-management/`](design-management/)：Project Design Basis、system development、跨部門 review、mock-up、材料／圖面 release 與 revision control。
- [`materials/`](materials/)：鋁、鋼、不鏽鋼等材料與材料替代／選用方法。
- [`fasteners/`](fasteners/)：螺絲、螺栓、property class 與扣件 engineering guardrails。
- [`anchors/`](anchors/)：cast-in embedded plate、post-installed mechanical anchor、qualification / design / installation routing。
- [`finishes/`](finishes/)：鋁表面處理與塗裝。
- [`corrosion-protection/`](corrosion-protection/)：鍍鋅、防蝕與材料相容性。
- [`glazing/`](glazing/)：一般建築玻璃產品與 glass design-standard routing。
- [`structural-glass/`](structural-glass/)：glass fin、laminated effective thickness、point-supported / drilled glass、FEA、movement、walkable glass、post-breakage / redundancy。
- [`sealants/`](sealants/)：structural silicone、weatherseal 與 joint design。
- [`gaskets/`](gaskets/)：EPDM / silicone 等 gasket engineering baseline。
- [`cladding/`](cladding/)：金屬面板、複合板／蜂巢板、完成面與 panel-specific structural analysis。
- [`stone/`](stone/)：天然石材外牆與 fixing system。
- [`skylights/`](skylights/)：採光罩與斜面玻璃。
- [`operable-elements/`](operable-elements/)：活動窗／可開啟構件的 sash、hardware、connection、whole-product performance / life cycle。
- [`water-management/`](water-management/)：雨水侵入機制、pressure equalization / rainscreen、drainage / weep。
- [`building-physics/`](building-physics/)：thermal、thermal bridge、condensation。
- [`fire/`](fire/)：perimeter fire barrier、fire-resistive joint 與外牆防火 routing。
- [`performance-testing/`](performance-testing/)：氣密／水密／結構／層間位移等 performance-test crosswalk 與後續試驗方法論。
- [`structural-design/`](structural-design/)：耐風、耐震、荷載生成、frame mechanics、connections、secondary support、preliminary sizing 與 calculation review。

## 結構工程入口

結構問題優先從 [`structural-design/README.md`](structural-design/README.md) 開始，再依問題進入：

- wind / seismic
- load generation
- framing
- connections
- secondary support / reaction handoff
- preliminary sizing
- review / coverage / hidden multiplier audit

Component-specific mechanics 仍留在其 domain，例如 structural glass、metal panel、operable elements、anchors；不因「需要結構計算」就全部搬入 `structural-design/`。

## 標準與來源 ownership

- 工程解讀放 `knowledge/`。
- 標準 current edition / status、官方 URL、查證日期與 provenance 優先由 [`../references/standards/`](../references/standards/) 單一維護。
- 政府技術資料由 [`../references/government/`](../references/government/) 保存 public dossier。
- 公開 GitHub 軟體／工程專案只放 [`../references/github-projects/`](../references/github-projects/)，一律視為 NON-NORMATIVE implementation reference。

Knowledge page 不應為方便而在多處獨立維護同一標準的 current-edition snapshot。

## 機器可讀資料

通用 engineering data models 位於 [`../schemas/`](../schemas/)；它們是 interchange contract，不保存 project instance，也不取代 governing engineering method。

Machine-readable routing / lookup 放 `../indexes/`；index 不複製 knowledge 內容，只提供 path、domain、document type、canonical key 等檢索資訊。

## 公開安全

若知識最初來自私人計算書、施工圖、專案規範或教育訓練資料，public repository 只保留：

- 去識別後的 engineering principle；
- 可由 public source 支持的方法論；
- generic failure mode / review guardrail。

不得留下 project name、樓層、尺寸、荷載、圖號、節點、截圖、私人檔名或 private provenance。

> `knowledge/` 是工程結論層，不是來源文件倉庫，也不是不知道該放哪裡時使用的 `engineering-notes` catch-all。