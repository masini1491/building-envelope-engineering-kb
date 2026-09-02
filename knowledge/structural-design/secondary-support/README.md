---
title: "帷幕牆次結構支撐與反力交接（Secondary Support / Reaction Handoff）"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 帷幕牆次結構支撐與反力交接（Secondary Support / Reaction Handoff）

本目錄處理帷幕牆固定件與主結構之間的 **secondary support / back bracing / reaction handoff**。

核心問題不是「背撐角鋼要多大」，而是先確認：

> façade reaction 由誰算？secondary support 由誰設計？primary structure local effect 由誰負責？設計責任在哪一個介面切開？

## 三種常見責任模式

### 模式 A — 帷幕廠負責次結構支撐設計

典型 load path：

`curtain wall`
→ `façade fixing`
→ `back brace / secondary steel`
→ `brace connection`
→ `primary-structure interface`

帷幕設計端除提供 façade reaction 外，也負責 scope 內的：

- back brace / secondary member；
- member stability；
- end connections；
- weld / bolt / anchor；
- local plate / bracket checks；
- movement compatibility。

但 primary beam / slab / column 本體是否可接受該 concentrated / eccentric demand，仍應依專案責任矩陣確認是否由主結構技師 review / design。

詳見 [`curtain-wall-back-bracing.md`](curtain-wall-back-bracing.md)。

### 模式 B — 帷幕廠只提供反力

典型責任切點：

`curtain wall calculation`
→ `façade fixing reaction`
→ **reaction handoff interface**
→ `primary-structure engineer`
→ `secondary steel / stiffener / beam / slab reinforcement`

此模式下，帷幕端的核心 deliverable 是**可重建、可追溯的 reaction package**，不是替主結構技師決定補強形式。

詳見 [`reaction-handoff-to-primary-structure.md`](reaction-handoff-to-primary-structure.md)。

### 模式 C — 分割式次結構設計

例如：

- 帷幕廠設計 back brace 本體；
- 主結構技師設計 beam flange / web stiffener；
- 鋼構包製作 secondary steel；
- 營造／顧問負責介面 approval。

這種模式最容易形成 scope gap，必須明確畫出 design interface 並逐項分配責任。

詳見 [`secondary-support-interface-and-responsibility.md`](secondary-support-interface-and-responsibility.md)。

## 核心 load path

無論採哪一種責任模式，至少應能追溯：

`wind / dead / seismic / movement input`
→ `façade framing response`
→ `façade support reaction`
→ `reaction location / eccentricity`
→ `secondary support or handoff`
→ `primary structural member`
→ `global / local primary-structure response`

不得在責任切點把 load path 變成只有一個無方向、無位置的數字。

## 支承主構件的局部效應

即使 back brace 或 reaction 本身已確認，主結構端仍可能受：

- beam torsion；
- flange local bending；
- web local yielding / crippling / buckling；
- concentrated load introduction；
- local plate bending；
- stiffener demand；
- connection eccentricity；
- slab / edge / anchor local effects。

這些項目見 [`supporting-steel-local-effects.md`](supporting-steel-local-effects.md)。

## Review 狀態規則

### 通過（`PASS`）

只能對**明確 scope**給 PASS，例如：

- `façade_reaction_generation: PASS`
- `back_brace_member: PASS`
- `brace_end_connection: PASS`
- `reaction_handoff_completeness: PASS`

不能因其中一項 PASS 就寫 `secondary_support_system: PASS`，除非整個責任範圍與下游介面都已完成。

### 不完整（`INCOMPLETE`）

若以下任一事項不明，應優先回傳 `INCOMPLETE`：

- design responsibility boundary；
- reaction direction / sign convention；
- reaction location；
- reaction spacing / tributary meaning；
- eccentricity；
- load case / combination；
- source calculation / revision；
- secondary-support geometry；
- primary-structure receiving point。

## 相關 routing

- [`../connections/load-path-and-anchor-reactions.md`](../connections/load-path-and-anchor-reactions.md)
- [`../connections/fastener-group-analysis.md`](../connections/fastener-group-analysis.md)
- [`../connections/weld-group-analysis.md`](../connections/weld-group-analysis.md)
- [`../../anchors/README.md`](../../anchors/README.md)
- [`../seismic/seismic-movement-compatibility.md`](../seismic/seismic-movement-compatibility.md)
- [`../review/design-factor-and-hidden-multiplier-audit.md`](../review/design-factor-and-hidden-multiplier-audit.md)

> 本目錄只定義次結構支撐與 reaction handoff 的通用工程方法，不保存任何私人專案的樓層、反力、圖號、構件尺寸、TYPE 編號或責任人名稱。