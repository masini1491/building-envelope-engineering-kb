---
title: "等壓與雨幕設計（Pressure Equalization / Rainscreen）"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
---

# 等壓與雨幕設計（Pressure Equalization / Rainscreen）

Pressure equalization 的目的，是降低 exterior rain barrier 兩側的壓差，使 pressure-driven rain penetration 的 driving force 下降；它通常必須和 air seal、compartmentation、drainage 一起工作。

## 不是「開孔」就叫等壓

一個有效的 pressure-equalized / pressure-moderated concept 至少要回答：

- exterior rain barrier 在哪裡；
- exterior opening / vent 在哪裡；
- cavity / chamber 的界線在哪裡；
- air seal / inner pressure boundary 在哪裡；
- chamber 是否被適當 compartmentalized；
- chamber leakage 路徑有哪些；
- 進入 chamber 的水如何排回室外；
- gust / transient pressure 下是否仍有合理反應。

若只是外層留孔、內側又沒有可靠 air seal，不能因為 detail 有 cavity 就宣稱 pressure equalized。

## 兩階段接縫（Two-stage joint）

公開 NIST guidance 支持以下基本概念：

1. 外層 rain seal / baffle 先減少直接進水與雨滴動能；
2. 外層可設 vent / opening，使 chamber 壓力趨近外部；
3. chamber 後方設較連續的 air seal；
4. chamber geometry 同時處理 gravity / capillary transport；
5. 穿過外層的少量水仍需要 drainage path。

因此 outer seal 與 inner air seal 的功能不能混成同一條「越密越好」的 sealant line。

## Compartmentation

Pressure equalization 並非只看 opening area。

若 cavity 無限制地跨越過大範圍，局部 wind pressure distribution 可能不同，chamber 內部也可能形成 cross-flow。

設計 review 至少應確認：

- vertical / horizontal compartment boundaries；
- mullion / transom / panel joint 的 cavity continuity；
- corner / parapet / roof interface；
- stack joint / unitized chamber continuity；
- unintended holes between compartments；
- inner air seal continuity。

## Dynamic response

風壓不是恆定 scalar。

實際 pressure equalization 會受：

- exterior pressure fluctuation；
- vent/opening flow resistance；
- chamber volume；
- chamber leakage；
- inner air-barrier leakage；
- compartment size；
- local wind field；

影響。

因此不得把某個歷史教材的 chamber/opening ratio、equalization time 或 pressure percentage 當 universal rule。

如果專案的 dynamic performance 是 design requirement，應使用 project-specific analysis / test 或 applicable standard，而不是只憑幾何比例判 PASS。

## Rainscreen vs Drained / Back-ventilated

必須分辨不同 system concept：

- **pressure-equalized rainscreen**：以 pressure moderation / equalization 作核心；
- **drained / back-ventilated rainscreen**：重點可以是 drainage + ventilation，而不一定達成 pressure equalization。

FGIA 目前分別有：

- AAMA 508-21：pressure-equalized rainscreen wall cladding systems；
- AAMA 509-22：drained and back-ventilated rainscreen wall cladding systems。

不能只因都有 cavity / open joint 就把兩者等同。

## Curtain wall 系統中的應用

在 stick / unitized curtain wall 中，pressure moderation 可能發生於：

- pressure-equalized glazing rebate；
- horizontal rail cavity；
- mullion cavity；
- stack joint；
- drained gasket / pressure plate system；
- metal panel rainscreen cavity。

每個 cavity 的 pressure boundary、drainage outlet 與 compartment behaviour 可能不同。

## 常見失敗模式

- exterior vent 被 sealant / tape 封死；
- inner air seal discontinuity；
- horizontal cavity 無 end dam；
- compartment 被連通；
- weep / drain blocked；
- cavity 形成 inward slope；
- drainage outlet 位於高點；
- outer joint direct line-of-sight 讓風驅雨直接打入；
- field modification 改變原 pressure boundary；
- unitized stack joint 中 inner seal / baffle 損傷。

## 驗證

依系統與專案要求，可能需要：

- laboratory static / dynamic water test；
- AAMA 508 evaluation（適用 rainscreen cladding 時）；
- field diagnostic water test；
- mock-up inspection of cavity / seal / weep before closure；
- pressure taps / instrumentation for research or special validation。

## 主要公開來源

- [`../../references/standards/aama-508-21-pressure-equalized-rainscreen.md`](../../references/standards/aama-508-21-pressure-equalized-rainscreen.md)
- [`../../references/government/nist-envelope-rain-penetration-and-pressure-equalization.md`](../../references/government/nist-envelope-rain-penetration-and-pressure-equalization.md)
- [`../../references/government/abri-metal-curtain-wall-design-manual-2003.md`](../../references/government/abri-metal-curtain-wall-design-manual-2003.md)

> Pressure equalization 是 system behaviour，不是一個單獨尺寸或單一開孔比。若 project-specific chamber ratio、vent size、pressure-response criterion 沒有來源，應標 `INCOMPLETE`。