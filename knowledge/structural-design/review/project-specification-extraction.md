---
title: "專案規範 → 結構設計基準抽取"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 專案規範 → 結構設計基準抽取

## 目的

在審查帷幕牆結構計算書之前，先把 project specification、performance specification、approved design criteria 與相關正式文件抽取成一份可追溯的 **Project Design Basis Sheet**。

這一層回答的是：

> 這個專案要求「算什麼、用什麼條件、用什麼判定標準、需要提出哪些證據」？

而不是先回答：

> 技師的公式算得對不對？

完整 review workflow：

`project specification / approved criteria`

→ `Project Design Basis Sheet`

→ `drawings / actual geometry / material data`

→ `engineer's structural calculation`

→ `KB methodology / failure-mode review`

→ `spec-to-calc compliance + engineering review`

## Extraction 與 Verification 必須分開

### Phase A — 原文抽取

先忠實保存文件實際要求：

- 原始 criterion
- 原始單位
- 原始 standard / edition wording
- clause / page / revision
- component scope
- load case / direction
- acceptance wording

這一步**不得因 AI 認為規範過時、數值奇怪或另有更常見做法而自行修改**。

### Phase B — 權威性／現行性驗證

再另外判斷：

- 是否與現行法規衝突
- 引用 standard 是否仍 current
- project specification 是否有 addendum / clarification / approved substitution
- 不同文件間是否有 precedence rule
- criterion 是否為 project-specific requirement

因此資料模型應同時保存：

`specified_value`

與

`verification_status`

而不是在抽取階段直接覆寫原文要求。

## 必抽取的十個 domains

### 1. Document control / authority

至少保存：

- document type
- revision / issue date
- clause / page
- contract / specification / addendum / RFI / approved clarification 等角色
- document precedence rule（若有）
- governing jurisdiction

若不同文件衝突，不得自行合併；建立 `CONFLICT` item。

## 2. Design responsibility / required scope

抽取：

- façade contractor / engineer 的設計責任
- 是否要求 licensed structural engineer certification
- 是否要求 glass analysis / FEA / 3D analysis
- 是否要求 calculation 與 shop drawing 相互配合
- required structural-calculation coverage

Required coverage 應轉成後續 checklist targets，而不是只保留一段 prose。

## 3. Governing references

逐項抽取：

- law / regulation
- CNS
- ASTM
- AAMA / FGIA
- Aluminum Association
- AISC / ACI / AWS
- manufacturer design procedure
- other project-specified references

每一項至少保存：

`standard_id + edition_if_stated + source_clause + applicability`

若 specification 說「latest edition」，也要原樣保存，不要在 extraction 階段自行填一個版本。

## 4. Loads / actions

至少依適用性尋找：

- positive / negative wind pressure
- wind-tunnel source / zone map / external attachment
- corner / multi-surface load cases
- dead load
- seismic component force
- inter-story displacement
- thermal movement
- concentrated load
- maintenance / BMU / façade-access load
- operable-element load
- impact / special attachment load
- other project-specific load cases

每一個 load criterion 必須保存：

- source
- magnitude / referenced source
- unit
- direction
- component scope
- load-case combination rule
- whether it is `design`, `serviceability`, `test`, or `safety / proof` demand

### Design pressure ≠ test pressure

即使數值彼此相關，也必須保存成不同 requirement objects。

## 5. Strength / safety criteria

抽取：

- allowable / resistance basis
- safety / proof / ultimate multiplier
- permanent-deformation prohibition
- stress interaction requirement
- special restrictions for anchors / fasteners / concrete interfaces
- material-specific strength criteria

不得把不同 component 的 factor 合併成一個 project-wide `safety_factor`。

## 6. Serviceability / movement criteria

按 component + direction 分開保存：

- mullion deflection
- transom wind-direction deflection
- transom dead-load deflection
- metal panel deflection
- glass deflection
- skylight criteria
- stone-support criteria
- interior-finish compatibility
- glass bite / edge engagement
- sealant / joint movement
- inter-story drift / seismic movement
- adjacent-component clearance

例如 `L/n`、absolute limit、`min(L/n, X)`、`L/n + C` 應保留原 criterion type，不要先轉成單一數字。

## 7. Required calculation coverage

把 specification 中的「計算書須包含」轉成 machine-reviewable checklist，例如：

- mullions / vertical framing
- transoms / horizontal framing
- member stability / lateral buckling
- local bending
- screw boss / local extrusion
- fastener / connection groups
- brackets / stiffeners
- anchors / embed plates / load transfer to primary structure
- glass stress / deflection
- structural silicone
- metal panel / backpan / stiffener
- FEA and boundary conditions
- operable-window hardware
- special attachments

任何 specification 明確要求但 calculation package 找不到對應 evidence 的項目，至少應標為 `INCOMPLETE`。

