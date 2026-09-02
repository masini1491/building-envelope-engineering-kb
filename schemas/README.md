# Machine-readable Engineering Schemas

`schemas/` 定義 AI、calculator、spreadsheet 或其他工具可共用的**通用 engineering interchange contract**。Schema 不保存 project instance，也不代表某一專案或某一標準已核准特定設計值。

## 分類

### 核心輸入／設計依據

- `material.schema.json`：材料、product form、condition、mechanical/design properties 與 provenance。
- `load-case.schema.json`：load source 與 pressure / line / point / displacement 等 application。
- `project-design-basis.schema.json`：project specification → structured design basis。
- `design-factor.schema.json`：load / resistance / safety / allowable / test multiplier 與 factor ledger。

### 結構模型／分析資料

- `section-properties.schema.json`：`A / centroid / Ixx / Iyy / Ixy / J / Cw` 等截面資料。
- `support-joint.schema.json`：逐自由度 boundary condition、release、spring、gap 與 transfer intent。
- `plate-fea-model.schema.json`：solver-independent plate / shell FEA metadata。
- `seismic-component.schema.json`：façade component seismic input / classification / provenance。
- `deflection-criterion.schema.json`：serviceability criterion、方向、scope、source。

### Review／coverage

- `structural-coverage.schema.json`：failure-mode coverage、scope 與 `PASS / WARNING / FAIL / INCOMPLETE / NOT_APPLICABLE`。

## 維護規則

- JSON Schema Draft 2020-12。
- `$id` 使用本 repository 的穩定 namespace。
- Unit 必須明示；不得靠欄位上下文猜測。
- Material allowable / resistance 不得脫離 standard、edition、product form、condition、limit state 與 provenance。
- Design pressure、test pressure、reaction、imposed displacement 等不同 engineering objects 不得為方便而合併成單一 scalar。
- Schema 必須能表示 provisional / unknown / incomplete；不要逼迫使用者填入猜測值。
- Schema path 與 `$id` 若已被 calculator / external tool 使用，避免只為目錄美觀而搬動。

## 與 Knowledge 的關係

`knowledge/` 定義工程方法與 guardrails；`schemas/` 定義資料交換格式。

例如：

- `knowledge/structural-design/framing/` 解釋 support / composite-action mechanics；
- `support-joint.schema.json` 只提供對應資料模型。

Schema 通過 validation 不代表工程內容已通過 governing-code review。

> 新增 schema 前先確認既有 schema 是否能擴充；避免同一 engineering object 出現兩套互不相容的資料模型。