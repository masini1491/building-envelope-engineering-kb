# AI 工程回覆呈現規則（AI Response Contract）

本檔定義使用本 repository 回答建築外殼／帷幕工程問題時的**人類可讀回覆 contract**。

它只控制「答案怎麼呈現」，不重新定義工程公式、來源權威、標準版本、failure-mode methodology 或 project responsibility。工程 authority 仍依 [`AGENTS.md`](AGENTS.md) 與對應 `knowledge/` / `references/` canonical pages。

## 優先順序

回覆格式與深度依下列順序決定：

1. 使用者當次明確要求的格式、深度與目的；
2. task-specific canonical knowledge / review methodology；
3. 本檔的預設回覆 contract；
4. 一般聊天習慣。

若使用者只問一個明確問題，不應為了套模板把答案擴成完整報告。

## 核心原則

### 結論優先

能直接回答時，先回答使用者真正問的事，再提供最低充分理由。

例如使用者問「這個做法可以嗎？」：

- 第一段先回答「可以／不建議／目前無法確認」。
- 後面才說控制條件、依據與缺口。

不要先鋪陳大量背景才讓使用者自行找結論。

### 回覆深度與問題成比例

- 簡單 factual / routing 問題：短答即可。
- 比較／選擇問題：先給差異與判斷，再補必要限制。
- 計算／設計問題：交代 inputs、method、result、criterion 與 status。
- 計算書／圖面／規範審查：使用 scope-qualified review status。
- 研究／建立 methodology：才展開 evidence hierarchy、failure modes 與 research gaps。

**不要因 repository 很大，就把所有相關知識一次倒進答案。** Progressive reading 也應對應 progressive answering。

### 事實、工程判斷與缺口不可混寫

當三者可能影響使用者決策時，應清楚區分：

- **已確認**：可由目前 project input、canonical KB 或 primary evidence 支持。
- **工程判斷／推論**：由已知條件推得，但不是來源原文直接聲明。
- **尚缺資料／待驗證**：目前 evidence 不足以安全下結論。

不需要每一句都加標籤；只有當混淆會影響工程結論時才明示分層。

### 缺資料時不要補猜

必要 input、criterion、standard edition、support model、factor、material property、connection geometry 或 responsibility boundary 不足時：

1. 先說目前**能確認到哪一層**；
2. 明確指出**哪一項仍不能確認**；
3. 若該缺口會控制 PASS / FAIL，使用 `INCOMPLETE`；
4. 只要求真正會改變判斷的最低必要補充資料。

不要列十幾個「可能需要」的資料，把使用者真正缺的關鍵 input 淹沒。

## Review Status 使用規則

`PASS / WARNING / FAIL / INCOMPLETE / NOT_APPLICABLE` 主要用於**審查／verification task**，不是每個一般問答都必須套 status。

Status 的語意與 aggregation 以相關 review canonical pages 為準，例如：

- [`knowledge/structural-design/review/README.md`](knowledge/structural-design/review/README.md)
- [`knowledge/structural-design/review/coverage-and-completeness.md`](knowledge/structural-design/review/coverage-and-completeness.md)

使用 status 時必須附 scope，例如：

- `member_flexure: PASS`
- `anchor_concrete_breakout: PASS`
- `factor_audit: WARNING`
- `primary_structure_local_effect: INCOMPLETE`

不得只寫沒有範圍的：

- `STRUCTURE: PASS`
- `ANCHOR: OK`
- `SYSTEM SAFE`

局部 PASS 不得被語言包裝成整體系統安全結論。

## 預設回答結構

### A. 快速工程問答

預設結構：

1. **結論**：直接回答。
2. **關鍵理由**：1～3 個真正控制判斷的因素。
3. **必要限制**：只有會改變答案時才補。

不需要固定小標；自然段落即可。

### B. 比較／選型／替代

優先回答：

1. 哪個選項較適合目前條件；
2. 差異真正來自哪裡；
3. 哪些條件成立時結論會反轉；
4. 哪些項目仍需 project-specific verification。

若使用表格能降低閱讀成本，可使用表格；不要為了格式完整而把沒有證據的欄位填滿。

### C. 工程計算／驗算

至少保留：

`Inputs`
→ `Derived values`
→ `Formula / Method`
→ `Result`
→ `Criterion / Capacity source`
→ `Status / conclusion`

要求：

- units 明確；
- positive / negative、axis、direction 不得丟失；
- factor 必須可追溯；
- design pressure / test pressure 不得混用；
- 若只完成 demand 或 mechanics，不能假裝 capacity verification 已完成。

### D. 計算書／圖面／規範審查

建議順序：

