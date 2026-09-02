---
title: "Structural Silicone Bite／Joint Geometry 設計 Routing"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
---

# Structural Silicone Bite／Joint Geometry 設計 Routing

## Core standards

- ASTM C1184-25：structural silicone sealant material specification
- ASTM C1401-24：structural sealant glazing design / installation guide
- ASTM C1135-15(2020)：tensile adhesion test method

## 核心概念

Structural silicone bite 不是固定材料常數，也不是「所有案子都用同一尺寸」。它是 project-specific joint design 的結果，至少受：

- design wind pressure
- glass / panel tributary dimension
- joint geometry
- sealant product 的 manufacturer-approved design stress / design method
- substrate / coating
- sealant thickness
- allowable movement
- temperature / cure condition
- system support arrangement

影響。

## Design workflow

1. 確認 structural silicone 實際承擔的 load path。
2. 取得 positive / negative design pressure envelope。
3. 確認玻璃／panel 尺寸與 silicone support perimeter。
4. 依 sealant manufacturer 的正式 structural calculation procedure 與 project review 設計 bite / thickness。
5. 驗證 substrate adhesion、primer requirement、compatibility。
6. 確認 shop / field QA、cure、handling、deglazing / repair procedure。

## Thickness and movement

Structural bite 與 sealant thickness 是不同幾何參數：

- bite：沿被黏結面承擔 structural load 的有效黏著寬度
- thickness：兩 substrate 間 sealant bead 的厚度／間距，與 movement capability、installation tolerance、cure 等相關

不能用增加 bite 無限補償 thickness 不合理，也不能反過來。

## Manufacturer-review guard

不同 silicone product 的設計方法、allowable stress、minimum geometry、substrate approval、warranty condition 可能不同。

因此 Repo 不保存一個跨品牌通用固定 allowable structural stress；正式案應以：

- project specification
- sealant manufacturer current technical data
- manufacturer project-specific structural review
- adhesion / compatibility test

為準。

## Dead load

是否允許 structural silicone 承擔玻璃永久自重，不可由一般 SSG 概念自行推定。應依系統設計、setting block / dead-load support arrangement、產品與 manufacturer approval 判斷。

## Do not assume

- `固定 6 mm bite`、`固定 12 mm bite` 等不能當通用規則。
- C1184 compliant 不等於任意 bite 都成立。
- weatherseal joint sizing 不可直接拿來當 structural bite sizing。
- 同品牌不同產品也不得自動共用 allowable design parameter。

## Primary sources

- ASTM C1184-25: https://store.astm.org/c1184-25.html
- ASTM C1401-24: https://store.astm.org/c1401-24.html
- ASTM C1135-15(2020): https://store.astm.org/c1135-15r20.html

> 正式 structural silicone sizing 應由採用產品之 manufacturer technical review 與專案計算確認。