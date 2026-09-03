# 建築外殼工程知識庫（Building Envelope Engineering Knowledge Base）

以台灣建築外殼工程實務為核心的公開技術知識庫，供工程師與 AI（例如 ChatGPT / Codex）查詢、交叉驗證、計算審查與持續維護。

範圍包含帷幕牆、玻璃與結構玻璃、鋁板／金屬外牆、石材、採光罩、材料與扣件、表面處理、防蝕、結構耐風／耐震、錨栓、背撐／次結構、性能試驗、水管理、活動窗、建築物理、防火，以及相關 CNS / ASTM / AAMA-FGIA / ISO 與台灣工程實務。

本知識庫採 **AI-assisted engineering knowledge management** 方式維護，由維護者以工程實務判斷主導，並使用 ChatGPT 協助資料整理、交叉查證、知識重構與文件維護；工程結論仍以現行法規、正式標準、政府資料、製造商正式文件與其他可追溯工程證據為依據。**ChatGPT 是知識整理工具，不是工程權威來源。**

## 核心原則

1. **證據優先（Evidence first）**：先有來源，再下工程結論。
2. **辨識來源權威（Authority aware）**：法規、正式標準、政府資料、專案文件、製造商資料與工程觀察不可混為同一層級。
3. **現行資訊優先（Current before cached）**：標準版本、法規與產品資料可能更新時，重新查證 freshness。
4. **單一 canonical owner**：同一規則、標準版本或工程結論只維護一個 owner，其他頁面用 routing / link。
5. **漸進式讀取（Progressive reading）**：AI 不預設掃完整個 Repo，只讀回答問題所需的最低充分內容。
6. **`INCOMPLETE` 是有效結果**：必要 input、criterion、capacity source、support model 或 provenance 不足時，不得補猜為 PASS。
7. **公開安全（Public-safe）**：不公開未授權施工圖、計算書、可辨識專案條件、私人 provenance 或受版權限制全文。

完整治理規則見 [`AGENTS.md`](AGENTS.md)。AI 精簡啟動與載入策略見 [`CHAT_INIT.md`](CHAT_INIT.md)。AI 工程回覆呈現規則見 [`AI_RESPONSE_CONTRACT.md`](AI_RESPONSE_CONTRACT.md)。語言規則見 [`LANGUAGE.md`](LANGUAGE.md)。

## 快速導入人工智慧（AI）

本 repository 已設計為可直接交由 ChatGPT、Codex 或其他可讀取 GitHub repository 的 AI 使用，不需要把整個知識庫複製進 prompt，也不需要人工逐頁指定要讀哪些文件。

最小導入方式：

1. 將本 repository 提供給 AI。
2. 要求 AI 先讀 [`CHAT_INIT.md`](CHAT_INIT.md)。
3. AI 依 `knowledge-index → domain manifest → canonical leaf page` 漸進式載入最低必要內容。
4. 只有在 Repository 維護、工程審查、標準 provenance 或其他特定任務時，才條件式載入對應治理文件。

因此一般使用者不需要自行管理每一份知識文件，也不需要要求 AI 預先掃描整個 repository。

**目標不是讓 AI 記住整個 Repo，而是讓 AI 能快速找到唯一、最新且足夠的工程權威內容。**

## 快速開始

### 給工程師／一般使用者

先進入 [`knowledge/README.md`](knowledge/README.md)，依主題選擇 domain。

主要入口：

- [`knowledge/structural-design/README.md`](knowledge/structural-design/README.md) — 結構設計／計算審查總 router
- [`knowledge/structural-glass/README.md`](knowledge/structural-glass/README.md) — 結構玻璃
- [`knowledge/water-management/README.md`](knowledge/water-management/README.md) — 雨水侵入、等壓、排水
- [`knowledge/operable-elements/README.md`](knowledge/operable-elements/README.md) — 活動窗／可開啟構件
- [`knowledge/design-management/curtain-wall-design-workflow.md`](knowledge/design-management/curtain-wall-design-workflow.md) — 帷幕設計作業流程
- [`knowledge/performance-testing/curtain-wall-performance-crosswalk.md`](knowledge/performance-testing/curtain-wall-performance-crosswalk.md) — CNS / ASTM / AAMA-FGIA 性能試驗 crosswalk

