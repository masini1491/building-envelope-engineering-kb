---
title: "多件鋁擠型共同作用與荷載分配"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 多件鋁擠型共同作用與荷載分配

## 角色

帷幕牆 mullion / transom 常由 male / female profile、interlock、sleeve、reinforcement、snap-on feature 或其他多件擠型共同組成。工程計算最容易出錯的地方之一，是在沒有證據時直接把各構件的 `I`、`S` 或強度相加，等同假設所有構件具有 full composite action。

本頁定義多件擠型的建模 guardrail；不提供任何專案專屬截面、尺寸或 allowable stress。

## 必須先宣告 composite-action state

至少使用下列其中一種狀態：

- `independent`：各構件不假設共同彎曲，依實際 load path 分別承載。
- `full_composite`：有充分證據支持共同曲率／共同變形，可依完整組合截面分析。
- `effective_properties_user_supplied`：直接採用已驗證的 effective `EA / EI / section properties`。
- `company_validated_rule`：採用已有試驗、長期設計驗證或正式內部程序支持的工程模型。
- `unknown`：目前無法證明 load transfer；不得自動假設 full composite。

`unknown` 應視為 `INCOMPLETE`，而不是由 AI 自行選一個有利假設。

## Full composite 需要什麼證據

只有當構件間能可靠傳遞使其維持相容變形所需的 longitudinal shear / contact force 時，才可考慮 full composite。可能的證據包括：

- 連續且可驗證的機械連結
- 經計算證明足以傳遞介面剪力的 bolts / screws / welds / structural connection
- 經試驗或認證證明的 interlock / crimp / bonded interface
- 已驗證的產品或公司設計方法

單純「兩支鋁料互相卡在一起」、「施工後不易分開」或「CAD 看起來接觸」都不足以證明 full composite action。

## 截面性質力學

若確定為 full composite，必須先建立共同 reference axis / neutral axis；不能只把每一支 profile 對自己 centroid 的 `I` 無條件相加。

同材質、共同曲率的理想組合截面，其平行軸概念為：

`I_total = Σ (I_i,c + A_i d_i²)`

其中：

- `I_i,c`：第 i 構件對自身 centroid axis 的 second moment of area
- `A_i`：第 i 構件面積
- `d_i`：該 centroid 到共同 neutral axis 的距離

若材料彈性模數不同，應改以 `EA / EI` 或 transformed-section / stiffness 方法處理，不能只比較幾何 `I`。

## 相對剛度荷載分配

在**已經證明構件具有 compatible curvature** 的前提下，才可討論依 flexural-stiffness contribution 分配彎矩。

對真正的 full-composite built-up section，每一構件的 stiffness contribution 必須建立在**共同 reference / neutral axis** 上，而不是直接拿各 profile 對自身 centroid 的 `I_i,c` 做比例分配。概念上可寫成：

`(EI)_i,contribution = E_i × (I_i,c + A_i d_i²)`

再以：

`M_i = M_total × (EI)_i,contribution / Σ(EI)_j,contribution`

理解各 constituent 對共同曲率下彎曲剛度的貢獻。

若材料 `E` 相同，仍必須使用對共同 axis 的 section-property contribution；**不能簡化成各 profile 自身 centroidal `I` 的比例，除非幾何上它們恰好共用同一 centroid / reference axis。**

若分析對象不是 full-composite built-up section，而是多個獨立 member 因 connector / frame constraint 形成相容變形，則應另依該 structural model 的 member stiffness 與 connector mechanics 求 load sharing，不應把本段 built-up-section 關係直接套用。

這些公式只是在**共同作用已經由 load-transfer evidence 建立之後**描述 stiffness distribution；它們本身不能證明 composite action 存在。

## 公／母帷幕鋁擠型防呆

對 male / female mullion 或類似 interlocking extrusion，至少要另外確認：

1. interlock 是否能在正、負風壓方向都維持所假設的 load transfer
2. contact / clearance 是否造成單向接觸或 initial slip
3. screws / clips / splice 是否限制 relative slip
4. thermal movement 是否要求某方向刻意滑動
5. local wall deformation 是否會先於整體截面共同作用失效
6. profile 中斷、splice、anchor location 是否改變 effective composite length

因此「某一跨距可視為 composite」不代表整支 mullion 每個位置都可使用同一組 effective section properties。

## 獨立／部分共同作用

若介面不能可靠傳遞共同作用所需的 shear，應：

- 依實際 load path 分別求各 profile 的 force / moment；或
- 使用經驗證的 effective stiffness；或
- 建立 contact / connector / slip model；或
- 對 bounding cases 分別分析，例如 `independent` 與合理的 upper-bound composite model。

不得用「取兩種結果中較安全的一個」取代對 load path 的判斷，因為強度、撓度與 connection reaction 的 governing case 可能不同。

## 應力／撓度檢核

多件 extrusion 分析至少應檢查：

- global flexural stress
- major / minor axis bending
- resultant or biaxial deflection when applicable
- interface / connector force
- local bearing / wall bending
- splice / sleeve region
- discontinuity near anchor / transom connection
- glass edge relative displacement / serviceability compatibility

## AI 防呆

AI 不得：

- 看到 male + female profile 就自動 `I_total = I_male + I_female`
- 以幾何接觸直接宣稱 full composite
- 用各 profile 自身 centroidal `I` 比例冒充 full-composite stiffness contribution
- 用某一份既有計算書的 stiffness-sharing 方法當作所有 curtain wall system 的 universal rule
- 在缺少 interface force-transfer evidence 時輸出 final PASS

若 composite behavior 未定，應明確輸出：

`composite_action = unknown → structural result incomplete`

## Public sources / routing

- The Aluminum Association, **Aluminum Design Manual 2020**：鋁結構 strength / member design 的現行公開出版資訊可由 Aluminum Association Standards / Bookstore 查證。
- 內政部建築研究所《帷幕牆系統結構耐風設計手冊》：作為台灣帷幕 framing / load-path 的總體 routing。
- 實際 interface / interlock / fastener capacity 仍須依適用產品資料、現行規範與 project-approved design basis。

> 本頁中的 stiffness / section-property 公式是一般結構力學框架，不代表任何特定 proprietary curtain-wall system 已證明 full composite action。