---
title: "排水與 Weep 設計（Drainage / Weep Design）"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
---

# 排水與 Weep 設計（Drainage / Weep Design）

良好的 curtain-wall water-management system 通常不假設外層永遠完全不進水，而是讓少量進入 cavity 的水能被收集、導引並排回室外。

## 排水路徑要完整

至少應能回答：

1. 水最可能從哪裡進入？
2. 第一個 collection cavity 在哪裡？
3. cavity 底部是否有明確低點？
4. 水從低點如何到 outlet？
5. outlet 是否真正連到 exterior？
6. 排水過程會不會跨越 inner air / water barrier？
7. 上層排出的水會不會灌入下層 vulnerable joint？

不能只在圖面畫一個 `weep hole` 就視為 drainage path 已成立。

## 幾何原則

Review 至少包括：

- slope direction；
- end dam / stop end；
- cavity continuity；
- low point；
- outlet elevation；
- outlet direction；
- baffle / labyrinth；
- capillary break；
- sealant / gasket termination；
- joint overlap；
- water path at corner / splice / stack joint。

## 排水孔／出口（Weep / outlet）防呆

Weep 可能因：

- sealant overflow；
- gasket displacement；
- setting block；
- debris；
- insect screen / mesh；
- field tape；
- coating / paint；
- machining burr；

而部分或完全堵塞。

因此設計與 inspection 應考慮：

- 可施工性；
- 可目視確認性；
- redundancy；
- outlet 被堵後的 secondary path；
- field-cleaning / maintenance access（若適用）。

## 垂直排水與分艙（Vertical drainage / compartment）

水可以沿 mullion / cavity 向下，但不能不加控制地跨越所有樓層與 pressure compartments。

應明確定義：

- 哪些 cavity 允許 vertical drainage；
- 哪裡必須 terminate / collect / discharge；
- stack joint 是否把上層水帶入下層；
- transom / sill 是否具有 end dam；
- curtain-wall-to-adjacent-construction interface 如何收水。

## 水頭（Water head）

任何需要以 water head / hydrostatic pressure 判斷 outlet elevation 或 dam height 的設計，都必須以本次 project pressure、geometry 與 governing method建立。

不得把歷史教材中的固定高度或特定 test-pressure 換算值當作 universal minimum。

設計資料應至少保存：

- differential pressure；
- assumed water level / head；
- outlet / dam elevation；
- governing load / test condition；
- safety / freeboard treatment（若使用）；
- source / provenance。

## 框架式帷幕牆（Stick curtain wall）

常見 review point：

- glazing pocket drainage；
- transom end seal；
- mullion/transom intersection；
- pressure plate / cap system；
- vertical mullion cavity；
- sill / starter condition；
- field splice；
- perimeter seal interface。

## 單元式帷幕牆（Unitized curtain wall）

常見 review point：

- stack joint；
- male / female mullion cavity；
- horizontal stack drainage；
- corner unit；
- unit-to-unit gasket continuity；
- setting / erection damage；
- floor-to-floor compartment behaviour；
- sill / head transition。

## 金屬面板／雨幕（Metal panel / rainscreen）

若為 open-joint metal cladding，還須區分：

- exterior cladding joint；
- rainscreen cavity；
- secondary water-resistive / air barrier；
- flashing；
- cavity base drainage；
- ventilation opening。

這和 glazed curtain-wall glazing pocket 的 drainage mechanics 不一定相同。

## 試體／Mock-up／現場審查

水管理 detail 很適合在封板前檢查：

- end dam continuity；
- weep openness；
- air-seal continuity；
- splice seal；
- cavity segmentation；
- actual slope；
- field-applied sealant overflow。

如果 performance test 失敗，修正應先找 mechanism / path；不要只在漏水表面追加 sealant，而沒有確認是否破壞原本 drainage / pressure-equalization intent。

## 相關頁面

- [`water-ingress-mechanisms.md`](water-ingress-mechanisms.md)
- [`pressure-equalization-and-rainscreen.md`](pressure-equalization-and-rainscreen.md)
- [`../performance-testing/curtain-wall-performance-crosswalk.md`](../performance-testing/curtain-wall-performance-crosswalk.md)

> Drainage design 的核心是可追溯的 continuous path。未知 outlet geometry、未知 cavity connection 或未知 pressure basis 時，不應只靠「一般做法」判 PASS。