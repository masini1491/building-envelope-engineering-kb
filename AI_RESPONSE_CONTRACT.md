# 人工智慧（AI）工程回覆增量規則（Engineering Reporting Delta）

本檔定義使用本 repository 回答建築外殼／帷幕工程問題時，相對於 shared AI Development Playbook `REPORTING.md` 的**專案特定工程回覆增量規則（project-specific engineering reporting delta）**。

跨專案共通的語言、result-first、scope fidelity、progress integrity、避免 presentation noise、reporting timestamp 與 pre-send presentation gate，由 `AGENTS.md` 宣告之 Playbook baseline 的 `REPORTING.md` 擁有。本檔不複製第二份 shared reporting policy，也不因被載入而啟用其他 Playbook governance。

本檔只控制 KB-specific engineering presentation delta，不重新定義工程公式、來源權威、標準版本、failure-mode methodology、project responsibility 或底層 evidence truth。工程 authority 仍依 [`AGENTS.md`](AGENTS.md) 與對應 `knowledge/` / `references/` canonical pages。

## 適用順序

工程回覆同時受到多層 contract 約束時，依下列原則處理：

1. 使用者當次明確要求的格式、深度與目的；
2. 本 repository 的 current engineering／review canonical owner；
3. 本檔的 KB-specific engineering reporting delta；
4. declared Playbook baseline 的 shared `REPORTING.md` 共通呈現 contract；
5. 一般聊天習慣。

若 shared reporting 與本 repository 的 project-specific engineering authority 發生衝突，以本 repository 較具體且較嚴的 engineering boundary 為準；presentation rule 不得改寫 evidence、status 或 validation truth。

## 工程事實、判斷與缺口

當三者混淆會影響工程決策時，應清楚區分：

- **已確認**：可由目前 project input、canonical KB 或 primary evidence 支持。
- **工程判斷／推論**：由已知條件推得，但不是來源原文直接聲明。
- **尚缺資料／待驗證**：目前 evidence 不足以安全下結論。

必要 input、criterion、standard edition、support model、factor、material property、connection geometry 或 responsibility boundary 不足時：

1. 先說目前能確認到哪一層；
2. 指出真正控制判斷的缺口；
3. 若該缺口會控制 acceptance，使用 scope-qualified `INCOMPLETE`；
4. 只要求會 materially 改變工程判斷的最低必要補充資料。

不得為了填滿格式而補猜工程數值、standard equivalence 或 project condition。

## 審查狀態（Review Status）

`PASS / WARNING / FAIL / INCOMPLETE / NOT_APPLICABLE` 主要用於**審查／verification task**，不是一般工程問答的固定模板。

Status 的正式語意與 aggregation 以相關 review canonical pages 為準，例如：

- [`knowledge/structural-design/review/README.md`](knowledge/structural-design/review/README.md)
- [`knowledge/structural-design/review/coverage-and-completeness.md`](knowledge/structural-design/review/coverage-and-completeness.md)

使用 status 時必須附 scope，例如：

- `member_flexure: PASS`
- `anchor_concrete_breakout: PASS`
- `factor_audit: WARNING`
- `primary_structure_local_effect: INCOMPLETE`

不得把局部 arithmetic／calculator／member／connection `PASS` 包裝成整體 façade system、整份計算書或完整工程安全 `PASS`。Calculator 的 `COMPUTED / MATCH / MISMATCH / INCOMPLETE_INPUT / UNSUPPORTED_MODEL` 等 execution／comparison status，也不得與 engineering acceptance status 混成同一維度。

## 快速工程問答增量

一般明確工程問題在 shared `REPORTING.md` 的 result-first contract 之上，只追加下列 KB-specific boundary：

- 已有足夠 canonical evidence 時直接回答，不得只回覆 router／檔案路徑要求使用者自行找結論。
- 只展開與當前 load path、component、standard 或 review scope materially 相關的 failure modes；不為形式列完整 checklist。
- 若答案需要 current standard／法規／manufacturer information，而 repository freshness 不足，先重新確認 current primary source，再形成工程結論。

## 工程計算／驗算呈現

需要呈現計算或 deterministic recomputation 時，至少保留：

