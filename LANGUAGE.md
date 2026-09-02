# 繁體中文與技術術語規則

本 repository 以**繁體中文（台灣）**作為主要的人類可讀語言，同時保留必要的英文工程術語，以避免翻譯造成技術歧義。

本規則適用於 README、knowledge pages、references、templates、AI 回答與其他人類可讀文件；machine-readable schema、程式碼、標準正式名稱與識別碼依下列例外處理。

## 核心原則

1. **敘述以繁體中文為主**：章節標題、說明文字、表格欄名、審查結論與 AI 預設回答使用繁體中文。
2. **技術精確性優先於硬翻譯**：英文術語若翻譯後可能改變工程語意，保留原文。
3. **採台灣工程用語**：已有穩定台灣用語時優先採用，不使用簡體字或僅適用中國大陸語境的譯詞取代台灣既有用法。
4. **首次出現可中英並列**：有穩定中文詞且保留英文有助檢索時，建議使用 `中文（English）`，後續可依上下文只使用中文或英文。
5. **人類可讀標題採中文優先**：若標題同時包含中文與一般英文詞，原則上讓中文概念先出現，例如 `排水孔（weep）防呆`，而不是 `Weep 防呆`。正式標準編號、材料牌號、產品名稱、固定 machine-readable status 等例外可維持原始識別順序。
6. **不為繁中化破壞資料介面**：schema key、程式識別碼、檔案路徑、公式符號、API field 等維持既有穩定名稱。

## 應以繁體中文呈現的內容

原則上以下內容使用繁體中文：

- 文件標題與章節標題
- 工程方法說明
- 審查流程與 checklist 說明
- failure-mode 的人類可讀說明
- 表格欄位名稱與註解
- AI 對使用者的預設回答
- README / router / onboarding 文件
- public reference dossier 的摘要、限制與不可推論事項
- 授權範圍、第三方權利與工程免責的 repository-authored 說明

例如：

- `荷載路徑（load path）`
- `複合作用（composite action）`
- `局部挫屈（local buckling）`
- `邊界條件（boundary condition）`
- `不完整（INCOMPLETE）`

## 可保留英文或原始正式名稱的內容

下列內容通常不應為了繁中化而改名或硬翻：

- 標準編號：`ASTM E330/E330M`、`CNS 13972`、`AAMA 501.4`
- 標準正式英文名稱；必要時可在旁補繁中用途摘要
- 材料與牌號：`6063-T5`、`3004-H12`、`A2-70`
- alloy / temper / property class
- 產品名稱、商標與 manufacturer 正式名稱
- schema key、JSON field、enum value
- 程式函式、變數、class、API 名稱
- 檔案與資料夾路徑
- 數學符號、公式與工程單位
- `PASS / WARNING / FAIL / INCOMPLETE / NOT_APPLICABLE` 等已定義 machine-readable status
- `load path`、`failure mode`、`composite action`、`effective thickness`、`oil canning` 等在中文工程溝通中保留英文更不易歧義的詞；可中英並列

## 不要機械式翻譯

繁中化不是把所有英文詞逐字翻成中文。

若中文譯詞：

- 在台灣工程界沒有穩定用法；
- 可能和另一個結構／材料概念混淆；
- 會讓標準檢索或跨國技術溝通變困難；

則保留英文，並用繁體中文解釋其工程意義。

例如 `proof load`、`bite`、`galling`、`prying`、`oil canning` 等，應依上下文決定是否中英並列，而不是創造不常用的中文名稱。

## 人工智慧（AI）回答規則

使用本 repository 的 ChatGPT、Codex 或其他 AI：

1. 除非使用者另有要求，**預設以繁體中文（台灣）回答**。
2. 技術術語可保留英文，但句子結構、說明與結論應以繁體中文為主。
3. 引用原始來源時保留來源原文，不擅自把正式標準名稱翻譯成看似官方的中文名稱。
4. 若中英文術語可能造成不同解讀，應明示兩者對應，而不是默默替換。
5. machine-readable output（JSON / YAML / schema instance）必須維持規定的 key / enum，不因回答語言而改名。

## 法律與授權文件

- `LICENSE-CODE` 保存 MIT License 的官方英文文字，**不得為繁中化而改寫或翻譯取代**。
- `LICENSE.md`、`LICENSE-DOCS.md`、`THIRD-PARTY-NOTICE.md` 與 `DISCLAIMER.md` 可使用繁體中文說明 repository 的授權範圍與責任邊界。
- CC BY 4.0 的實際授權條款以 Creative Commons 官方授權頁與 legal code 為準；repository 的繁中說明不是另一份翻譯法律文本。

## 資料結構（Schema）與程式碼

`schemas/`、`scripts/`、`.github/` 的識別碼與機器介面以穩定性優先：

- 不因繁中化重新命名 JSON keys。
- 不因繁中化改 enum value。
- 不因繁中化改 file path 而造成既有連結或程式失效。
- human-readable `title` / `description` 可視需要逐步補繁中說明，但不得犧牲跨工具互通性。

## 文件維護

新增或改寫人類可讀文件時：

- 優先使用繁體中文標題。
- 主要段落應能讓台灣工程師不依賴英文長句即可理解。
- 保留真正有技術價值的英文詞，不追求「零英文」。
- 不要只因檔名是英文就重新命名；檔名／URL 穩定性優先。
- 原始證據是英文時，可用繁中摘要，但不得改變來源實際支持的內容。

> 本 repository 的目標是「繁體中文優先的工程知識庫」，不是「所有工程詞彙全部中文化」的翻譯專案。