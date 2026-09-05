---
title: "結構計算審查紀錄與追溯"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-05"
canonical_owner: true
---

# 結構計算審查紀錄與追溯

本頁定義 AI／工程師完成 calculation review 後，如何留下**可續接、可稽核、避免事後覆寫的 review record**。它不取代計算方法、project criteria 或 deterministic calculator；其責任是保存「當時看到什麼、算出什麼、怎麼判讀、後來新增什麼證據，以及最後如何收斂」。

核心原則：

> **保留原始 review judgment node；後續證據與 reconciliation 以追加為主，不用 hindsight 改寫第一次判斷。**

## 適用時機

正式 record 特別適合：

- 計算書存在 `MISMATCH`、missing input、hidden multiplier 或 model uncertainty，需要後續追查；
- 同一 calculation package 會跨聊天室、跨 revision 或跨 reviewer 延續；
- 需要保留 reported／recomputed comparison 與 deterministic execution evidence；
- 後續 drawing、specification、calculation revision 或補件可能改變 root-cause judgment；
- 需要回頭確認「當時為什麼提出這個 review comment」。

一次性、沒有後續價值的局部 arithmetic check 不強制建立長期 record。

## 持久化是選配功能

Review record 定義的是 **memory contract**，不是指定唯一的 **memory backend**。一般使用者不需要先理解 GitHub、database 或 storage schema 才能使用本方法；只有當 review 需要跨聊天室、跨 revision、跨 reviewer 延續，或需要可稽核的長期歷史時，才需要啟用持久化。

可依需求分成三層：

- **不持久化**：一次性 review 只存在目前工作階段；AI 不得把 conversational context 宣稱成長期工程紀錄。
- **可攜式紀錄檔**：以 Markdown／JSON 等 artifact 保存，之後由使用者重新提供或放入專案工作區；record schema 仍保持相同。
- **可直接寫入的外部儲存**：若需要可靠續接、長期追溯或團隊協作，優先使用 ChatGPT／AI 能直接讀寫且具有明確 persistence 的外部 backend，例如 private GitHub repository、受控文件庫、資料庫或其他版本化儲存。

對需要長期記憶的一般使用者，**建立一個 AI 可直接寫入的外部持久化位置通常是較可靠的預設**。GitHub 是適合有版本歷史、diff、stable path 與 machine-readable record 需求的選項之一，但不是唯一合法 backend。

AI 不得默認「ChatGPT 自己會記得」即可取代正式 review record。若使用者需要長期續接但目前沒有可用 backend，應先說明這是選配能力，並建議建立一個可直接讀寫的外部持久化位置；在 backend 尚未建立前，可先產生 portable record artifact，不得假裝已完成外部保存。

一旦使用外部 backend，應維持相同 `review_id`、append-first history 與 provenance；storage location 可以改變，但不得因此改寫原始 judgment node。

## 跨聊天室續接與重新載入（Rehydration）

舊聊天室 summary、checkpoint、handoff 或模型 memory 只可作為**尋找既有紀錄的 recovery pointer**，不得升格成 current review authority。Fresh session 若要延續既有 review，應先從可用 persistence backend／project workspace 重新取得 current record，再決定從哪裡續審。

建議重新載入順序：

`review_id / backend → current record → source revision / review contract → latest reconciliation updates → current lifecycle / final judgment → next authorized review action`

一般原則：

- 先確認 `review_id` 與 source revision／package identity，避免把相似計算書、舊 revision 或另一個 judgment node 接錯。
- 重新讀取目前 record 的 source facts、recalculations、engineering interpretations、latest reconciliation 與 final judgment；不要只依舊 summary 重建狀態。
- 若 summary／checkpoint 與 current record、current source revision 或較高權威 project criteria 衝突，以 current canonical evidence 為準；舊 summary 降為 stale recovery context，但原始 review judgment node 仍依 append-first 規則保留。
- Fresh session 不得假定舊聊天室的 backend access、write permission 或 execution capability 自動繼承；需要更新外部 record 時，仍須確認目前 session 具有必要讀寫能力與授權。
- 若 current record 無法取得，明確標示 rehydration incomplete；不得把記憶中的 completion、root cause 或 next action 當成已重新確認。

## 固定紀錄身分與生命週期

