---
title: "結構矽利康 bite／接縫幾何設計 routing"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
---

# 結構矽利康 bite／接縫幾何設計 routing

## 核心標準

本頁的標準版本以 `structural-silicone-baseline.md` 為 canonical routing；截至 2026-09-02：

- ASTM C1184-23：structural silicone sealant material specification
- ASTM C1401-23：structural sealant glazing design / installation guide
- ASTM C1135-19(2024)：tensile adhesion test method

若版本資訊更新，應優先更新 canonical baseline，再同步檢查本頁，不在不同頁面各自維護互相衝突的 current-edition snapshot。

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

## 設計流程

1. 確認 structural silicone 實際承擔的 load path。
2. 取得 positive / negative design pressure envelope。
3. 確認玻璃／panel 尺寸與 silicone support perimeter。
4. 依 sealant manufacturer 的正式 structural calculation procedure 與 project review 設計 bite / thickness。
5. 驗證 substrate adhesion、primer requirement、compatibility。
6. 確認 shop / field QA、cure、handling、deglazing / repair procedure。

## 厚度與位移

Structural bite 與 sealant thickness 是不同幾何參數：

- bite：沿被黏結面承擔 structural load 的有效黏著寬度
- thickness：兩 substrate 間 sealant bead 的厚度／間距，與 movement capability、installation tolerance、cure 等相關

不能用增加 bite 無限補償 thickness 不合理，也不能反過來。

## 製造商審查防呆

不同 silicone product 的設計方法、allowable stress、minimum geometry、substrate approval、warranty condition 可能不同。

因此 Repo 不保存一個跨品牌通用固定 allowable structural stress；正式案應以：

- project specification
- sealant manufacturer current technical data
- manufacturer project-specific structural review
- adhesion / compatibility test

為準。

## 自重

是否允許 structural silicone 承擔玻璃永久自重，不可由一般 SSG 概念自行推定。應依系統設計、setting block / dead-load support arrangement、產品與 manufacturer approval 判斷。

## 不可推論事項

- `固定 6 mm bite`、`固定 12 mm bite` 等不能當通用規則。
- C1184 compliant 不等於任意 bite 都成立。
- weatherseal joint sizing 不可直接拿來當 structural bite sizing。
- 同品牌不同產品也不得自動共用 allowable design parameter。

## 主要來源

- Canonical repo routing：`knowledge/sealants/structural-silicone-baseline.md`
- ASTM C1184-23: https://store.astm.org/c1184-23.html
- ASTM C1401-23: https://store.astm.org/c1401-23.html
- ASTM C1135-19(2024): https://store.astm.org/c1135-19r24.html

> 正式 structural silicone sizing 應由採用產品之 manufacturer technical review 與專案計算確認。