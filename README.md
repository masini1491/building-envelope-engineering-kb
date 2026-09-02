# Building Envelope Engineering Knowledge Base

以台灣建築外殼工程實務為核心的公開技術知識庫，供工程師與 AI（例如 ChatGPT / Codex）查詢、交叉驗證、計算審查與持續維護。

範圍包含但不限於：帷幕牆、玻璃、結構玻璃、鋁板與金屬外牆、石材、採光罩、材料與扣件、表面處理、防蝕、結構耐風／耐震、氣密／水密／層間變位試驗、活動窗、building physics、fire，以及相關 CNS / ASTM / AAMA-FGIA / ISO 標準與台灣工程實務。

## 核心原則

1. **Evidence first**：先有來源，再下工程結論。
2. **Authority aware**：區分法規、正式標準、政府手冊、專案文件、製造商資料、工程經驗與未驗證資訊。
3. **Current before cached**：涉及現行規範、版本或產品資料時，優先確認 freshness；舊聊天與 AI memory 不作正式技術來源。
4. **Reference, don't repeat**：同一規則、標準版本或技術結論只保留一個 canonical owner，其他頁面以連結／routing 為主。
5. **Progressive reading**：AI 先從本 README 與 `CHAT_INIT.md` 進入，再依題目讀最低必要內容。
6. **Incomplete is a valid result**：必要 input、criterion、capacity source、support model 或 provenance 不足時，應回傳 `INCOMPLETE`，不得補猜為 PASS。
7. **Public-safe**：不公開未授權施工圖、專案名稱／可辨識 geometry、客戶／公司機密、私人 provenance、受版權保護標準全文或其他不可再散布內容。

## Repository routing

- `AGENTS.md`：AI / maintainer 的治理、authority、來源、schema 與公開安全規則。
- `CHAT_INIT.md`：新聊天室最小啟動流程。
- `knowledge/`：整理後、可供工程師與 AI 直接使用的 canonical technical knowledge。
- `references/`：**只保存可公開散布**的來源、版本、適用範圍、限制與 evidence dossier。
- `schemas/`：AI / calculator / spreadsheet 共用的 machine-readable engineering data models。
- `indexes/`：未來需要 standards / materials / cross-reference lookup 時才建立的 machine-readable index；不與 `schemas/` 混用。
- `templates/`：新增標準、材料與工程知識時的固定格式。

## Structural methodology baseline

目前已建立的主要 structural chain：

```text
project specification / design basis
        ↓
load definition / load generation
        ↓
framing / panel / glass / sash response
        ↓
splice / composite action / movement
        ↓
fastener / local extrusion / weld / anchor
        ↓
primary structure interface
        ↓
performance test / validation
        ↓
failure-mode coverage / completeness review
```

主要入口：

- [`knowledge/structural-design/review/README.md`](knowledge/structural-design/review/README.md) — structural calculation review / coverage router
- [`knowledge/structural-design/review/project-specification-extraction.md`](knowledge/structural-design/review/project-specification-extraction.md) — project specification → Project Design Basis
- [`knowledge/structural-design/load-generation/README.md`](knowledge/structural-design/load-generation/README.md) — pressure / mass / point load → component demand
- [`knowledge/structural-design/framing/mullion-transom-design-baseline.md`](knowledge/structural-design/framing/mullion-transom-design-baseline.md) — mullion / transom baseline
- [`knowledge/structural-design/framing/continuous-mullion-analysis.md`](knowledge/structural-design/framing/continuous-mullion-analysis.md) — multi-span / support DOF
- [`knowledge/structural-design/framing/multi-part-extrusion-load-sharing.md`](knowledge/structural-design/framing/multi-part-extrusion-load-sharing.md) — composite-action guardrails
- [`knowledge/structural-design/connections/load-path-and-anchor-reactions.md`](knowledge/structural-design/connections/load-path-and-anchor-reactions.md) — connection / anchor load path
- [`knowledge/structural-design/seismic/README.md`](knowledge/structural-design/seismic/README.md) — Taiwan façade seismic force + movement routing
- [`knowledge/cladding/structural-analysis/README.md`](knowledge/cladding/structural-analysis/README.md) — metal panel / stiffener / plate-shell FEA
- [`knowledge/operable-elements/README.md`](knowledge/operable-elements/README.md) — operable sash / hardware / life-cycle routing
- [`knowledge/structural-glass/README.md`](knowledge/structural-glass/README.md) — structural glass / laminated effective thickness / point supports / movement / redundancy

## Standards / performance baseline

- [`knowledge/standards/performance-testing/curtain-wall-performance-crosswalk.md`](knowledge/standards/performance-testing/curtain-wall-performance-crosswalk.md) — CNS / ASTM / AAMA-FGIA performance-test crosswalk
- [`knowledge/structural-design/wind/taiwan-curtain-wall-wind-design-manual.md`](knowledge/structural-design/wind/taiwan-curtain-wall-wind-design-manual.md) — 內政部建研所帷幕耐風手冊 routing
- [`knowledge/structural-design/wind/taiwan-design-wind-pressure-workflow.md`](knowledge/structural-design/wind/taiwan-design-wind-pressure-workflow.md) — current Taiwan wind-design workflow

Cross-reference 只表示用途相關，不代表不同標準體系全文等價。

## Materials / finishes / durability baseline