正式紀錄應有穩定 `review_id`；後續更新引用同一 ID，不靠檔名或聊天室猜測。

### 審查單元與容器邊界

Calculation package、PDF、資料夾、聊天室、batch 或 aggregate report 都可以是 physical container，但不因此成為其中所有審查問題的單一 semantic identity。

原則上，一個 `review_id` 應代表**一個可獨立形成 engineering judgment、reconciliation lifecycle 與 final disposition 的 review unit**。同一份 calculation package 若同時存在彼此可獨立追查、補件、close 或 supersede 的 discrepancy／review issue，可以建立多個 `review_id`，並各自保留來源與判斷證據鏈。

這不要求現行 schema 預先為每個 child event 增加 ID。只有實際 consumer 需要在同一 `review_id` 內唯一引用多個同型 recomputation／interpretation／update，而且現有 pointer 已不足時，才應依真實使用需求擴充 stable child identity。不得只因事件都放在同一 JSON／Markdown container，就假定 array order、檔名或相近 timestamp 足以取代 semantic identity。

建議 lifecycle：

- `in_review`：正在審查，尚未完成必要核對。
- `waiting_for_input`：已辨識缺口，等待補件／revision／來源。
- `reconciled`：主要 discrepancy 已找到可追溯 root cause。
- `unresolved`：已完成目前可做核對，但 root cause 或必要證據仍不足。
- `superseded`：後續正式 revision 建立新的主要 review record；舊 record 保留。
- `closed`：本次 scope 已形成最終 review judgment。

`lifecycle_status` 不等於工程 acceptance status，也不等於 calculator 的 `calculation_status`／`comparison_status`。

## 六層審查證據

### 第一層：審查契約（Review Contract）

保存結果出現前已固定的 scope：

- review object／package identity（私人工作流程內）；
- source revision／日期；
- review scope、exclusions、completion rule；
- governing project criteria／design basis 的引用；
- 預定使用的 methodology／calculator route。

Contract 若有實質缺陷，不應事後靜默改寫；建立修正版 record 或留下明確 amendment。

### 第二層：來源事實（Source Fact）

只保存來源中實際可見、可定位的內容：

- source document／page／section／revision；
- reported inputs、formula、intermediate value、reported result；
- units、load case、member／connection scope；
- source 中明示的 assumptions。

這一層不得把 AI 推論或重算值冒充成原文件內容。

### 第三層：原始重算（Original Recalculation）

若 `scripts/engineering_calc/review.py` 支援該 check，依 adapter-first contract 保存最低充分 execution evidence：

- `check_type`；
- `calculation_status`；
- `comparison_status`；
- reported／recomputed 關鍵值；
- tolerance；
- relevant `review_flags`；
- calculator／repository commit 或其他足以識別執行版本的 provenance（若可得）。

若 adapter 不支援而採 bounded fallback，必須保存 `ADAPTER_FALLBACK`、原因與 scope。

### 第四層：原始工程判讀（Original Engineering Interpretation）

保存第一次正式 engineering interpretation，例如：

- visible arithmetic discrepancy；
- model／support／unit／factor provenance 尚待確認；
- 局部 `MATCH` 但 coverage 仍 `INCOMPLETE`；
- 當時可支持的 scope-qualified `PASS / WARNING / FAIL / INCOMPLETE / NOT_APPLICABLE`。

這一層不能因後來找到答案而改寫成「一開始就知道 root cause」。

### 第五層：調和更新（Reconciliation Update）

後續取得的新 evidence 以 dated append 追加，例如：

- 找到先前未顯示的 multiplier／load source；
- 補到 drawing／specification／calculation revision；
- 確認單位或 transcription error；
- 發現原先抽取值錯誤並留下 correction provenance；
- 新 adapter execution 改變 comparison result。

每次更新應區分 `new_evidence`、`recomputation` 與 `interpretation_change`，避免把三者混成一句結論。

### 第六層：最終審查判斷（Final Review Judgment）

本次 scope 收斂後，保存：

- root cause：`confirmed / probable / unresolved / not_applicable`；
- 最終 scope-qualified engineering status；
- 尚未解決的缺口；
- disposition／需要的下一步；
- 若由新 revision 取代，指向 successor record。

Final judgment 不刪除前面曾經出現的 `MISMATCH`、錯誤抽取或 provisional interpretation。

