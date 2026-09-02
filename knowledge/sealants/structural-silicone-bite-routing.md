---
title: "結構矽利康 bite／接縫幾何設計 routing"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
document_type: "methodology"
domain: "sealants"
canonical_key: "sealants.structural-silicone-bite-routing"
---

# 結構矽利康 bite／接縫幾何設計 routing

## 標準 routing

本頁不維護 ASTM edition snapshot。current edition / status 由以下 dossier 單一維護：

- [`../../references/standards/astm-c1184.md`](../../references/standards/astm-c1184.md)
- [`../../references/standards/astm-c1401.md`](../../references/standards/astm-c1401.md)
- [`../../references/standards/astm-c1135.md`](../../references/standards/astm-c1135.md)

工程角色與 SSG 基線見 [`structural-silicone-baseline.md`](structural-silicone-baseline.md)。

## 核心概念

Structural silicone bite 不是固定材料常數，也不是所有案子都用同一尺寸。它是 project-specific joint design 結果，至少受：

- design wind pressure；
- glass / panel tributary dimension；
- joint geometry；
- product-specific manufacturer-approved design stress / method；
- substrate / coating；
- sealant thickness；
- allowable movement；
- temperature / cure condition；
- support arrangement。

影響。

## 設計流程

1. 確認 structural silicone 實際承擔的 load path。
2. 取得 positive / negative design-pressure envelope。
3. 確認玻璃／panel 尺寸與 silicone support perimeter。
4. 依所選產品之正式 technical procedure / project review 設計 bite / thickness。
5. 驗證 substrate adhesion、primer requirement、compatibility。
6. 確認 shop / field QA、cure、handling、repair / replacement procedure。

## 有效黏著寬度（Bite）與厚度

- **bite**：沿被黏結面承擔 structural load 的有效黏著寬度。
- **thickness**：兩 substrate 間 sealant bead 厚度／間距，與 movement capability、installation tolerance、cure 等相關。

不能用增加 bite 無限補償 thickness 不合理，也不能反過來。

## 製造商審查防呆

不同 silicone product 的 design method、allowable stress、minimum geometry、substrate approval、warranty condition 可能不同。

因此本 Repo 不保存跨品牌通用固定 structural allowable。正式案應以：

- project specification；
- manufacturer current technical data；
- manufacturer project-specific structural review；
- adhesion / compatibility test；

為準。

## 自重

Structural silicone 是否可承擔玻璃永久自重，不可由一般 SSG 概念推定。應依 system design、setting block / dead-load support arrangement、產品與 manufacturer approval 判斷。

## 不可推論事項

- 固定 `6 mm`、`12 mm` 等 bite 不可作 universal rule。
- material specification compliance 不等於任意 bite 都成立。
- weatherseal sizing 不可直接當 structural bite sizing。
- 同品牌不同產品也不得自動共用 allowable design parameter。

> 正式 structural silicone sizing 應由採用產品之 manufacturer technical review 與專案計算確認。