---
title: "活動窗扇／框結構分析方法"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 活動窗扇／框結構分析方法

## 角色

活動窗 sash / vent frame 不是單純四根鋁料拼成矩形。其結構反應同時受到玻璃／填充材、自重、風壓、五金支承位置、corner joint、frame-to-sash clearance 與局部補強影響。

因此整窗結構分析應先建立完整 load path，再決定可否用簡化梁／框架模型或需要 2D / 3D FEA。

## 基本 workflow

1. 定義 sash / outer-frame geometry。
2. 定義玻璃或 infill 的重量與支承方式。
3. 定義 hinge / stay / lock / keeper / restrictor 的位置與 boundary condition。
4. 定義 section properties、material、reinforcement。
5. 建立 wind load 與 dead-load case。
6. 分析 frame bending、torsion、racking、deflection 與 hardware reactions。
7. 將 reactions 傳至 hardware / fastener / local extrusion checks。
8. 再以 whole-product performance test routing 驗證需要的 air / water / structural / operability performance。

## Load cases

至少分開考慮：

- positive wind pressure
- negative wind pressure
- sash / glass dead load
- operating / handling load where required
- hardware stop / restrictor load where required
- seismic / building-movement effects where project requires

不要一開始就把所有作用合成單一 envelope；不同 load direction 可能改變 hinge / lock 哪一側 governing。

## Glass / infill dead load

玻璃自重通常透過 setting block / glazing support 傳到 sash frame，再由 hinge / pivot / support hardware 傳回 outer frame。

因此：

`glass weight → setting block → sash member → hinge/support hardware`

不應直接假設全部 glass dead load 平均分到所有硬體。

## Wind-load transfer

風壓作用於 glass / infill 後，reaction 由 sash perimeter 傳入：

- hinge side
- lock side
- top / bottom rails
- corner joints
- hardware points

實際 distribution 取決於 frame stiffness、hardware spacing、locking-point layout 與 boundary condition。

## Corner-joint behavior

Corner joint 可能是：

- crimped / mechanically keyed
- screwed
- welded
- reinforced
- adhesive-assisted
- proprietary system

不得只因外觀形成閉合框，就默認四角完全剛接。若 corner rotational stiffness 對分析有影響，應由產品資料、試驗或 validated model 支持。

## Frame analysis choices

### Beam / frame model

適合幾何與 load path 清楚、截面可用 beam properties 表示、corner / hardware boundary condition 可合理 idealize 的情況。

### Shell / solid model

當局部薄壁變形、hardware cut-out、corner joint、reinforcement、torsion 或 local contact 重要時，可需要更高階模型。

模型精細度應由 failure mode 決定，不是越複雜越好。

## Results to preserve

至少保存：

- member moment / shear / axial force
- frame deflection
- sash racking / relative corner displacement
- hardware reactions
- corner-joint demand
- local reinforcement demand
- glass-edge / gasket relative movement where relevant

## Operability guard

結構計算即使應力與撓度均 PASS，也不自動代表窗仍可正常操作。

整窗可能因：

- sash racking
- hardware misalignment
- keeper interference
- gasket compression change
- permanent set

造成 operating force / locking function 異常。

因此需要時應以 NAFS / AAMA 910 或 project-specific performance test 驗證。

## AI guard

不得：

- 將 sash 四邊自動假設為 fixed frame
- 將所有 hinge / lock reaction 平均分配
- 把 corner joint 默認 rigid
- 用單一 member deflection 代表整窗 operability
- 只算 aluminium member stress 就宣告整窗 structural PASS
- 忽略 glass dead-load path

## Public-source routing

- AAMA/WDMA/CSA 101/I.S.2/A440-26 (NAFS)
- AAMA 910-24
- ASTM E330/E330M-14(2021)
- The Aluminum Association, Aluminum Design Manual 2020

> 本頁不提供任何特定窗型的五金位置、尺寸或固定 allowable。