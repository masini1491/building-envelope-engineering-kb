---
title: "建築外殼常用鋁合金基線：3003-H14 / 3004-H12 / 6005-T5 / 6105-T5 / 6063-T5"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 建築外殼常用鋁合金基線

本頁整理目前台灣帷幕／建築外殼工程常見的鋁板與鋁擠型牌號，作為後續逐牌號詳細頁面的入口。

## 產品形式分類

### 板材／片材

- 3003-H14
- 3004-H12

常見 governing family：
- ASTM B209/B209M — Aluminum and Aluminum-Alloy Sheet and Plate
- CNS 2253 — 鋁及鋁合金片、捲及板（現行中文名稱依 CNS 公告為準）

### 擠型材

- 6005-T5
- 6105-T5
- 6063-T5

常見 governing family：
- ASTM B221 / B221M — Aluminum and Aluminum-Alloy Extruded Bars, Rods, Wire, Profiles, and Tubes
- CNS 2257 — 鋁及鋁合金擠型材

ASTM 目前公開標準索引列：
- B209/B209M-21a
- B221-21 / B221M-21

## 台灣工程實務備註

### 3003-H14 → 3004-H12

近年台灣帷幕／金屬外牆材料供應已有由 3003-H14 轉向 3004-H12 的實務案例與市場趨勢觀察。

目前 repository 將此趨勢標記為：
- `FIELD_OBSERVATION`：實際專案與供應端觀察
- 後續若取得可公開的一手供應商／製造商文件，再提升 verification status

### 平整度議題

3004-H12 導入時，建築師可能因 H12 相對較低加工硬化程度而質疑成品板面平整度。

工程上不應簡化成「H12 一定比 H14 不平」。完成面平整度／oil canning 還受到：
- 板厚
- 面板尺寸與長寬比
- coil / sheet leveling 品質
- 殘留應力
- 裁切與折彎
- 補強配置
- 烤漆固化熱歷程
- 安裝拘束與固定方式

影響。

因此材料替換應分開驗證：
1. alloy / temper 與機械性質
2. 原板 flatness requirement
3. fabrication compatibility
4. full-size finished panel visual mock-up（需要時）

## 設計值防呆

本頁**不保存未逐項核實的 yield strength / tensile strength / allowable stress 數值**。

結構計算應依：
- 當版 governing material standard
- mill certificate
- 專案 design specification
- 採用之 aluminum design standard

確認設計值。

## 標準新鮮度快照

- ASTM B209/B209M-21a：ASTM 2026 非鐵金屬標準索引仍列為 current
- ASTM B221-21 / B221M-21：ASTM 2026 非鐵金屬標準索引仍列為 current
- CNS 2253：標準檢驗局於 2025-04-18 公告修訂；詳細內容應以 CNS 線上服務現行版為準
- CNS 2257：後續建立專頁時再核對最新修訂日期

## 後續待補知識

後續拆頁：
- 3003-H14.md
- 3004-H12.md
- 3003-H14-vs-3004-H12.md
- 6005-T5.md
- 6105-T5.md
- 6063-T5.md
- aluminum-panel-flatness-and-oil-canning.md

## 主要／輔助來源

- ASTM nonferrous standards index: https://store.astm.org/products-services/standards-and-publications/standards/nonferrous-metal-standards-and-nonferrous-alloy-standards.html
- ASTM 2026 BOS Vol. 02 listing: https://store.astm.org/products-services/standards-and-publications/standards/bos-standards.html?volume=2&year=2026
- BSMI CNS standard announcements / services: https://www.bsmi.gov.tw/

> 本頁為工程基線與 routing；個別材料是否可替代必須依專案規範與正式材料證明判斷。