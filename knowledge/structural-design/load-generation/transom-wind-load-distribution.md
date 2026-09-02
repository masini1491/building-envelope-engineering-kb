---
title: "橫料風壓分配方法"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 橫料風壓分配方法

## 為什麼不能只用 uniform line load

對四邊支承的玻璃／面板，面壓傳到橫料時，沿橫料長度的 tributary depth 可能隨位置改變，因此形成 triangular 或 trapezoidal line load，而非固定 `p × constant width`。

這在 curtain-wall transom design 很常見，尤其上下 lite 高度不同時。

## Geometry-first workflow

1. 確認 panel width / height。
2. 確認四邊、兩邊或其他實際 support condition。
3. 將 panel 對 transom 的 tributary region 以幾何方式分配。
4. 將 pressure `p` 轉成 line load `w(x)`。
5. 分別計算 upper lite / lower lite 對 transom 的作用。
6. 依實際 load case 合成 bending moment、shear、deflection 與 end reaction。

## Typical shape concept

四邊支承矩形 panel 常可出現：

- triangular line load
- trapezoidal line load
- upper / lower panel 各自形成不同 distribution

但實際形狀取決於 panel aspect ratio 與採用的 load-distribution assumption；不能只因為「是玻璃」就固定採某一張公式表。

## Wind vs dead load

Transom 的 wind load 與 glass dead load應分開：

- wind：由 panel surface pressure 經支承邊傳入
- dead load：主要由 setting blocks / bearing points 傳入

因此 wind 可為 distributed load，而 dead load常是 concentrated loads。

## Simplified formulas guard

Closed-form beam formulas可以用於：

- preliminary sizing
- hand-check
- independent verification of a computer result

但必須明確記錄：

- load shape
- support condition
- span
- load extent
- eccentricity if any

如果實際 transom 有 sleeve、semi-rigid connection、multiple spans、torsion、eccentric glass seat 或複雜 framing，應採更適當的 structural model。

## Reactions are part of the output

Transom calculation不能只輸出 stress / deflection。至少還應保存：

- left / right end reaction
- wind / dead load reaction 分量
- resulting connector demand

因為這些反力會直接進入 transom-to-mullion fastener / cleat / sleeve 設計。

## Do not assume

- 不得把所有 transom wind load 都簡化成 full-span UDL。
- 不得把 upper / lower lite 作用混成一個未知來源的等效 line load。
- 不得用 wind tributary geometry 算 setting-block dead load。
- 不得在未記錄 distribution assumption 時只留下 final moment。

## Source distinction

本頁的方法論受到實際 curtain-wall calculation workflow 啟發，但公開內容沒有引用或保存任何非公開專案尺寸、荷載或 detail。具體 load distribution 應依公開工程力學方法、適用 façade design guide 與 project geometry 建立。

> Future calculator 應把 `w(x)` 或 load-shape metadata 當一級資料，而不是只保存一個 maximum line load。