### 給 ChatGPT / Codex

新 session 優先讀 [`CHAT_INIT.md`](CHAT_INIT.md) 作為精簡 bootstrap，再依任務條件載入：

1. 一般工程問答：用 [`indexes/knowledge-index.json`](indexes/knowledge-index.json) 的 `aliases / entrypoint` 路由，只讀最低必要的 `knowledge/` 頁面。
2. 需要標準版本、來源或 provenance：再用 [`indexes/standards-index.json`](indexes/standards-index.json) 找對應 `references/standards/` dossier。
3. 計算書／圖面／規範審查：再讀 [`AI_RESPONSE_CONTRACT.md`](AI_RESPONSE_CONTRACT.md) 與相關 review methodology。
4. Repository 維護／新增／修改：再讀 [`AGENTS.md`](AGENTS.md)，並依需要載入 `LANGUAGE.md`、templates、schemas 與 validator。
5. Repository evidence 不足或 freshness 不明時，再查 current primary source。

**一般明確問答不要求無條件完整載入 README、AGENTS 與 AI_RESPONSE_CONTRACT。** 目標是以最低充分上下文找到正確 canonical owner，降低重複 token 與 instruction dilution。

## 儲存庫（Repository）結構

- [`knowledge/`](knowledge/)：整理後、供工程師與 AI 直接使用的 canonical engineering knowledge。
- [`references/`](references/)：**只保存可公開散布**的 public evidence dossier、版本、scope、限制與 provenance。
  - `references/standards/` 是標準 current-edition / status 的優先 owner。
  - [`references/github-projects/`](references/github-projects/) 是 NON-NORMATIVE 軟體／實作參考。
- [`schemas/`](schemas/)：AI / calculator / spreadsheet 共用的 machine-readable engineering data models。
- `indexes/`：machine-readable routing / lookup index；`knowledge-index.json` 提供 domain aliases 與 entrypoint，index 不複製 knowledge 本體。
- [`templates/`](templates/)：新增 knowledge / reference 時的格式骨架。
- [`scripts/`](scripts/) 與 `.github/`：repository validation / maintenance tooling。

## 關鍵工程防呆

本 Repo 不自行捏造或從不相干資料推算：

- 材料強度／allowable / resistance
- safety factor / hidden multiplier
- test pressure / duration
- bolt proof / torque
- glass capacity / interlayer shear modulus
- structural silicone allowable design stress
- 標準等價關係

Cross-reference 只代表用途相關，不代表 CNS / ASTM / AAMA-FGIA / ISO 等不同體系全文等價。

結構審查特別區分：

`Project Design Basis`
→ `load generation`
→ `member / panel / glass response`
→ `connection / anchor`
→ `secondary support / primary-structure interface`
→ `movement / performance validation`
→ `failure-mode coverage`

任一局部 `PASS` 不自動代表整體系統 `PASS`。

## 自動驗證

`.github/workflows/validate-repo.yml` 執行 `scripts/validate_repo.py`。目前 baseline 包含：

- JSON / JSON Schema validation
- Markdown relative-link existence
- knowledge verification status / canonical ownership
- public-reference privacy rule
- standards dossier machine metadata / standards-index 對應
- `LANGUAGE.md` 繁中 heading lint
- architecture / AI routing index lint

## 授權與責任

本 repository 採雙授權模型，且只授權 maintainer 有權授權的原創內容：

- 工程知識／文件：CC BY 4.0
- schemas／scripts／code：MIT License

詳見：

- [`LICENSE.md`](LICENSE.md)
- [`LICENSE-DOCS.md`](LICENSE-DOCS.md)
- [`LICENSE-CODE`](LICENSE-CODE)
- [`THIRD-PARTY-NOTICE.md`](THIRD-PARTY-NOTICE.md)
- [`DISCLAIMER.md`](DISCLAIMER.md)

> 本知識庫是工程研究、查核與 AI 輔助工具，不取代專案契約、正式標準原文、製造商 project review 或依法應由合格專業人員承擔的設計責任。