`Inputs → Derived values → Formula / Method → Result → Criterion / Capacity source → Engineering status / conclusion`

要求：

- units 明確；
- positive / negative、axis、direction 不得丟失；
- factor 必須可追溯；
- design pressure / test pressure 不得混用；
- reported value 與 recomputed value 要能區分；
- 若只完成 demand／mechanics／comparison，不能假裝 capacity verification 或 engineering acceptance 已完成；
- repository calculator 的 execution status 與工程 acceptance status 分開呈現。

## 計算書／圖面／規範審查呈現

完整 review 應依 task-specific methodology 與實際 scope 組織。通常至少讓使用者能辨識：

1. governing engineering finding／目前 acceptance boundary；
2. 會影響接受與否、設計安全、責任界面或後續計算的 controlling issue；
3. scope-qualified review status；
4. 對應 canonical knowledge、project input 或 current public evidence；
5. 真正阻止 closure 的 evidence gap；
6. 若 review 會跨 revision／聊天室持續，current review record／reconciliation state。

Minor wording comment 與 governing load-path／capacity／responsibility issue 應分開，不得讓大量小問題掩蓋 material engineering finding。

## 證據與引用的工程增量

### 儲存庫內證據已足夠

- 優先以 canonical KB page 支持工程判斷；
- standard current edition / status 優先回到 `references/standards/` owner；
- 不為了看起來可靠而堆疊二手來源或同 lineage 的重複證據。

### 需要目前外部查證

法規、標準版本、產品、manufacturer literature 或其他可能變動資訊若 repository freshness 不足：

- 優先確認 current primary source；
- 將 external currentness evidence 與 KB cached／historical evidence 分開；
- 只呈現支持結論所需的最低充分 provenance，不把 research process 本身當答案。

### 私人專案證據

私人聊天中可依使用者提供的計算書、圖面、規範進行分析，但 public KB 維護必須遵守 [`AGENTS.md`](AGENTS.md) 的 private-to-public generalization／mosaic boundary：

- 本次 project judgment 可以使用私人 evidence；
- public KB conclusion 只保留去識別且可公開驗證的方法論；
- project-specific dimension、load、drawing number、private provenance 或 unique geometry 不得被包裝成 repository 通則。

## 工程用語防呆

除非 scope 真正支持，避免使用過度寬泛語句：

- 「整體安全」
- 「完全沒問題」
- 「符合所有規範」
- 「一定可以」
- 「等同於」

優先改成可追溯 scope，例如：

- 「就目前提供的 member flexure check，可判定 PASS。」
- 「anchor steel check 可確認；concrete edge breakout 尚缺 geometry，因此整體 anchor verification 仍為 INCOMPLETE。」
- 「兩個標準用途相關，但目前 evidence 不支持宣稱 equivalent。」

## 簡答與完整審查

使用者要求簡答時，保留工程結論與會改變結論的 critical caveat；可省略背景教學、完整 failure-mode map 與 research history，但不得省略 controlling uncertainty。

使用者要求全檢／完整 review 時，先依 canonical methodology 界定 scope 與 completeness，覆蓋必要 failure modes／responsibility boundaries；missing evidence 使用 `INCOMPLETE` 或其他既有 project taxonomy，不因篇幅要求而以假設填滿。

## 工程回覆前最低檢查

shared `REPORTING.md` 的 pre-send gate 之外，本 KB 只追加下列 engineering checks：

1. 工程結論是否超出目前 evidence／review scope？
2. 事實、工程推論與 unknown 是否在需要時清楚分離？
3. `PASS / WARNING / FAIL / INCOMPLETE / NOT_APPLICABLE` 是否有明確 object／scope？
4. 是否偷偷補入 safety factor、allowable、standard equivalence 或其他無 provenance 值？
5. calculation／comparison status 是否被誤寫成 engineering acceptance status？
6. current standard／法規／產品資訊若 materially 影響答案，freshness 是否足夠？
7. 私人 project evidence 是否被錯誤泛化成 public KB rule？

> 核心原則：**Shared `REPORTING.md` 擁有共通呈現；本檔只保存 building-envelope engineering 的 project-specific reporting delta。**
