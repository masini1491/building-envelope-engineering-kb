---
title: "Required Section Properties：I 與 S 的前期反推"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# Required Section Properties：I 與 S 的前期反推

## 用途

在實際 extrusion 尚未完成或尚未取得完整 section properties 時，可先依 load、span、support、material modulus 與 design criteria 反推最低需要的 section performance。

此方法適合 preliminary sizing，不等於正式 project-specific structural calculation。

## Deflection → Required I

線彈性、小變形且 member stiffness 可按比例縮放時，撓度與 `1/(EI)` 成正比。

若以 trial section property `I_trial` 得到 `delta_trial`，且允許撓度為 `delta_allow`，可用：

`I_required = I_trial × |delta_trial| / delta_allow`

前提至少包括：

- `E > 0`
- `delta_allow > 0`
- support model 合法且不奇異
- load 非零
- member stiffness assumptions 與 trial / required case 一致

對 simple-span uniform load，可用 closed-form solution 作 sanity check；複雜 multi-span / semi-rigid / eccentric system 不應因有此比例式就忽略正確結構模型。

## Bending strength → Required S

若採 ASD 型式且已有 project-approved allowable bending stress：

`S_required = |M_max| / F_allow`

其中 `F_allow` 必須來自可追溯的 material / project criteria，不得由 AI 或 calculator 自行以 `Fy / arbitrary safety factor` 生成。

若 allowable stress 不明，strength result 應為 `INCOMPLETE`。

## I 與 S 不可互相取代

- `I` 控制 stiffness / deflection。
- `S` 控制 extreme-fiber bending stress。

只有在已知 `I` 與對應 extreme-fiber distance `c` 時，才能由 `S = I / c` 導出該方向 section modulus。

非對稱截面應保留正／負 extreme fiber：

- `Sx+`, `Sx-`
- `Sy+`, `Sy-`

不得只存單一 `Sx` / `Sy` 而忽略方向差異。

## Actual verification

取得實際 section property 後，可做：

- `I_actual >= I_required` → stiffness requirement satisfied
- `S_actual >= S_required` → bending-strength requirement satisfied

但正式判斷仍應同步重新計算 actual deflection / actual stress，而不是只比較 ratio。

## Governing envelope

一個構件可能有多個：

- positive / negative wind cases
- tributary conditions
- support conditions
- bending axes

因此 required result 應保存 governing case 與 governing axis，而不是只輸出一組沒有來源的數字。

## Do not assume

- 有 `Ix` 不代表已有 `Sx`。
- `Ix > Iy` 不代表 x 一定是實際 strong axis；必須依截面與 load orientation 定義。
- male / female profile 的 `I` 不得預設可直接相加。
- preliminary required property 不等於 final extrusion approval。

> 本頁保存方法論；實際 allowable stress、deflection limit、support condition 與 section properties 必須由各專案可靠來源提供。