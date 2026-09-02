---
title: "活動窗 Hinge／Lock／Stay 連接設計方法"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 活動窗 Hinge／Lock／Stay 連接設計方法

## 角色

活動窗五金連接通常同時包含 hardware body、multiple screws / bolts、薄壁鋁擠型、局部 reinforcement 與 eccentric load。不能只以單支螺絲 capacity 或螺絲數量作完整判定。

## 連接拆解

對每個五金節點至少拆成：

1. hardware body / plate
2. fastener group
3. thread engagement / pull-out
4. local bearing
5. local extrusion wall bending / tear-out
6. reinforcement / backing plate（若有）
7. load transfer into sash / outer frame

## 緊件群分析

若 hardware 以多支 screw / bolt 固定，且 force 不通過 group centroid，應依 [fastener-group-analysis](../structural-design/connections/fastener-group-analysis.md) 建立：

- fastener coordinates
- group centroid
- direct force
- eccentric moment / torsion
- individual fastener resultant demand

不得無條件採 `total force / fastener count`。

## 抗拔／螺紋咬合

薄壁 aluminum extrusion 常可能由 connected material 先 governing，而不是 fastener shank。

應分別確認：

- screw type / thread geometry
- pilot hole / formed hole condition
- extrusion alloy / temper
- actual engaged thickness
- thread engagement length
- edge / local geometry
- applicable test / standard / manufacturer evidence

詳見 [screw-pullout-and-thread-engagement](../structural-design/connections/screw-pullout-and-thread-engagement.md)。

## 鋁擠型局部行為

Hardware load 可能使 extrusion 發生：

- bearing
- local wall bending
- lip / screw-race deformation
- tear-out / edge failure
- local prying

若有 reinforcement，必須確認 reinforcement 自身以及 reinforcement-to-extrusion 的 load path；「有加鐵片／補強料」不等於已自動形成完整 composite section。

## 鉸鏈特定注意事項

Hinge / pivot 可能同時承受：

- sash dead load
- wind reaction
- moment from sash CG eccentricity
- opening / handling load

上下 hinge / pivot 的作用不必相同；實際分配須由 geometry / stiffness / hardware mechanism 決定。

## 鎖點／keeper 特定注意事項

Locking points 主要可能承擔 wind restraint 與 sash sealing / closing function。應確認：

- positive / negative pressure reversal
- keeper bearing / local bending
- screw group eccentricity
- lock engagement geometry
- frame deformation causing engagement loss

`lock connection strength PASS` 仍不等於 closing / sealing function 已驗證。

## 摩擦撐／限位器（Friction stay／restrictor）特定注意事項

Friction stay / restrictor 除 pressure reaction 外還可能有：

- opening angle geometry
- lever-arm amplification
- end-stop load
- repeated operating cycle
- local rail / track attachment demand

靜態強度計算不能替代 durability / life-cycle performance testing。

## 五金修改防呆

若修改：

- hardware model
- quantity
- spacing
- screw type
- substrate thickness
- reinforcement
- sash dimensions / mass

原有 test / rating 的適用性必須重新確認。

## AI 防呆

不得：

- 把 hardware catalogue capacity 直接乘數量
- 只檢查 screw shear 而漏掉 pull-out / bearing / local wall
- 假設所有 hinge 平均承擔 sash weight
- 假設 lock point 只受純剪力
- 忽略 fastener eccentricity
- 把一次 static calculation 當作 life-cycle durability

## 公開來源 routing

- AAMA/WDMA/CSA 101/I.S.2/A440-26 (NAFS)
- AAMA 910-24
- FGIA / manufacturer product-specific hardware technical data as applicable
- AAMA TIR-A9-14 for fenestration fastener design routing

> 本頁只定義 generic connection methodology，不保存非公開專案五金配置。