---
title: "玻璃對玻璃結構矽利康（Glass-to-Glass Structural Silicone）"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
document_type: "methodology"
domain: "structural-glass"
canonical_key: "structural-glass.glass-to-glass-structural-silicone"
---

# 玻璃對玻璃結構矽利康（Glass-to-Glass Structural Silicone）

## 適用範圍

本頁處理 structural-glass system 中 glass-to-glass structural silicone 的 load-transfer 與設計 routing。

## 標準與 sealant routing

本頁不維護 ASTM current-edition snapshot。請依：

- [`../sealants/structural-silicone-baseline.md`](../sealants/structural-silicone-baseline.md) — SSG engineering baseline；
- [`../../references/standards/astm-c1184.md`](../../references/standards/astm-c1184.md)；
- [`../../references/standards/astm-c1401.md`](../../references/standards/astm-c1401.md)；
- [`../../references/standards/astm-c1135.md`](../../references/standards/astm-c1135.md)。

## 荷載路徑分流

至少分開：

- wind / pressure load transfer；
- glass self-weight / permanent dead load；
- thermal movement；
- inter-story imposed movement。

不得因 structural silicone 可傳遞風壓，就自動認定它也是主要 dead-load support。若永久自重由 setting block、shoe、bearing member、glass fin 或其他 mechanical support 承擔，analysis model 與 detail 必須反映該 load path。

## Bite／厚度設計 routing

Structural bite 與 sealant thickness 是不同設計參數。

Bite sizing 可由 design load、tributary geometry 與 approved product-specific design stress / method 建立 load-per-unit-length 關係，但：

- design stress / design method 必須有適用標準、manufacturer project review 或正式核准資料；
- 不得把某一專案／品牌數值當 universal value；
- glass-to-glass 與 glass-to-metal substrate / adhesion condition 必須分別確認。

詳見 [`../sealants/structural-silicone-bite-routing.md`](../sealants/structural-silicone-bite-routing.md)。

## 黏著／相容性

應確認：

- glass coating / frit / ceramic surface；
- edge treatment；
- primer requirement；
- spacer / gasket / setting block compatibility；
- cure condition；
- adhesion test；
- production / field QA。

## 位移防呆

Structural silicone 具有 deformation capability，不代表可忽略 joint movement。應以實際 joint geometry、product、design movement 與 substrate behaviour 判斷 shear / tension demand。

## 不可推論事項

- structural silicone allowable stress 是固定常數；
- bite 越大就一定越安全；
- sealant 可以自動平均所有 support reactions；
- flexible sealant 可以消除 structural-glass movement stress；
- product-spec compliance = project-specific SSG approval。

> 專案特定的 structural-glass SSG system，仍須依所選 sealant manufacturer 的 engineering review 與需要的 substrate approval / testing 辦理。