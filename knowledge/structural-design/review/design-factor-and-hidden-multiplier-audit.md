---
title: "結構計算 Design Factor／Safety Factor／隱藏倍率稽核"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 結構計算 Design Factor／Safety Factor／隱藏倍率稽核

## 目的

本頁用於審查帷幕牆／建築外殼結構計算中所有會改變 **demand、capacity、allowable、resistance、test demand 或 reported utilization / safety ratio** 的係數。

核心不是判斷「安全係數越大越安全」，而是要求：

> **每一個會改變結果的 factor 都必須具名、具來源、具適用範圍、具運算方向，而且可以從原始 input 一路重建到 final result。**

若計算結果看似 PASS，但中間存在無法追溯的倍率、除數、折減、放大或 ratio 定義，該 PASS 不應視為可靠。

## 為什麼「Safety Factor」這個名稱不夠

同一個數字，例如 `1.5`，可能代表完全不同的工程意義：

- demand amplification
- load combination factor
- proof / test multiplier
- factor of safety applied to nominal capacity
- allowable-stress conversion
- material reduction
- resistance factor 的倒數或其他轉換
- project-specific factor
- warning / management threshold
- purely reported `capacity / demand` safety ratio

因此不得只保存：

```text
SF = 1.5
```

必須知道它**作用在哪一個量、用乘還是除、來源在哪裡，以及最後讓 utilization 增加還是減少**。

## 係數台帳（Factor ledger）

審查一份計算書時，建議先建立完整 factor ledger：

| ID | 名稱／原文標示 | 數值 | Factor type | 作用對象 | Operator | Source | Clause | 對 utilization 的影響 | Status |
|---|---|---:|---|---|---|---|---|---|---|
| F-001 | ... | ... | ... | demand / capacity / allowable / test | × / ÷ / formula | ... | ... | increase / decrease / depends | ... |

任何公式中出現但 ledger 找不到的 factor，至少標為 `WARNING`；若它會影響 PASS / FAIL 且缺少可信來源，應標為 `INCOMPLETE`。

## 建議 factor types

### 1. `load_factor`

用於 governing code / project design basis 定義的 load combination 或 load amplification。

需確認：

- load case
- combination rule
- limit state
- governing standard / project criterion

### 2. `demand_amplification`

直接放大 calculation demand，但不一定等同規範 load factor，例如特殊 eccentricity、dynamic / impact treatment 或 project-defined amplification。

不得只因它「比較保守」就免除來源說明。

### 3. `capacity_safety_factor`

名義 capacity 依指定 factor 轉成 design / allowable capacity 的處理。

必須確認該 factor 是否已經內含在 governing allowable / resistance procedure 中，避免 double counting。

### 4. `resistance_factor`

依 governing resistance design method 使用的 resistance factor / strength reduction treatment。

不得和 ASD-style allowable、manufacturer allowable 或另一套 safety factor 無條件混用。

### 5. `allowable_conversion`

把 nominal / ultimate / proof property 轉成 allowable value 的明示轉換。

若 source 已經直接給 allowable value，就不得再自行重複除一次 safety factor，除非 source / project criterion 明確要求。

### 6. `material_reduction`

例如 weld-affected condition、temperature、duration、environment、product-form 或其他有正式設計依據的 material reduction。

必須和原始 material property 分開保存。

### 7. `test_or_proof_multiplier`

把 design demand 轉成 mock-up / proof / safety test demand 的倍率。

**Test / proof multiplier 不得靜默回灌成 normal design capacity 或 design load factor。**

### 8. `project_specific_factor`

由 project specification、approved clarification 或其他正式 project source 明示的特殊 factor。

Public KB 不保存特定專案數值；project review 時則必須保存 source clause。

### 9. `warning_threshold`

例如 utilization > 0.90 時顯示 WARNING。

這是管理 threshold，不是 structural safety factor，也不得改變 capacity。

### 10. `reported_ratio_definition`

有些計算書把：

```text
utilization = demand / capacity
```

另一些則輸出：

```text
safety ratio = capacity / demand
```

兩者數字方向相反。

因此「Safety Factor 很高」本身不能直接判斷安全性；必須先確認 ratio definition。

## 必做 reconciliation

### A. 需求對帳

應能重建：

`raw load / pressure`

→ `project / code load treatment`

→ `tributary conversion`

→ `combination / amplification`

→ `member / connection demand`

任何不明倍率都要列出。

### B. 承載力對帳

應能重建：

`material / product property`

→ `applicable condition / product form`

→ `code / manufacturer design treatment`

→ `reduction / allowable / resistance`

→ `calculation capacity`

不得只接受計算書最後一格 `Allowable = X`。

### C. 結果對帳

應能重建 final check 的實際定義，例如：

```text
utilization = demand / design_capacity
PASS if utilization <= 1.0
```

或：

```text
reported_safety_ratio = capacity / demand
PASS if reported_safety_ratio >= required_ratio
```