1. **總結論**：最重要的 PASS / FAIL / INCOMPLETE / risk。
2. **控制性發現**：只列會影響接受與否、設計安全、責任界面或後續計算的項目。
3. **Scope-qualified status**：必要時用表格整理。
4. **證據／依據**：連到 canonical knowledge、project input 或 current public source。
5. **缺口**：只列真正阻止 closure 的資料。

若有很多 minor comment，應與 governing issue 分開，不要讓十個小 wording issue 淹沒一個真正的 load-path failure。

## 回覆精簡規則

### 不重複同一結論

同一個核心結論通常只需要：

- 開頭說一次；
- 後文用 evidence 支持。

不要在「結論」「總結」「最後建議」三個區塊用不同句子重複同一件事。

### 不把 Router 當答案

回答工程問題時可以引用 canonical page，但不能只回：

> 請看某某頁。

若目前 evidence 已足夠，仍應直接回答使用者問題；routing 是證據與延伸閱讀，不是逃避判斷的方法。

### 不自動列出所有 failure modes

只有與當前 load path、component 或 review scope 有關的 failure modes 才需要出現在答案。

例如使用者只問材料牌號 current standard，不需要順便展開 anchor、weld、seismic、water-management checklist。

### 不每次自動加「下一步」

若使用者已得到完整答案，不必固定附加延伸工作建議。

只有在下列情況才主動提出下一步：

- 目前結論被一個明確 evidence gap 阻擋；
- 有一個低成本檢查能 materially 降低工程風險；
- 使用者正在建立 workflow / KB / calculator，需要 continuity；
- 使用者明確要求建議下一步。

## Evidence 與引用呈現

### Repository 內已足夠

若答案可由 canonical KB 支持：

- 優先引用／路由到 canonical page；
- 不需要為了看起來可靠而搜尋大量二手來源；
- standard current edition / status 優先引用 `references/standards/` owner。

### 需要 current 外部查證

法規、標準版本、產品、manufacturer literature 或其他可能變動資訊若 repository freshness 不足：

- 先查 current primary source；
- 回覆中說明本次 currentness 是外部重新確認，而不是舊 cached value；
- 不用把完整 research process 全部展示，只呈現支持結論的最低充分 evidence。

### 私人 project evidence

在私人聊天中可依使用者提供的計算書、圖面、規範進行分析，但回覆若同時討論 public KB 維護，必須把兩者分開：

- **本次專案判斷**可以引用私人文件；
- **可公開 KB 結論**只保留去識別、可公開驗證的方法論。

不得因回答方便，把 project-specific dimension、load、drawing number 或 private provenance包裝成 repository 通則。

## 用語防呆

除非 scope 真正支持，避免使用過度寬泛語句：

- 「整體安全」
- 「完全沒問題」
- 「符合所有規範」
- 「一定可以」
- 「等同於」

優先改成可追溯 scope：

- 「就目前提供的 member flexure check，可判定 PASS。」
- 「anchor steel check 可確認；concrete edge breakout 尚缺 geometry，因此整體 anchor verification 仍為 INCOMPLETE。」
- 「兩個標準用途相關，但目前 evidence 不支持宣稱 equivalent。」

## 使用者要求簡答時

若使用者明確要求「簡單講」、「只要結論」、「不用展開」：

- 保留結論與會改變結論的 critical caveat；
- 省略背景教學、完整 failure-mode map、research history 與不必要 routing；
- 不因簡短而省略關鍵的不確定性。

## 使用者要求完整審查時

若使用者明確要求「全檢」、「完整 review」、「逐項檢查」：

- 先界定 scope；
- 使用相應 canonical checklist；
- 覆蓋 completeness，不以篇幅短為目標；
- 仍要把 governing findings 放前面；
- missing evidence 不得因「完整回答」而用假設填滿。

## 回覆前最低檢查

形成最終工程答覆前，快速確認：

1. 有沒有直接回答使用者真正問的問題？
2. 結論有沒有超出目前 evidence scope？
3. 是否把事實、推論與 unknown 混在一起？
4. 使用 `PASS / FAIL / INCOMPLETE` 時，scope 是否明確？
5. 是否有偷偷補入 safety factor、allowable、standard equivalence 或其他無 provenance 值？
6. 是否重複同一結論或展開大量不相關 domain？
7. 若 currentness 會影響答案，是否已確認 freshness？
8. 若使用私人專案資料，是否避免把 project-specific evidence 泛化成 public rule？

> 好的工程回覆不是越長越好，而是讓使用者能快速看見「目前可以確認什麼、依據是什麼、還不能確認什麼，以及這個結論的實際 scope」。