- [`knowledge/materials/aluminum/common-curtain-wall-alloys.md`](knowledge/materials/aluminum/common-curtain-wall-alloys.md)
- [`knowledge/materials/steel/astm-a36.md`](knowledge/materials/steel/astm-a36.md)
- [`knowledge/materials/stainless-steel/stainless-steel-baseline.md`](knowledge/materials/stainless-steel/stainless-steel-baseline.md)
- [`knowledge/fasteners/stainless/iso-3506-a2-70-a2-90.md`](knowledge/fasteners/stainless/iso-3506-a2-70-a2-90.md) — A2-70 與非標準 A2-90 designation guardrail；不保存 private-project provenance
- [`knowledge/finishes/aluminum-organic-coatings-aama-2603-2604-2605.md`](knowledge/finishes/aluminum-organic-coatings-aama-2603-2604-2605.md)
- [`knowledge/corrosion-protection/hot-dip-galvanizing-astm-family.md`](knowledge/corrosion-protection/hot-dip-galvanizing-astm-family.md)
- [`knowledge/engineering-notes/aluminum-panel-flatness-and-oil-canning.md`](knowledge/engineering-notes/aluminum-panel-flatness-and-oil-canning.md)

## Glazing / sealants / envelope systems

- [`knowledge/glazing/glass-standards-baseline.md`](knowledge/glazing/glass-standards-baseline.md)
- [`knowledge/glazing/ASTM-E1300-design-routing.md`](knowledge/glazing/ASTM-E1300-design-routing.md)
- [`knowledge/sealants/structural-silicone-baseline.md`](knowledge/sealants/structural-silicone-baseline.md)
- [`knowledge/sealants/structural-silicone-bite-routing.md`](knowledge/sealants/structural-silicone-bite-routing.md)
- [`knowledge/sealants/weatherseal-joint-design.md`](knowledge/sealants/weatherseal-joint-design.md)
- [`knowledge/gaskets/elastomeric-gasket-baseline.md`](knowledge/gaskets/elastomeric-gasket-baseline.md)
- [`knowledge/stone/dimension-stone-cladding-baseline.md`](knowledge/stone/dimension-stone-cladding-baseline.md)
- [`knowledge/skylights/skylight-and-sloped-glazing-baseline.md`](knowledge/skylights/skylight-and-sloped-glazing-baseline.md)
- [`knowledge/building-physics/thermal-and-condensation-baseline.md`](knowledge/building-physics/thermal-and-condensation-baseline.md)
- [`knowledge/fire/perimeter-fire-barrier-and-joints.md`](knowledge/fire/perimeter-fire-barrier-and-joints.md)

## Machine-readable schemas

`schemas/` 已包含 material、load case、section properties、deflection criterion、support/joint DOF、plate/shell FEA metadata、seismic component、structural coverage 與 project design basis models。

Schema 是 engineering interchange contract，不是 project instance。正式 calculator 實作前必須確認 unit、provenance、standard/edition、scope、boundary condition 與 incomplete-state handling。

## Automated validation

`.github/workflows/validate-repo.yml` 會在 push / pull request 執行 `scripts/validate_repo.py`，目前檢查：

- JSON parse
- JSON Schema Draft 2020-12 meta-validation
- schema `$id` 不得使用 `example.invalid`
- Markdown relative-link existence
- knowledge frontmatter `verification_status`
- `references/` 不得建立 private-project dossier 目錄

這是 baseline guard；後續可再擴充 duplicate canonical-owner、standard-version ownership 與更多 privacy lint。

## Current hardening priorities

目前內容已由「建立 baseline」進入「consolidation / hardening」階段。後續優先：

1. 建立 `references/standards/`、`references/government/` 等 public evidence dossiers，集中 current-edition ownership。
2. 持續強化 JSON schemas 與 source/provenance model。
3. 擴充 automated validation：duplicate canonical-owner、standard-version ownership、privacy lint。
4. 補 AAMA 611、CNS 10007 / 1247 等尚未建立的 standards pages。
5. 視實際需求再建立 `indexes/`，不要為了目錄完整而預先複製資料。

## Licensing

本 repository 採雙授權模型，且只授權 repository maintainer 有權授權的原創內容：

- **工程知識／文件：CC BY 4.0** — 一般適用於 `README.md`、`AGENTS.md`、`CHAT_INIT.md`、`knowledge/`、repository-authored `references/` metadata/commentary、`templates/` 等文件內容。
- **schemas／scripts／code：MIT License** — 一般適用於 `schemas/`、`scripts/`、`.github/` 與其他明確屬於 software/tooling 的內容。

詳見：

- [`LICENSE.md`](LICENSE.md) — 授權範圍與雙授權總則
- [`LICENSE-DOCS.md`](LICENSE-DOCS.md) — CC BY 4.0 文件授權說明
- [`LICENSE-CODE`](LICENSE-CODE) — MIT License
- [`THIRD-PARTY-NOTICE.md`](THIRD-PARTY-NOTICE.md) — 第三方標準、出版物、商標與技術資料不因出現在本 Repo 而被重新授權
- [`DISCLAIMER.md`](DISCLAIMER.md) — engineering / AI review 免責與責任邊界

## Copyright / third-party boundary

ASTM、AAMA-FGIA、ISO、CNS、Aluminum Association、AWS、AISC、製造商資料與其他第三方作品可能受各自著作權、商標或授權條款限制。

本 repository 的 CC BY 4.0 / MIT 授權**不會重新授權這些第三方原始作品**。Repo 原則上只保存標準編號、版本資訊、適用範圍、合法可引用的最低充分內容、自行整理的工程摘要／routing 與官方或合法來源連結；不把付費／受限制標準全文或未授權 PDF 直接 commit 到公開 repository。

## Engineering responsibility boundary

本 repository 可支援工程研究、初步分析、計算審查與 AI-assisted review，但不取代 project-specific professional engineering judgment、技師簽證、主管機關審查、正式試驗、施工核可或 project approval。

**任何 AI / automated review 輸出的 `PASS` 都不構成專業工程認證、法規核准或施工授權。** 詳見 [`DISCLAIMER.md`](DISCLAIMER.md)。