## 8. Required calculation trace / submittal evidence

尋找：

- free-body diagram
- force location
- eccentricity
- reactions
- section-property source / die drawing
- material properties
- formula / standard basis
- safety factor
- drawing reference
- revision / date / page index
- calculation-to-shop-drawing coordination
- manufacturer review / certificate
- test report

若 specification 要求 FBD / eccentricity / reactions，而計算書只列最後 utilization，屬 specification-compliance gap。

## 9. Performance test / acceptance

分開抽取：

- test sequence
- design-pressure structural test
- safety / proof pressure test
- positive / negative sequence
- air / static water / dynamic water
- displacement / seismic movement
- operable-element cycling
- BMU / concentrated-load test
- anchor field test
- weld inspection / NDT
- acceptance after test

**Test requirement 不是 calculation criterion 的替代品。**

應另外記錄 specification 是否要求：

`analysis result ↔ mock-up / test result correlation`

## 10. Material / connection-specific requirements

抽取：

- aluminum alloy / temper / property source
- steel / stainless grade
- fastener material / property class
- AAMA TIR-A9 or other fastener basis
- weld standard / weld type / inspection
- anchor type / prohibited anchor type
- structural silicone basis
- corrosion / isolation requirement when it affects connection design

不要把 material requirement 與 structural capacity value 混成同一欄位。

# Project Design Basis Sheet

推薦至少輸出以下 table：

| ID | Domain | Requirement | Scope | Load case | Specified value / rule | Source | Verification | Conflict |
|---|---|---|---|---|---|---|---|---|
| DB-001 | wind | design pressure source | façade zone | positive | referenced report | §... | VERIFIED / PENDING | — |
| DB-002 | deflection | mullion limit | primary mullion | wind | criterion | §... | SPECIFIED | — |
| DB-003 | connection | required analysis | anchor | all applicable | stress + deflection + reaction | §... | SPECIFIED | — |

實際 project sheet 屬 project context，不應 commit 到 public repository。

## Spec → Calc Coverage Matrix

取得 Design Basis Sheet 後，再建立：

| Requirement ID | Calculation evidence | Status | Comment |
|---|---|---|---|
| DB-... | calc p./section ... | PASS / WARNING / FAIL / INCOMPLETE | ... |

Status 必須區分至少兩種問題：

### Engineering result

例如：

`member_flexure = PASS`

### Specification compliance

例如：

`project_deflection_criterion = FAIL`

不能因公式 mechanics 正確，就把不符合 project criterion 的結果判為 PASS。

# Conflict handling

文件彼此不一致時：

1. 保存每一條 requirement 的原始來源。
2. 尋找 specification 中明示的 precedence / stricter-rule clause。
3. 判斷兩條 requirement 是否真的在相同 scope / load case / limit state 下可比較。
4. 若無法確認 governing requirement，標 `CONFLICTING_EVIDENCE` / `INCOMPLETE`。
5. 不得由 AI 靜默選擇較方便、較常見或數值較大的 criterion。

「採較嚴格者」只有在 governing documents 明確要求且兩個 criterion 可直接比較時才能直接執行。

# Recommended extraction statuses

- `SPECIFIED` — 文件明確寫出。
- `REFERENCED_EXTERNAL` — specification 指向外部報告／圖表／其他文件，尚需取得。
- `VERIFIED_CURRENT` — 已另行確認 current governing source。
- `PROJECT_APPROVED` — 有 approved project clarification / substitution / revision。
- `INCOMPLETE` — 必要資料缺少。
- `CONFLICTING_EVIDENCE` — 不同 project sources 尚未解決。
- `NOT_APPLICABLE` — 有明確理由判定不適用。

# AI 防呆

AI 不得：

- 在 extraction 階段把舊版 standard 名稱自動改成最新版。
- 把「latest edition」自行翻譯成某個具體年份而不查證。
- 把 design pressure、test pressure、proof pressure 合併。
- 把所有 safety factor 合併成 project-wide constant。
- 把 mullion / transom / glass / panel 的 deflection criteria 混用。
- 看到 specification 說「所有 connections」卻只查 fastener body。
- 把 required calculation scope 找不到的項目當作 `NOT_APPLICABLE`。
- 因為技師已簽證就跳過 independent completeness review。
- 將 project-specific extraction 結果寫回 public knowledge base。

# Machine-readable routing

推薦搭配 repository 根目錄：

`schemas/project-design-basis.schema.json`

並與：

- `schemas/structural-coverage.schema.json`
- `schemas/load-case.schema.json`
- `schemas/deflection-criterion.schema.json`
- `schemas/seismic-component.schema.json`

共同使用。

> 本頁定義的是 project specification extraction / review workflow；不保存任何特定專案的 specification、criterion、load、drawing 或 confidential provenance。