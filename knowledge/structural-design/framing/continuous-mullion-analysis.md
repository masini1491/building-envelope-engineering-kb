---
title: "Continuous Mullion 多跨直料結構分析方法"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# Continuous Mullion 多跨直料結構分析方法

## 角色

帷幕牆直料不一定是單跨 simply supported beam。實際系統可能跨越多個樓層，並在樓板 anchor、splice、sleeve、stack joint 或其他節點處形成不同程度的 translational / rotational restraint。

因此正式分析應先建立**結構模型**，再求 member force、deflection 與 support reaction；不能先挑一條熟悉的單跨梁公式再反推模型。

## 基本 workflow

1. 定義 global / local axes。
2. 建立 mullion 節點位置。
3. 定義每一段 span 的 `E / I / A` 與必要時的 shear / torsional properties。
4. 對每個節點定義 translational restraint、rotational restraint 與 movement freedom。
5. 對 splice / sleeve 定義其 force-transfer model。
6. 施加各 load case 的 distributed / point load。
7. 求 bending moment、shear、deflection、rotation 與 support reactions。
8. 再把 reactions 傳入 bracket / fastener / anchor design。
9. 另外檢查 serviceability、glass-edge relative movement 與 splice / sleeve local failure。

## Continuous beam 不等於所有樓板都 fixed

多跨 mullion 可以在若干支點形成 continuous-beam behavior，但「多跨」本身不代表：

- 每個 support 都固定轉角；
- 每個 splice 都傳遞完整彎矩；
- 每個 anchor 都限制垂直 thermal movement；
- 每一段都有相同 `EI`。

模型必須逐節點說明 restraint。

## Support DOF 應明示

至少應分別記錄：

- `Ux`：沿某 global axis 的 translation
- `Uy`
- `Uz`
- `Rx`：rotation
- `Ry`
- `Rz`

實際 2D beam model 可只取相關 DOF，但資料模型仍應避免用含糊的 `fixed / free` 文字掩蓋真正 constraint。

例如一個 curtain-wall anchor 可能：

- restraint façade-normal translation；
- restraint dead-load direction at one designated support；
- allow vertical thermal sliding at another support；
- provide little or no rotational restraint。

這和 ideal `fixed support` 不同。

## Joint labels are not mechanics

分析軟體中的 `free joint`、`release`、`hinge`、`slider` 等名稱只是 solver implementation。工程文件必須能回答：

> 到底是哪一個 DOF 被 release？哪一個 force / moment 仍能傳遞？

不得只保存軟體畫面上的 label，卻無法重建 structural boundary condition。

## Member stiffness

線彈性 beam analysis 的主要 flexural stiffness 為：

`EI`

但 `E` 與 `I` 來源都必須可追溯。

若某一段因 reinforcement、sleeve、splice、截面變化或 multi-part composite action 而 stiffness 改變，應分段建模；不能用整支 mullion 單一平均 `I` 掩蓋局部剛度變化。

## Loads

應由 [load-generation](../load-generation/README.md) 路由進入，保留：

- positive / negative wind load case
- tributary width / load shape
- point load / concentrated attachment load
- dead load when applicable
- other project-required actions

不要把所有 action 先合併成單一 UDL，除非能證明這種 envelope simplification 對所檢查 response 保守且適用。

## Reactions are outputs, not assumptions

對多跨 mullion，樓板 reaction 受到：

- span length
- support layout
- splice location
- joint release
- EI distribution
- load distribution

共同影響。

因此不得用：

`reaction = total load / number of anchors`

取代 continuous-beam analysis。

## Strength checks

取得 internal force 後，至少依實際 member / section model檢查：

- major-axis bending
- minor-axis bending
- biaxial interaction where applicable
- shear
- local section / extrusion failure
- splice / sleeve demand
- bracket / fastener / anchor reactions

若 mullion 是多件 extrusion，另依 [multi-part extrusion load sharing](multi-part-extrusion-load-sharing.md) 確認 composite-action assumption。

## Deflection checks

除了 global maximum deflection，還可能需要：

- span deflection
- cantilever-tip deflection
- displacement at glass support points
- differential displacement across a lite
- relative movement at splice / stack joint

對玻璃邊緣相容性應路由至 [glass-edge-relative-deflection](glass-edge-relative-deflection.md)，不要只用整支 mullion 最大位移做判斷。

## Sensitivity / bounding analysis

當 splice stiffness 或 rotational restraint 不確定時，推薦使用 engineering bounding cases：

- moment-release lower-bound model
- rigid / continuous upper-bound model
- validated semi-rigid model（若有 stiffness evidence）

但**不能只選其中較容易 PASS 的結果**。應比較：

- member moment
- deflection
- support reaction
- splice demand
- connection demand

因為不同 failure mode 的 governing boundary condition 可能不同。

## AI guard

AI 不得：

- 把跨樓層 mullion 默認成 single-span simply supported beam
- 把每個樓板 anchor 默認 fixed support
- 把 splice 默認 hinge 或 rigid
- 把 solver 中 `free joint` 解讀成所有 DOF 都自由
- 以總荷載平均分配 support reaction
- 忽略 splice / sleeve 前後的 EI 變化
- 在 boundary condition 不明時輸出 final PASS

若支承或 splice 模型缺失，回傳：

`structural_model_status = INCOMPLETE`

## Public-source routing

- 內政部建築研究所《帷幕牆系統結構耐風設計手冊》及其前身研究：要求先界定帷幕系統構件、風壓傳導機制，再分別分析直料、橫料與繫件。
- FGIA **AAMA CWM-19 Curtain Wall Manual**：現行 curtain-wall manual，用於一般 curtain-wall design principles / movement / anchorage / splice routing；不在本 repository 重製受版權保護內容。
- The Aluminum Association **Aluminum Design Manual 2020**：截至 2026-09-02 Aluminum Association 仍列示之 aluminum structural-design manual。

> 本頁保存的是 structural modeling logic，不代表任何特定 curtain-wall system 的 support、splice 或 stiffness model。