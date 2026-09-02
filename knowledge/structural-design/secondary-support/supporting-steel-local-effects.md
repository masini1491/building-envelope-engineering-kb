---
title: "支承鋼構局部效應（Supporting-Steel Local Effects）"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
---

# 支承鋼構局部效應（Supporting-Steel Local Effects）

本頁處理 façade reaction / back brace 導入 primary or secondary steel member 後，除了整體 beam strength 之外可能出現的局部與扭轉效應。

## 核心原則

**Receiving member global PASS ≠ load-introduction zone PASS。**

一個很大的鋼梁，如果 concentrated reaction 作用在偏心 flange、薄 web 或局部 connection plate 上，仍可能由 local effect 控制。

## 典型檢核項目

依 geometry / load path，可能包括：

- beam torsion；
- flange local bending；
- flange local yielding；
- web local yielding；
- web crippling / local buckling；
- concentrated-force effect；
- local plate bending；
- stiffener demand；
- doubler / reinforcement plate；
- weld-group transfer；
- bolt-group transfer；
- secondary member end reaction；
- eccentricity-induced secondary moment。

不是每案都需要全部檢查，但任何被判 `NOT_APPLICABLE` 的項目都應有 geometry / mechanics basis。

## 偏心與扭轉

Reaction 若作用點不在 beam shear center / web plane，應至少辨識：

- force magnitude；
- eccentricity；
- resulting torsional moment；
- restraint condition；
- load introduction length；
- adjacent framing / diaphragm 是否提供 torsional restraint。

不能只把反力投影成 vertical / horizontal shear 後忽略扭矩。

## 翼板／腹板（Flange／Web）局部行為

若 connection 作用在 beam flange / web 局部區域，應確認：

- actual bearing / load patch；
- flange thickness；
- web thickness；
- distance to web / stiffener；
- weld / bolt geometry；
- concentrated force direction；
- compression / tension reversal；
- repeated loading where relevant。

是否需要 stiffener 應由 governing structural method 與 actual demand 判斷，不能用固定 façade wind-pressure threshold 直接決定。

## 加勁板（Stiffener）的角色

Stiffener 可能用來：

- reduce local flange / web deformation；
- improve concentrated-load transfer；
- provide brace connection geometry；
- increase torsional / local restraint；
- transfer load to both flanges / web。

但 stiffener 也可能：

- 改變 load path；
- 產生新的 weld demand；
- 造成 fabrication / access issue；
- 干涉 deck / MEP / fireproofing；
- 把力導到未檢查的位置。

因此 `加 stiffener` 不是自動 PASS。

## 下游結構責任（Downstream structural responsibility）

在 reaction-only handoff 模式下，這些 local effects 通常屬於 primary-structure engineer / designated steel designer 的 scope；帷幕端至少應提供足以讓對方建立 local model 的：

- reaction magnitude / direction；
- reaction point；
- eccentricity；
- repeated spacing；
- interface geometry；
- load case / design level；
- revision。

若 responsibility boundary 未確認，狀態應為 `INCOMPLETE`，不能假設「主結構一定會自己處理」。

## 與 façade back brace 的分工

若帷幕端負責 brace，本頁的 local receiving-steel effects 仍可能位於另一個責任範圍。

例如：

`brace member: PASS`

但：

`receiving_beam_local_effects: INCOMPLETE`

這是合法且更精確的 review outcome。

## 係數稽核（Factor audit）

任何用來簡化 flange / web / torsion capacity 的 coefficient、allowable multiplier、company rule 或歷史 project factor，都必須有 provenance。

不得只因最後 stress ratio 看起來小於 1 就接受不明 factor。

Routing：[`../review/design-factor-and-hidden-multiplier-audit.md`](../review/design-factor-and-hidden-multiplier-audit.md)。

> 本頁只建立 failure-mode / review routing；具體 steel-member local-capacity equation、stiffener criterion 與 resistance factor 應由 governing structural standard 與 project design basis 提供。