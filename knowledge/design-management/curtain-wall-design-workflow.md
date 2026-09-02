---
title: "帷幕牆設計作業流程（Curtain-Wall Design Workflow）"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
---

# 帷幕牆設計作業流程（Curtain-Wall Design Workflow）

本頁整理帷幕牆工程從專案啟動到設計 release / fabrication 前的通用工程流程。它是 process methodology，不是法規或契約條款；實際專案應以 contract、project specification、approved procedure、design responsibility matrix 與 project schedule 為準。

## 核心原則

帷幕牆設計不是「先畫圖，再算結構」。

較可靠的 workflow 是：

`收集 project inputs`
→ `建立 design basis / responsibility / scope`
→ `system / typical detail development`
→ `跨部門 manufacturability / installation / cost review`
→ `structural / performance verification`
→ `mock-up / prototype planning`
→ `material / hardware approval`
→ `shop / fabrication drawing development`
→ `final design verification`
→ `release to procurement / factory / site`
→ `revision control / feedback`

任何重要變更都應能回到 design basis 重新檢查，而不是只修改圖面。

## Phase 0 — 收集專案輸入

正式開始設計前，至少確認可取得的：

- contract / scope / responsibility matrix；
- project specification / performance criteria；
- architectural drawings；
- structural drawings / concrete / steel interface；
- wind / seismic design basis；
- adjacent-trade drawings；
- MEP interface where relevant；
- material / finish / hardware requirements；
- approved sample / mock-up requirements；
- schedule / procurement constraints；
- existing calculations / reports；
- prior approved details only as reference, not automatic design authority。

缺少會影響系統或責任界面的文件時，應先記錄 `INCOMPLETE / RFI required`，不要默默沿用前案。

## Phase 1 — 建立 Project Design Basis

應把 specification 與 governing references 轉成可檢核的 project-specific basis：

- loads / actions；
- strength criteria；
- serviceability criteria；
- movement / tolerance criteria；
- performance-test requirements；
- materials / finishes；
- corrosion / durability；
- fire / thermal / acoustic requirements；
- design responsibility / delegated design boundary；
- submittal / approval requirements。

Routing：[`../structural-design/review/project-specification-extraction.md`](../structural-design/review/project-specification-extraction.md)。

## Phase 2 — 系統／標準部設計

先建立代表性 typical / system details，再大量展開施工圖。

至少處理：

- system type；
- mullion / transom / panel module；
- glass / infill support；
- stack / splice / expansion joints；
- anchor / bracket concept；
- water-management / drainage；
- air barrier / sealant / gasket strategy；
- fire / thermal interface；
- perimeter / roof / sill / corner / termination；
- operable element interface。

System detail 尚未穩定前，過早大量展開 shop drawing 會提高後續 revision cost。

## Phase 3 — 跨部門設計審查

System design 應至少接受下列視角的 review：

- structural engineering；
- fabrication / machining；
- assembly；
- surface treatment；
- transportation；
- erection / installation；
- waterproofing / sealant；
- procurement / lead time；
- cost / contractual scope；
- quality inspection。

目的不是讓所有部門「簽名」，而是提早發現：

- 無法加工；
- 無法組裝；
- 無法安裝；
- tolerance 不可吸收；
- tool access 不足；
- sealant 無施工空間；
- fastener 無法鎖固／檢查；
- incompatible material / finish；
- excessive part count / field work；
- project scope gap。

## Phase 4 — 結構與性能驗證

結構 calculation 應與 drawing geometry 同步，而不是獨立存在。

至少確認：

- design loads / combinations；
- framing；
- glass / infill；
- anchors / brackets；
- fasteners / welds；
- local extrusion；
- operable hardware；
- seismic movement；
- water / air / thermal / fire interface；
- required performance test。

Calculation review routing：[`../structural-design/review/README.md`](../structural-design/review/README.md)。

水管理 routing：[`../water-management/README.md`](../water-management/README.md)。

## Phase 5 — Mock-up／Prototype 規劃

若專案要求 laboratory mock-up / performance test，應盡早選定代表性 specimen，而不是設計全部完成後才臨時拼試體。

選擇時可考慮：

- representative large module；
- high-risk joint；
- operable element；
- corner / transition；
- stack joint；
- perimeter interface；
- atypical anchor / bracket；
- difficult drainage detail。

Mock-up 的價值不只在「取得 PASS」；失敗與拆解 observation 應回饋到 production design。

Performance-test routing：[`../performance-testing/curtain-wall-performance-crosswalk.md`](../performance-testing/curtain-wall-performance-crosswalk.md)。

## Phase 6 — 材料／樣品／五金核准

在大量採購或加工前，至少追蹤：

- exact material / alloy / temper / grade；
- finish / colour / coating；
- glass make-up；
- sealant / gasket；
- fastener / anchor；
- hardware；
- insulation / fire material；
- compatibility / adhesion / corrosion requirements；
- approved sample / mock-up reference；
- current revision。

「等級相近」或「廠商說可以」不等於 approved substitution。

## Phase 7 — Shop／Fabrication Drawing 製作

Fabrication drawing 是 design intent 轉成工廠可製造資料的工程介面。

可能包括：

- unit assembly drawing；
- part drawing；
- extrusion / die drawing；
- anchor / bracket drawing；
- machining drawing；
- glass / panel schedule；
- numbering / mark；
- BOM / quantity list；
- jig / fixture reference where relevant。

Shop / fabrication drawing 應能回到 approved design drawing、design basis 與 revision source。

## Phase 8 — 最終設計確認（Final Design Verification）

Release 前不應只做 drawing drafting check；至少再確認：

- approved revision 是否一致；
- calculation geometry 是否與 drawing 一致；
- material / hardware 是否與 approval 一致；
- interface 是否已協調；
- tolerance / movement 是否仍成立；
- water-management path 是否因細部修改被破壞；
- machining / assembly 是否符合 system intent；
- unresolved RFI / NCR / comment 是否已關閉。

## Phase 9 — Release 與 Revision Control

發行後應保存：

- revision；
- issue purpose；
- affected drawings / calculations / schedules；
- change reason；
- approval status；
- downstream recipients；
- procurement / fabrication impact；
- site change impact。

重要設計變更若影響 geometry、material、load path、seal / drainage、movement 或 performance，應重新觸發相應 engineering review。

## 不可推論事項

- `過去成功 detail = 本案可直接使用`：錯誤。
- `shop drawing approved = engineering calculation automatically correct`：錯誤。
- `calculation PASS = fabrication / installation feasible`：錯誤。
- `mock-up PASS = production workmanship automatically identical`：錯誤。
- `材料已採購 = 可以略過 substitution review`：錯誤。

## 公開來源 routing

- [`../../references/government/abri-metal-curtain-wall-design-manual-2003.md`](../../references/government/abri-metal-curtain-wall-design-manual-2003.md) — 台灣帷幕牆 coverage / performance / mock-up / fixed-attachment historical public technical source。
- 本頁另外整合一般 façade engineering process practice；因此 verification status 為 `HIGH_CONFIDENCE`，不宣稱為法規程序。

> 好的帷幕牆 workflow 不是線性「畫完就交」，而是有明確 design basis、跨部門 review、verification、approval、manufacturing feedback 與 revision loop 的受控流程。