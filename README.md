# Building Envelope Engineering Knowledge Base

以台灣建築外殼工程實務為核心的公開技術知識庫，供工程師與 AI（例如 ChatGPT / Codex）查詢、交叉驗證與持續維護。

本 repository 的範圍包含但不限於：帷幕牆、玻璃、鋁板與金屬外牆、石材、採光罩、材料與扣件、表面處理、防蝕、結構耐風、氣密／水密／層間變位試驗，以及相關 CNS / ASTM / AAMA-FGIA / ISO 標準與台灣工程實務。

## 核心原則

1. **Evidence first**：先有來源，再下工程結論。
2. **Authority aware**：明確區分法規、正式標準、政府手冊、專案文件、製造商資料、工程經驗與未驗證資訊。
3. **Current before cached**：涉及現行規範、版本或產品資料時，優先確認 freshness；舊聊天與 AI memory 不作為正式技術來源。
4. **Reference, don't repeat**：同一規則或技術結論只保留一個 canonical owner，其他頁面以連結／路由為主，避免 drift。
5. **Progressive reading**：AI 不應預設完整掃描 repository；先從本 README 與 `CHAT_INIT.md` 進入，再依題目讀最低必要內容。
6. **Public-safe**：不公開未授權施工圖、客戶／公司機密、受版權保護標準全文或其他不可再散布內容。

## Repository 路由

- `AGENTS.md`：AI / maintainer 的治理、authority、來源與公開安全規則。
- `CHAT_INIT.md`：新聊天室最小啟動流程。
- `knowledge/`：整理後、可供工程師與 AI 直接使用的技術結論。
- `references/`：來源、provenance、版本、適用範圍、限制與 evidence dossier。
- `indexes/`：規範、材料與 cross-reference 的機器可讀索引。
- `templates/`：新增標準、材料、工程筆記與專案知識時的固定格式。

## 預定知識範圍

### Standards / performance testing

- CNS 13971 / 13972 / 13973 / 13974 / 14280 / 14281
- ASTM E283 / E330 / E331 / E1105 / E1233 等
- AAMA / FGIA 501 系列、503 等

### Materials

- 鋁板：3003-H14、3004-H12 等
- 鋁擠型：6063-T5、6005-T5、6105-T5 等
- 結構鋼：ASTM A36 等
- 不鏽鋼與其他建築外殼常用材料

### Finishes / corrosion protection

- AAMA 2603 / 2604 / 2605
- AAMA 611
- ASTM A123 / A153 / A780 / A384 / A385
- CNS 熱浸鍍鋅相關規範

### Fasteners

- ISO 3506 系列
- A2-70 / A2-80 與專案特殊高強度扣件
- ISO 898-1、ASTM fastener standards
- tension / shear / bearing / thread engagement / galling / galvanic corrosion

### Structural design / manuals

- 《帷幕牆系統結構耐風設計手冊》
- 設計風壓、有效受風面積、直料、橫料、繫件、螺栓、玻璃、結構矽膠等

### Engineering notes / case knowledge

保存標準沒有直接回答、但工程實務反覆遇到的問題，例如：

- 3003-H14 與 3004-H12 的選用差異
- 鋁板平整度與 oil canning
- 材料替代時應驗證的項目
- 重大專案的特殊規格，但只保存可公開的抽象化工程知識，不上傳機密原始文件

## Copyright / licensing boundary

ASTM、AAMA-FGIA、ISO、CNS 與其他第三方標準可能受著作權或授權條款限制。本 repository 原則上只保存：

- 標準編號與版本資訊
- 適用範圍與工程摘要
- 必要的 cross-reference
- 合法可引用的最低充分內容
- 官方或合法來源連結
- 自行整理的工程解讀與注意事項

不把付費／受限制標準全文或未授權 PDF 直接 commit 到公開 repository。

## Status

目前為初始化階段。第一優先是建立 standards / materials / finishes / fasteners / structural-design 的可信 baseline，再逐步擴張至其他 building-envelope 領域。
