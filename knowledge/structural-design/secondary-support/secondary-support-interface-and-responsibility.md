---
title: "次結構支撐介面與責任分界（Interface / Responsibility）"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
---

# 次結構支撐介面與責任分界（Interface / Responsibility）

本頁處理 curtain-wall fixing、secondary support、back brace、primary structure 之間的設計責任分界。

## 核心原則

**Engineering scope 必須沿 load path 明確切割。**

不應只用「帷幕廠負責外牆」或「結構技師負責鋼構」這類模糊描述取代實際 responsibility matrix。

## 建議把 interface 畫成圖

例如 Mode A：

`curtain wall`
→ `fixing`
→ `back brace`
→ `brace connection`
→ **DESIGN INTERFACE**
→ `primary beam / slab / column`

Mode B：

`curtain wall calculation`
→ `support reaction`
→ **REACTION HANDOFF INTERFACE**
→ `secondary steel / stiffener / primary member design`

Mode C：

`curtain wall`
→ `back brace member`
→ **INTERFACE 1**
→ `brace-to-beam connection`
→ **INTERFACE 2**
→ `primary beam local reinforcement`

只要 interface 沒畫清楚，就容易形成 scope gap。

## Responsibility matrix 最低欄位

至少釐清：

- façade load basis；
- façade framing analysis；
- fixing reaction；
- back brace / secondary member；
- brace-end connection；
- anchor / weld / bolt；
- primary beam / slab / column capacity；
- local flange / web / torsion；
- stiffener / reinforcement；
- shop drawing / fabrication drawing；
- material procurement；
- installation / welding / bolting；
- inspection / testing；
- revision / change notification；
- final approval / professional sign-off。

## 常見 scope-gap 情況

### 情況 1

帷幕廠提供 reaction，主結構端以為 secondary steel 已包含在帷幕 scope。

結果：secondary member 無人設計。

### 情況 2

帷幕廠設計 brace member，但沒有確認 beam flange / web local effects。

結果：brace PASS，但 receiving member 未檢核。

### 情況 3

主結構技師設計 stiffener，但 reaction revision 更新後未重新通知。

結果：downstream reinforcement 使用過期 demand。

### 情況 4

鋼構包自行改 connection detail 以利加工，但沒有重新確認 eccentricity / movement / load path。

結果：製造可行，但 engineering model 已改變。

## SHOP DWG／現場協調

Secondary-support design 常高度依賴：

- steel beam actual depth / flange width；
- deck profile；
- slab edge；
- beam camber；
- steel bracing；
- MEP；
- fireproofing；
- weld access；
- bolt installation clearance；
- erection sequence。

因此 design package 應定義哪些資訊是：

- design assumption；
- required coordination item；
- final field-verification item。

若 steel SHOP DWG 與 original structural drawing 不一致，不能只以「施工圖為準」取代 engineering re-check。

## 變更管理（Change management）

以下變更可能跨越責任介面：

- façade reaction 增加；
- support spacing 改變；
- reaction location 改變；
- primary beam size 改變；
- brace angle / length 改變；
- stiffener configuration 改變；
- bolt / weld detail 改變；
- movement release 改變。

應有明確的 re-review trigger，而不是各包商各改各的圖。

## 建議 review output

可分開輸出：

- `façade_reaction_generation: PASS`
- `reaction_handoff: PASS`
- `secondary_support_member: NOT_APPLICABLE / PASS / INCOMPLETE`
- `secondary_support_connection: PASS / INCOMPLETE`
- `primary_structure_local_effect: INCOMPLETE / PASS`
- `responsibility_boundary: PASS / INCOMPLETE`

這比一個沒有 scope 的 `STRUCTURE: PASS` 更可靠。

## 不可推論事項

- `對方是結構技師，所以沒寫 responsibility 也沒關係`：錯誤。
- `營造廠要求帷幕廠處理 = 帷幕廠必然承擔 primary structure design`：錯誤，應回 contract / approved scope。
- `反力交出去 = 責任自然完成`：錯誤；至少要確認 handoff receipt、revision 與 downstream scope。
- `SHOP DWG 有畫補強 = 補強已經完成 engineering verification`：錯誤。

> 責任分界的目的不是推卸責任，而是確保 load path 的每一段都有明確設計者、輸入、輸出與 revision owner。