## 證據來源精度（Provenance Precision）

Review record 應保存**實際證據能證明的 precision**；schema 欄位存在、格式完整或某一 provenance field 已知，不代表其他 provenance 也已驗證。

- `repository_commit` 已知，只能證明 calculator／repository version 可被識別；不自動代表 Python version、OS、raw adapter input、environment 或其他 execution metadata 已知。
- Source 只提供 date、minute-level timestamp、revision 或 page locator 時，只保存該 precision；不得把後來取得或模型推測的細節回填成「當時已知」。
- Schema 若要求 machine timestamp，應清楚區分「record／execution event 建立時間」與「source evidence 實際發生時間」；不得用前者冒充後者的精度。
- `MATCH`、`MISMATCH`、`PASS` 或其他 status 只證明它實際涵蓋的 comparison／engineering scope；不能因 status 欄位完整就推導未記錄的 runtime、source 或 acceptance evidence。
- `unknown / unavailable / unverified` 應維持未知邊界；schema completeness 不得被誤認為 evidence completeness。後續取得更高精度 provenance 時，以追加／reconciliation 方式升級，不改寫歷史認知狀態。

## 狀態必須分維度

不得把不同責任的 status 壓成單一 `PASS / FAIL`：

```text
lifecycle_status: waiting_for_input
calculation_status: COMPUTED
comparison_status: MISMATCH
engineering_status: INCOMPLETE
root_cause_status: unresolved
```

`MISMATCH` 只代表 reported 與 recomputed 在指定 tolerance 下不一致；它不是整份計算書或構件自動 `FAIL`。同理，局部 `MATCH` 也不是整體 engineering `PASS`。

## 追加優先與更正規則

正式 review record 原則上 append-only：

- 新 evidence → 追加 reconciliation update；
- 新 deterministic run → 追加 execution event；
- 新 engineering interpretation → 追加 interpretation change；
- final disposition → 追加 final judgment。

明確 typo、轉錄錯誤或 metadata 錯誤可以修正，但應保留最小 correction note。若原始 source extraction 本身錯誤，應保留「原抽取值 → 更正值 → 更正依據」，不要讓 audit trail 消失。

## 公開儲存庫邊界

本頁與 `/schemas/calculation-review-record.schema.json` 只定義**通用方法與資料模型**。Project-specific review record 通常包含文件名稱、revision、頁碼、構件、荷載、reported result、review comment 或其他非公開資訊，應保存在 public repository 之外。

若使用 GitHub 作為持久化 backend，私人專案紀錄應放在 private repository 或其他適當受控範圍，不應因為 public KB 提供 schema 就把實際 project record 寫回本公開知識庫。

Public KB 不得保存真實私人計算書的 record instance。若要建立範例，只能使用明確 synthetic／公開安全資料，且不得讓範例可反推出私人專案。

## 人工智慧使用原則

AI 若要建立或更新正式 review record：

1. 先辨識既有 `review_id`，避免同一 judgment node 重複建檔；
2. 先確認 review unit granularity；不要把同一 physical package 中可獨立 reconciliation 的多個問題因共用 container 而壓成一個 judgment identity；
3. 新資料先判斷屬於 source fact、recomputation、engineering interpretation 或 reconciliation；
4. calculator 支援時遵守 adapter-first execution contract；
5. 不用後來 evidence 覆寫 original interpretation；
6. 回答與 record 都分離 execution/comparison status、engineering status 與 lifecycle status；
7. provenance 只保存當下可證明的 precision；不得因 schema 欄位存在而補猜未知 metadata；
8. 若 evidence 不足，保留 `INCOMPLETE`／`unresolved`，不得補猜 root cause；
9. Fresh session 續接正式 review 時，先由 current record rehydrate，不依舊 summary／memory 直接延續；
10. 只有使用者需要長期續接時才啟用 persistence；若已選定可寫入 backend，優先把正式 record 寫入該 backend，而不是只留在聊天內容中。

對應 machine-readable interchange contract：[`/schemas/calculation-review-record.schema.json`](../../../schemas/calculation-review-record.schema.json)。

> 原則：**Python 決定可重現的 numeric result；工程方法決定 engineering meaning；review record 保存兩者在時間上的證據鏈。**
