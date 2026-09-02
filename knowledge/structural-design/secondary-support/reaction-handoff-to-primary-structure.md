---
title: "帷幕反力交接主結構（Reaction Handoff to Primary Structure）"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
---

# 帷幕反力交接主結構（Reaction Handoff to Primary Structure）

本頁定義帷幕廠只負責 façade reaction generation，而由主結構技師／結構顧問處理梁、樓板、補強材、stiffener 或其他 primary / secondary structural response 時，reaction handoff package 的最低工程要求。

## 核心原則

**Reaction handoff 是工程介面，不是單一數字。**

下游設計者必須能從 handoff package 重建：

- 力的大小；
- 力的方向；
- 力作用在哪裡；
- 相鄰作用點如何重複；
- 是否有偏心／力矩；
- 這個反力來自哪個 load case / calculation / revision；
- 哪一側負責 reaction 之前與之後的設計。

## 最低必要欄位

### 反力識別

- reaction ID / support ID；
- floor / zone / grid / façade line（專案內部使用）；
- drawing location / detail reference；
- support type。

Public KB 不保存 project-specific ID 實例，但 private handoff package 應具備唯一識別。

### 座標與方向

至少定義：

- global / local coordinate system；
- `+X / +Y / +Z` 方向；
- façade outward / inward convention；
- vertical direction；
- moment positive convention if moments are supplied。

只寫「水平反力」而沒有方向定義，通常不足以支援 downstream analysis。

### 反力分量

視介面需要提供：

- `Fx / Fy / Fz`；
- `Mx / My / Mz`；

或等效、明確定義的 directional reaction。

若僅提供單一 `Rw`，必須說明：

- `Rw` 對應哪個方向；
- 是否為正／負風 envelope；
- 是否已含偏心效果；
- 是否為 support reaction、anchor reaction、brace axial force 或其他 quantity。

## 作用位置與偏心

Reaction 的作用點和 primary-structure reference line 之間若存在偏心，應保存：

- `ex / ey / ez`；
- façade centerline / mullion centerline；
- beam web / flange / slab edge reference；
- stand-off distance；
- bracket / secondary-support geometry where relevant。

如果 downstream engineer 只收到 force 而沒收到 eccentricity，可能漏掉：

- torsion；
- flange local bending；
- secondary moment；
- connection prying；
- local stiffener demand。

## 間距與 tributary 定義

Handoff 圖常使用 `@ spacing` 表示重複 reaction。

必須說清楚這個 spacing 是：

- actual fixing spacing；
- repeated reaction spacing；
- tributary width；
- maximum design spacing；
- representative module spacing；

哪一種。

`Rw = XX kN @ YY mm` 若沒有上述定義，不足以直接建立主結構模型。

## 荷載案例／組合（Load case／combination）

每個 reaction 至少應對應到：

- load case name；
- wind positive / negative；
- dead load；
- seismic；
- maintenance / special load where applicable；
- service / allowable / factored / ultimate level；
- governing combination；
- factor provenance。

不得把不同 design level 的 reaction 混在同一張圖而沒有標示。

## 反力來源核對（Reaction source reconciliation）

Handoff reaction 必須能回到 upstream calculation：

`design input`
→ `tributary load`
→ `structural model`
→ `support reaction`
→ `handoff value`

至少保存：

- source calculation file / calculation ID；
- source revision；
- source drawing revision；
- calculation reaction；
- issued handoff reaction；
- difference / rounding / envelope explanation if values differ。

### 允許的差異

例如：

- transparent rounding；
- documented conservative envelope；
- project-approved minimum design reaction；

可以存在，但必須留下 provenance。

### 不允許的差異

若 handoff value 相對 calculation value 被任意放大／縮小而無 explanation，不應視為可追溯 reaction。

依 [`../review/design-factor-and-hidden-multiplier-audit.md`](../review/design-factor-and-hidden-multiplier-audit.md) 檢查。

## 責任交接（Responsibility handoff）

Reaction package 應明確說明至少下列責任：

### 帷幕端通常負責

- façade load basis within its scope；
- mullion / transom / façade-frame analysis；
- support reaction generation；
- reaction location / direction；
- interface geometry necessary to apply the reaction；
- revision notification when reaction changes。

### 主結構端通常負責（若 contract 如此分工）

- primary beam / slab / column capacity；
- beam torsion；
- flange / web local effects；
- stiffener；
- secondary steel added by primary-structure design；
- reinforcement of primary structure；
- structure-side connection design within assigned scope。

實際責任仍應以 contract / design responsibility matrix / approved RFI 為準。

## 版次控制（Revision control）

若以下任一項改變，應評估是否需要重新發 reaction package：

- wind pressure；
- mullion span / support；
- fixing spacing；
- façade geometry；
- member continuity；
- panel tributary width；
- bracket eccentricity；
- movement restraint；
- material / stiffness change；
- structural model assumption。

不能只更新 curtain-wall drawing，而讓舊 reaction package 繼續被 downstream engineer 使用。

## 建議 handoff 表格

Private project package 可使用類似欄位：

| Reaction ID | Location | Direction | Load case | Magnitude | Spacing | Eccentricity | Design level | Source calc rev | Drawing rev |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |

必要時再加 `Mx / My / Mz`、movement release、notes、governing combination 等欄位。

## 審查狀態（Review status）

### 通過（`PASS`）

只有 reaction magnitude、direction、location、spacing、load case、source revision 與 responsibility boundary 都能追溯時，才能給 `reaction_handoff_completeness: PASS`。

### 警告（`WARNING`）

例如 reaction 已完整，但 downstream geometry 尚待主結構端 final coordination。

### 不完整（`INCOMPLETE`）

例如：

- 只提供 reaction magnitude；
- 未定義方向；
- 未定義 spacing 含義；
- 未提供作用位置／偏心；
- 無法回到 calculation revision；
- load level 不明；
- responsibility boundary 不明。

## 核心防呆

- `Façade reaction PASS ≠ primary structure PASS`。
- `Reaction drawing issued ≠ downstream reinforcement designed`。
- `大一點比較安全的 reaction ≠ 不需要 provenance`。
- `support reaction = total load / number of supports` 不得無條件成立。

> 本頁定義 reaction handoff 的資料與責任完整性，不取代主結構技師對 receiving structure 的設計。