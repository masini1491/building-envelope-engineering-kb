---
title: "耐震位移相容性"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 耐震位移相容性

## 核心概念

Façade seismic design 有兩條不同但互相關聯的問題：

1. **strength / force path**：構材與連接能否承受地震作用力；
2. **movement compatibility**：建築物層間變形時，外牆是否能在不產生脫落、玻璃破壞、卡死或過大局部應力下隨動。

兩者必須分開檢核。

## 位移傳遞鏈

典型位移傳遞可寫成：

`story drift → slab / beam relative movement → anchor movement → mullion / unit movement → splice / stack joint → glass edge / gasket / silicone deformation`

任一節點若把原本應釋放的 movement 鎖死，整個系統可能改變受力路徑。

## 結構模型輸入

至少應保存：

- governing inter-story displacement / drift source
- direction
- support-to-support relative movement
- fixed / sliding support locations
- slot orientation / available travel
- splice / stack-joint gap
- mullion deformation superimposed on building movement
- glass-support displacement
- sealant / gasket movement demand

## 相對位移，而非僅絕對位移

對玻璃或面板來說，真正重要的常是相鄰支承點之間的**相對位移**，而不是某一節點對 global origin 的絕對位移。

因此應計算：

`Δ_relative = displacement(point B) - displacement(point A)`

再依實際支承／邊緣 clearance / joint capacity 判斷是否可接受。

## 層間變位與構件撓度

Building drift 與 wind-induced member deflection 是不同 action source，但在某些 serviceability / compatibility check 中可能需要依規範或 project basis 做相容性評估。

不得自行把兩者直接代數相加或取 envelope；應依 governing design basis 處理。

## 工程主題：Stack joint／splice

Unitized / stick system 在 splice / stack joint 可能需要：

- axial sliding
- in-plane racking
- out-of-plane movement
- rotation

實際容許模式必須由 joint geometry 與 connection design確認，不能只因存在 gap 就宣稱 movement 已被 accommodated。

## 玻璃邊緣／sealant routing

若 movement 會傳到玻璃支承邊，應再檢查：

- edge clearance
- setting block / side block contact
- gasket compression / disengagement
- structural-silicone movement
- point-supported glass local contact

相關 routing：

- `../framing/glass-edge-relative-deflection.md`
- `../../structural-glass/structural-glass-movement.md`
- `../../sealants/structural-silicone-baseline.md`

## 試驗 routing

Inter-story movement performance 可與 applicable laboratory / mock-up standard 對照，例如 repository 既有 performance-testing crosswalk 中的 CNS 14281 / AAMA 501.4 routing。

但 test specimen PASS 不代表所有不同 geometry / anchor / panel size 的 façade location automatically covered；必須確認 representation。

## 不可推論事項

- `story drift ratio × story height` 永遠就是 façade joint demand
- 有 slotted hole 就等於可滑動到 slot 全長
- gap dimension = usable movement capacity
- glass edge clearance 全部可用於地震位移
- laboratory specimen PASS = 全案所有 façade configuration PASS
- force check PASS = movement compatibility PASS

## 輸出要求

至少輸出：

1. building movement source
2. support locations
3. relative movement demand
4. joint / slot / gap available movement
5. glass / panel interface demand
6. sealant / gasket demand if applicable
7. test / calculation evidence
8. governing status
9. assumptions / missing data

## 一手來源 routing

- 內政部國土管理署《建築物耐震設計規範及解說》
- CNS 14281 / AAMA 501.4 inter-story movement performance routing
- project structural drift criteria / approved façade movement design basis

> 本頁不保存任何非公開專案的 drift value、joint gap、anchor layout 或 specimen geometry。