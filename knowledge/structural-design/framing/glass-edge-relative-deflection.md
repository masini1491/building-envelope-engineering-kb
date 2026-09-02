---
title: "玻璃邊緣相對變形與 Framing Compatibility"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 玻璃邊緣相對變形與 Framing Compatibility

## 核心概念

玻璃與 framing 的 serviceability 問題，常不是由「mullion 最大撓度」單獨控制，而是由玻璃不同支承點之間的**相對位移**控制。

例如同一片玻璃上下邊或左右邊所接觸的 framing 若產生不同 displacement，玻璃 edge clearance、gasket、setting block、structural silicone 或 pressure plate 可能承受額外 movement demand。

## Relative displacement

若 glass edge 上兩個支承位置的 framing displacement 分別為：

- `δ1`
- `δ2`

則最基本的相對位移概念為：

`Δδ = δ1 - δ2`

對多點／連續支承，應沿 glass edge 檢查 displacement profile，而不是只比較兩個端點。

## Why maximum mullion deflection is not enough

假設整支 mullion 以接近 rigid-body translation 的方式移動，即使 absolute deflection 很大，glass edge relative distortion 可能仍小。

反過來，即使 global maximum deflection 不大，如果 glass top / bottom / center support 的位移差很大，局部 edge compatibility 仍可能控制。

## Recommended workflow

1. 建立 framing analysis model。
2. 找出實際 glass-supported edge / contact locations。
3. 取得各 support locations 的 displacement components。
4. 計算 glass 所感受到的 relative displacement / distortion。
5. 分別與適用的：
   - glass edge clearance
   - bite / gasket engagement
   - sealant movement capability
   - pressure plate / pocket geometry
   - project criterion
   比較。
6. 保留 governing load case 與 sign / direction。

## Direction matters

至少區分：

- façade-normal relative displacement
- in-plane rack / lateral displacement
- vertical differential movement
- rotational effect where relevant

不同方向控制不同 failure mode，不能只取一個三維 resultant 後與所有 criterion 比較。

## Glass support assumption

ASTM E1300-24 的玻璃 load-resistance framework 假設支承邊具有足夠剛度，但這不代表 framing serviceability 自動滿足 glass-edge compatibility。玻璃結構檢核與 framing relative-displacement check 應分開。

## Criterion guard

公開 KB 不保存「固定為 glass bite 某百分比」之類未確認通用性的數值。

若某專案、manufacturer glazing guide、AAMA / FGIA document 或其他 public authority 提供 specific clearance / bite / deflection criterion，應以 source + edition + scope 儲存。

在沒有明確 criterion 時，結果應標記為：

`INCOMPLETE — relative displacement computed, acceptance criterion not verified`

## Do not assume

- 不得用 mullion maximum deflection 直接代表 glass edge demand。
- 不得把某一專案使用過的 bite percentage 泛化成 universal rule。
- 不得忽略正／負風壓可能造成的不同 contact state。
- 不得把三維 resultant displacement 當成所有 glazing interface 的唯一 demand。

## Routing

- [ASTM E1300 Glass Load-Resistance Routing](../../glazing/astm-e1300-glass-load-resistance-routing.md)
- [Biaxial Bending and Resultant Deflection](biaxial-bending-and-resultant-deflection.md)
- [Structural Glass Movement](../../structural-glass/structural-glass-movement.md)

> 本頁保存的是 relative-displacement methodology；實際 acceptance limit 必須由適用 public standard、manufacturer guidance 或 project requirement 提供。