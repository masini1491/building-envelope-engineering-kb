---
title: "偏心緊件群分析方法"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 偏心緊件群分析方法

## 角色

帷幕牆 connection 很常以多支 bolt / screw 形成 fastener group。當外力作用線不通過緊件群形心時，不能只用 `總力 ÷ 緊件數`。除了 direct shear / direct tension，還要處理由偏心產生的 moment / torsion 所造成的附加緊件力。

本頁整理通用計算框架，不提供任何特定專案尺寸、緊件配置或 allowable capacity。

## 基本輸入

至少需要：

- fastener 數量與每支座標 `(x_i, y_i)`
- group centroid
- applied force components `Fx / Fy / Fz`
- applied moments `Mx / My / Mz`
- force application eccentricity
- fastener type / diameter / thread condition
- connected-material thickness / edge distance / hole type
- governing fastener and connected-material capacity source

若 fastener stiffness 明顯不同、孔洞為 slot、部分孔位有 gap 或某些 fastener 不承受特定方向，不能直接使用等剛度群組模型。

## 1. 緊件群形心（Fastener-group centroid）

若所有緊件視為等剛度，群組形心可用幾何平均：

`x̄ = Σx_i / n`

`ȳ = Σy_i / n`

若各緊件剛度不同，應依實際 stiffness weighting 建模，不應仍使用純幾何平均。

## 2. 直接力（Direct force）

理想等剛度、所有緊件共同承載時：

`F_direct = F / n`

但這只代表通過 group centroid 的 direct component。

以下情況不得直接使用：

- slotted hole 在某方向允許 movement
- 部分 fastener 尚未 bearing
- single-sided contact / clearance
- fastener pretension / friction 被設計成主要 load-transfer mechanism
- connector flexibility 顯著不同

## 3. 面內偏心剪力／扭矩

對位於 `(x_i, y_i)` 的 fastener，可先定義相對 group centroid 的：

`r_i² = x_i² + y_i²`

等剛度彈性法常使用：

`J_group = Σ r_i²`

對繞群組法向軸的 moment `M`，第 i 支緊件由 moment 造成的 tangential force magnitude 可表示為：

`F_m,i = M r_i / J_group`

其方向與 `r_i` 垂直，再與 direct shear 向量合成。

這是 linear-elastic fastener-group model；若 connection 進入 bearing redistribution、slip、yielding 或大變形，需使用更適合的模型。

## 4. 偏心拉力／傾覆作用

對 bolt group 承受面外拉力與 overturning moment 時，應依實際 connection mechanics 分配 tension。不得假設：

- 所有 bolts 永遠平均承受 tension
- compression side bolts 仍與 tension side 相同受拉
- connected plate 完全剛性
- prying action 可忽略

必要時應考慮：

- compression bearing block / contact region
- plate flexure
- bolt-row lever arm
- prying
- anchor / bolt stiffness

## 5. 拉力＋剪力組合

每一支 fastener 的 demand 至少應分開求得：

- shear resultant `V_i`
- tension `T_i`

之後再依**適用標準或產品資料**的 interaction rule 檢核。

AI 不得自行把所有 fastener 都套成：

`(V/V_allow)² + (T/T_allow)² ≤ 1`

因為 interaction equation、allowable / design strength basis、thread condition 與 standard family 可能不同。

## 6. 被連接材料檢核

fastener 本體 PASS 不代表 connection PASS。至少要依實際情況檢查：

- bearing
- tear-out / edge failure
- net section
- local wall bending
- pull-out / thread stripping
- pull-over for thin sheet where applicable
- plate bending / prying
- block shear where applicable

## 7. 螺絲群特定防呆

對 curtain-wall self-tapping / machine screw connection，常見風險包括：

- screw shear capacity 足夠，但 extrusion thread engagement 不足
- screw tension capacity 足夠，但薄壁局部 pull-out governs
- eccentricity 導致遠端 screw demand 顯著高於平均值
- screw group geometry 改變後仍沿用舊計算

因此 input 應保留 screw coordinates，而不是只保存 `number_of_screws`。

## 8. 建議計算輸出

至少輸出：

1. group centroid
2. fastener coordinates relative to centroid
3. applied forces / moments
4. direct force component
5. moment-induced component
6. resultant demand per fastener
7. governing fastener
8. fastener strength check
9. connected-material failure modes
10. assumptions / excluded nonlinear behavior

## AI 防呆

不得：

- 無條件使用 `F/n`
- 無座標仍假裝完成 eccentric group calculation
- 只驗證 bolt / screw 本體，不驗證 connected material
- 用 property class 直接生成 connection capacity
- 把某一既有計算書內的 table value 當成現行 universal allowable

資料不足時應明確回報：

`fastener_group_geometry incomplete`、`capacity source pending verification` 或 `connected-material check incomplete`。

## 相關頁面與 routing

- 緊件 material / property class：`knowledge/fasteners/`
- 整體 load path / anchor reaction：`load-path-and-anchor-reactions.md`
- 局部鋁擠型破壞：`local-extrusion-failure.md`
- weld connection：`weld-group-analysis.md`

> 本頁描述的是通用 elastic fastener-group mechanics。實際 capacity、interaction 與 failure criteria 必須回到適用的現行標準、產品資料與 project design basis。