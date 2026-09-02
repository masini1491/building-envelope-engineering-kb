---
title: "鋁擠型連接處局部破壞模式"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 鋁擠型連接處局部破壞模式

## 角色

帷幕牆 connection 的 governing failure mode 常不是整支 mullion / transom 的 global bending，而是 bolt、screw、hook、sleeve、cleat 或 bracket 周圍的薄壁鋁擠型先發生局部破壞。

因此「member strength PASS」不能取代 local connection check。

## 常見局部 failure modes

至少依節點實際受力考慮：

- bearing at bolt / screw hole
- local wall bending
- local flange / web bending
- tear-out / edge failure
- net-section rupture
- screw pull-out / thread stripping
- pull-over in thin sheet where applicable
- local hook / lip bending
- sleeve-to-extrusion local flexure
- prying-related local deformation
- local crippling / concentrated-load deformation where applicable

並非每一節點都需要全部檢查；應依 load path 決定 applicable modes。

## Local-section model

常見簡化方法是把受力區域抽象成一段局部板件，建立：

- effective width `b_eff`
- local thickness `t`
- local depth / lever arm
- section area `A`
- second moment of area `I`
- section modulus `Z`
- applied local shear / tension
- eccentricity `e`

再由：

`M = F × e`

與適用的 local section properties 評估 bending / combined stress。

但 `b_eff` 不是任意可選參數。有效寬度的來源必須是：

- 適用標準／design manual
- 經驗證的公司方法
- 有工程依據的有限元素／試驗結果
- project-approved calculation basis

不能由 AI 為了讓 ratio 通過而調整 effective width。

## Bearing

理想化平均 bearing stress 常可寫成：

`f_b = V / (t d)`

其中 `V` 為傳入孔壁的力、`t` 為被承壓材料厚度、`d` 為適用的 fastener / bearing diameter。

這只是 demand expression；allowable / design bearing strength、edge-distance reduction、hole type、load direction、temper / heat-affected condition 等仍須依適用規範。

## Local wall bending

當 bolt / screw force 的作用線與局部板件 critical section 有 eccentricity，需考慮：

`M = F e`

再由：

`f_b = M / Z`

檢查局部壁厚是否足夠。

帷幕常見情況包括：

- bolt channel 壁
- screw race 附近薄壁
- hook / lip
- cleat support wall
- extrusion web adjacent to bracket

## Screw pull-out / thread stripping

對直接鎖入鋁擠型的 screw，至少要區分：

1. screw 本體 tension / shear
2. connected aluminum bearing
3. internal thread / engaged material pull-out or stripping

第三項受：

- screw diameter
- thread pitch / threads per unit length
- engaged thickness
- aluminum alloy / temper
- thread form
- pilot hole / tapping condition
- installation quality

影響。

不得因 screw 本體 A2-70 或其他 property class 很高，就推論 thread engagement 也有相同等級的 capacity。

## Thread engagement

若 design method 用 minimum engaged thickness 來確保 screw / bolt tensile capacity可被充分發揮，必須保存：

- governing source
- fastener thread geometry
- connected material
- assumed failure mode
- minimum calculated engagement
- actual engagement

不能只留下「至少 X mm」而失去來源與適用條件。

## Thin-wall and geometry guard

鋁擠型截面常具有：

- asymmetric walls
- screw races
- hollow cavities
- local radii
- lips / hooks
- variable thickness
- nearby free edges

所以不可把整個 extrusion 都當作無限寬平板。

如果 local geometry 對結果高度敏感，應使用 verified CAD geometry、局部 shell / solid FEA 或經驗證的 test data。

## HAZ / welding guard

鋁擠型若在 critical region 附近焊接，焊接熱影響可能改變局部材料強度。此時不能仍無條件採用未焊母材的 alloy / temper allowable。

應路由至適用的 Aluminum Design Manual / AWS aluminum welding design basis，再依 weld location 與 heat-affected zone 評估。

## 建議輸出

局部 connection calculation 至少記錄：

1. critical local section
2. load path
3. force / moment / eccentricity
4. local geometry and thickness
5. effective width source（若使用）
6. demand equation
7. material / condition
8. governing capacity source
9. utilization ratio
10. adjacent failure modes not yet checked

## AI 防呆

AI 不得：

- 只看到 global mullion PASS 就宣稱 connection PASS
- 自行捏造 effective width
- 忽略 hole edge distance / connected thickness
- 把 screw strength 當成 pull-out strength
- 把 nominal extrusion wall thickness 當成所有 critical section 的實際有效厚度
- 在焊接附近忽略 HAZ effect

## 相關頁面與 routing

- global framing：`../framing/mullion-transom-design-baseline.md`
- fastener group：`fastener-group-analysis.md`
- load path：`load-path-and-anchor-reactions.md`
- weld group：`weld-group-analysis.md`

> 本頁是 failure-mode routing 與一般 mechanics framework；任何 allowable / design strength 與 effective-width rule 必須另有可靠來源。