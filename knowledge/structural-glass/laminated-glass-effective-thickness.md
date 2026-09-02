---
title: "膠合玻璃等值厚度與剪力耦合"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
---

# 膠合玻璃等值厚度與剪力耦合

## 核心概念

Laminated glass 的結構行為不能只用 nominal thickness 相加判斷。不同玻璃層之間能傳遞多少剪力，會影響整體彎曲剛度、應力分配與變形。

## Current standard routing

- **ASTM E3491-25**：專門用於 laminated glass effective thickness 的 determination。
- **ASTM E1300-24**：用於建築玻璃 load resistance；若使用 effective-thickness method，應確認適用範圍與輸入條件一致。

## 必要輸入

至少確認：

1. glass ply 數量與各 ply minimum thickness
2. interlayer 種類與厚度
3. interlayer shear / relaxation properties
4. temperature
5. load duration / time scale
6. panel / beam / fin geometry
7. boundary condition
8. in-plane / out-of-plane behavior
9. symmetric / asymmetric make-up

## Interlayer guard

不得把某個 shear modulus `G` 當成跨專案、跨溫度、跨荷載時間的固定材料常數。

應視為：

`G = f(product, temperature, load duration, frequency/time scale, analysis condition)`

若 public manufacturer data 未提供適用條件，不得自行選一個 G 值填入模型。

## Deflection vs stress

Effective thickness 可能對 deflection 與 bending stress 使用不同等效量；AI 不得假設「一個等值厚度可以無條件同時處理所有 response」。

## Multi-ply laminate

三層以上玻璃或多層 interlayer 的 laminate，應依適用方法逐層／整體建模，不可把所有 glass plies 先機械合併成一片，再套雙層公式，除非該方法有明確理論或標準依據。

## Do not assume

- `8+8 laminated = 16 mm monolithic`
- `12+12 laminated = 24 mm monolithic`
- SGP / ionoplast 有固定單一 G 值
- PVB 與 ionoplast 可用同一 coupling assumption
- short-term wind 與 long-term dead load 可用同一 effective thickness

## Primary sources

- ASTM E3491-25: https://store.astm.org/e3491-25.html
- ASTM E1300-24: https://store.astm.org/e1300-24.html

> 實際設計應以 glass / interlayer supplier 的適用 mechanical data、正式標準與經驗證模型為準。