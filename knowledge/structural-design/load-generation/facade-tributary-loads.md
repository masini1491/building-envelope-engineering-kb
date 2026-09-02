---
title: "帷幕構件 Tributary Load 方法"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 帷幕構件 Tributary Load 方法

## 核心概念

外牆面壓力 `p` 不能直接拿去檢核 mullion / transom。必須先依面材與支承幾何轉成構件實際承受的 line load 或 point load。

基本概念：

`component load = design pressure × tributary geometry`

但 tributary geometry 由實際 support boundary 決定，不能預設為固定半跨或固定一半面板。

## 直料（Mullion）

對由左右面板將風壓傳給中間 mullion 的常見情況，線荷載可表示為：

`w_m = p × b_t`

其中 `b_t` 為該 mullion 的 tributary width。

對不對稱左右 panel width、edge mullion、corner mullion、opening-adjacent mullion 等，`b_t` 必須由實際幾何建立。

## 橫料（Transom）

Transom 的面材 tributary load 常不是單一 uniform line load。若 panel 四邊支承，面壓向 transom 的分配可能隨位置形成 triangular / trapezoidal line load；應依實際 panel aspect ratio、support assumption 與採用方法建立。

詳見 [Transom Wind-Load Distribution](transom-wind-load-distribution.md)。

## 集中荷載

以下作用通常不應直接平均成 façade UDL：

- setting-block dead load
- bracket / cleat concentrated reactions
- BMU / maintenance attachment
- canopy / sunshade tie
- local hardware load
- point-supported glass reaction

它們應保留 point-load location 與 eccentricity。

## 正／負壓案例

即使後續構件強度只取 absolute envelope，也建議資料層保留：

- positive pressure
- negative pressure
- corresponding tributary geometry
- governing case

因為 connection contact、interlock、sealant、glass support 與 local bearing 在正／負方向可能不是完全對稱。

## 不可推論事項

- 不得把 whole-panel area 當成單一 mullion 的 tributary area。
- 不得因左右 panel 看起來相近就預設各半。
- 不得把 point load 平均成 UDL 來掩蓋 local connection demand。
- 不得把 wind-load tributary geometry 直接套到 glass dead load。

## 公開來源 routing

- 內政部建築研究所《帷幕牆系統結構耐風設計手冊》：component / cladding、直料、橫料與繫件應依其實際受風面與 load path 分別設計。
- 基本 tributary-area / statics 原理。

> 本頁只定義 load transformation 方法，不提供任何 project-specific tributary width。