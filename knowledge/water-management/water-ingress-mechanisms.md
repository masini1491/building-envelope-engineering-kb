---
title: "帷幕牆雨水侵入機制（Water-Ingress Mechanisms）"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
---

# 帷幕牆雨水侵入機制（Water-Ingress Mechanisms）

水密問題應先辨識「水為什麼會移動」，再選 detail。不要從 sealant、weep 或 gasket 的單一零件開始倒推整個系統。

## 三項成立條件

外牆發生 rainwater ingress，通常至少需要同時存在：

1. **水源（water source）**；
2. **可通過的路徑（path / discontinuity）**；
3. **使水沿該路徑移動的驅動力（driving force）**。

因此修正策略可以從任一層切斷：減少直接水暴露、阻斷／改變路徑、降低 driving force，或讓進入 cavity 的水被控制與排出。

## 常見 driving forces

### 重力

水會沿有向下連通路徑流動。

設計 review：

- joint slope；
- end dam / upstand；
- horizontal cavity 是否形成 inward fall；
- drainage path 是否連續向外；
- outlet 是否位於 collection point。

### 表面張力／附著

水可能沿材料表面繞過邊緣或轉折。

設計 review：

- drip / capillary break；
- sharp return / undercut；
- 表面污染或塗層是否改變 wetting behaviour；
- detail 是否只是把水引到另一個 vulnerable joint。

### 毛細作用

窄縫可能產生 capillary transport。

設計 review：

- gap geometry；
- capillary break / cavity；
- gasket contact region；
- overlapping sheet / flashing lap；
- sealant backing / discontinuity。

不得使用單一「某縫寬以下必然毛細、以上必然不毛細」的 universal threshold，除非 governing source、材料與 geometry 已確認。

### 雨滴動能／風驅雨

風可能把雨滴直接帶入開口或接縫。

設計 review：

- direct line-of-sight opening；
- baffle / labyrinth；
- exterior joint orientation；
- façade exposure；
- corner / parapet / projection 等局部風雨環境。

### 空氣壓差

室外與 cavity / interior 之間的 pressure differential 可驅動含水空氣或水穿過 joint。

設計 review：

- pressure boundary 在哪一層；
- air seal 是否連續；
- cavity 是否可與 exterior pressure 連通；
- compartment leakage；
- inner seal leakage；
- stack / HVAC / wind pressure interaction。

## 多機制可以同時作用

實際漏水常不是單一原因。

例如 horizontal joint 可能同時存在：

- exterior rain exposure；
- capillary gap；
- inward slope；
- pressure differential；
- blocked weep。

因此「補矽利康後不漏」只能證明當下某一條 path 被阻斷，不能自動證明 root cause 已被正確理解。

## Failure diagnosis 建議流程

1. 標示觀察到的水源與漏水位置。
2. 追蹤可能的連續 path，而不是只看表面裂縫。
3. 列出可能 driving forces。
4. 用 controlled water / pressure / local spray / temporary sealing 等方法逐步隔離變數。
5. 確認 drainage / cavity / air-seal behaviour。
6. 修正後重新驗證，不只確認表面乾燥。

## 與 performance test 的關係

- static water test 主要建立受控水源 + pressure differential；
- dynamic water test 更接近風驅雨與非均勻氣流；
- field diagnostic water check 可協助定位局部 path；
- test method 不同，不能把 PASS 結果互相視為等價。

相關標準 routing：[`../performance-testing/curtain-wall-performance-crosswalk.md`](../performance-testing/curtain-wall-performance-crosswalk.md)。

## 公開來源

- 內政部建築研究所金屬帷幕牆設計技術手冊：歷史台灣 water-ingress topic map。
- NISTIR 4821：two-stage pressure-equalized joint、gravity / capillary / kinetic-energy / pressure-driven rain control principles。

> 本頁定義 mechanism-first review。任何特定 gap、opening、pressure 或 water-head 數值都必須另外有 current source / project basis。