如果計算書的 label、公式與判定方向不一致，至少 `WARNING`；若會改變結論則 `INCOMPLETE / FAIL` 依 governing basis 判斷。

## 常見異常模式

### 1. 無法解釋的倍率

公式中突然出現 `×k` 或 `÷k`，但沒有 standard / project / manufacturer source。

若 factor 影響 governing result：`INCOMPLETE`。

### 2. 重複計入（Double counting）

同一安全處理被套用兩次，例如：

- source 已提供 allowable，再額外除 safety factor；
- factored demand 又被重複放大；
- resistance reduction 已包含在 capacity，又再次套用。

Double counting 可能變得過度保守，也可能因 ratio 定義錯誤反而讓報表看似更安全；都必須釐清。

### 3. 漏掉必要係數

project specification / governing method 要求 factor，但計算書沒有套用。

這通常是 compliance gap；若會改變結果，應重新計算後判定。

### 4. 係數套用側錯誤

factor 的值本身正確，但乘／除在錯的 quantity，例如應放大 demand 卻被用來放大 capacity。

這是高風險錯誤。

### 5. 比值顛倒

把 `capacity / demand` 與 `demand / capacity` 混用，或 label 寫 Safety Factor、實際公式卻是 utilization。

不得用名稱猜公式，必須從算式重建。

### 6. 設計／試驗係數混用

將 structural test / proof multiplier 當成 normal design factor，或反過來用 design utilization 直接推論 test acceptance。

Design 與 test 必須分開。

### 7. 混用設計哲學

把不同 design basis 的 factor 混用，例如 allowable-based procedure、resistance-based procedure、manufacturer allowable 與 project-specific factor 交錯，但沒有 reconciliation。

若無法證明相容性：`INCOMPLETE`。

### 8. 試算表／軟體內隱藏係數

GUI、spreadsheet hidden cell、named range、template constant、macro、post-processing expression 或 solver setting 可能含 factor。

審查時應要求 final result 可由 visible trace 重建；不能只因軟體顯示 PASS 就接受。

### 9. 有利的四捨五入／截斷

若 intermediate value 被非一般 rounding、clamping、minimum / maximum rule 改變，該操作本身也視為 transformation，必須有依據。

### 10. 相似檢核間係數不一致

相同 design basis、相同 component family 或相同 limit state 的 factor 若在不同頁／不同構件無理由改變，應列 `WARNING` 並要求 reconciliation。

## 不要用「結果更保守」作為免審理由

未說明 factor 即使看似增加安全裕度，也可能：

- 造成 design philosophy double counting；
- 隱藏真正採用的 material capacity；
- 讓不同計算頁無法比較；
- 使 test / design criterion 混淆；
- 讓 reported safety ratio 的方向被誤讀；
- 遮蔽另一個 non-conservative assumption。

因此：

> **Conservative-looking ≠ traceable ≠ compliant.**

## AI review 規則

AI 審查計算書時：

1. 搜尋所有顯式倍率、除數、reduction、amplification、allowable conversion、safety ratio。
2. 對每個 factor 建立 ledger item。
3. 追查 factor source、edition、clause、scope、load case、limit state。
4. 判斷 factor 實際作用對象與 operator，而不是只讀 label。
5. 檢查同一 factor 是否 double counted、漏用、套錯側或前後不一致。
6. 將 design factor、test multiplier、warning threshold、reported ratio 分開。
7. 若 factor source 不明但不影響 governing conclusion，可先 `WARNING`。
8. 若 factor source / application 不明且可能改變 PASS / FAIL，必須 `INCOMPLETE`；不得維持原計算書的 PASS。
9. 不應直接指控作者意圖；輸出應描述「無法追溯／不一致／可能改變結果」的客觀證據。

## 建議輸出

```yaml
factor_audit:
  status: INCOMPLETE
  factors:
    - id: F-001
      factor_type: capacity_safety_factor
      value: 1.5
      applied_to: nominal_capacity
      operator: divide
      source_status: MISSING
      effect_on_utilization: increase
      status: INCOMPLETE
      issue: "無法找到 governing source / clause"
```

並另外輸出：

- `original_reported_status`
- `factor_audit_status`
- `recomputed_status_if_possible`

不得因原計算書印有技師簽章或 `PASS / OK` 就跳過 factor audit。

## 機器可讀 routing

搭配：

- `/schemas/design-factor.schema.json`
- `/schemas/project-design-basis.schema.json`
- `/schemas/structural-coverage.schema.json`

## 公開安全規則

本頁保存 generic audit methodology。實際專案的 factor、計算頁碼、技師姓名、公司名稱與 proprietary spreadsheet / calculation content 都屬當次 project context，不應 commit 到 public repository。

> 本方法用於提高 calculation traceability 與 independent review 能力；它不推定計算作者存在故意操弄，也不取代 governing code、project specification 或專業工程判斷。