---
title: "焊道群分析方法"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 焊道群分析方法

## 角色

帷幕牆鋼 bracket、angle、channel、embedded plate 或其他連接件，常以多段 weld 形成 weld group。當外力對焊群形心具有偏心時，不能只用 `總剪力 ÷ 總焊長`；必須同時考慮 direct force 與由 moment / torsion 引起的附加焊道應力。

本頁整理一般 weld-group mechanics。實際 strength 必須依適用鋼材／鋁材焊接規範與 project design basis；不得由本頁直接推導固定 allowable。

## 先區分兩個層次

### 1. 焊道群力學

回答「這一組焊道在目前幾何與外力下，各位置 demand 多大」。

### 2. 焊道／母材強度

回答「這個 demand 是否小於適用規範允許的 weld metal / base metal / HAZ / connected-part capacity」。

兩者不能混為一談。

## 角焊道有效喉厚

對 ideal equal-leg 45° fillet weld，幾何 effective throat 常表達為：

`t_e = s sin 45° ≈ 0.707 s`

其中 `s` 為 weld leg size。

這只是幾何關係，不是 weld allowable strength。若 weld geometry、root condition 或 applicable code 定義不同，應依該規範。

## 任意焊道群表示方式

建議把焊群建模為一組 line segments。每一段至少保存：

- start / end coordinates
- effective throat
- weld type
- length
- material / electrode or filler system

由 line geometry 建立 weld-group centroid、effective area 與幾何性質。

## 焊道群有效面積

對 line-weld model：

`A_w = Σ(t_e L_i)`

其中 `L_i` 為第 i 段有效焊長。

若實際 code 對 effective length 有扣除、end return、minimum length 等要求，必須依適用規範調整，不能只用圖面 nominal length。

## 形心與截面性質

應先以 effective weld area weighting 求 group centroid，再建立：

- `I_x`
- `I_y`
- `I_xy` when needed
- `J = I_x + I_y` for in-plane polar-type elastic group analysis

若 weld group 不對稱、座標軸不是 principal axes，不能忽略 product of inertia 對應的軸轉換問題。

## 直接力

對 through-centroid 的 force components，可先以有效 weld area 分配 direct stress / line force demand。

例如平均 direct shear magnitude 的概念：

`τ_direct = V / A_w`

但對具有方向性的 vector problem，應保留各 force component，不宜過早化成單一 scalar。

## 彎矩／扭矩效應

外力若對 weld-group centroid 有 eccentricity，應先換算成 moment：

`M = r × F`

再依適用 elastic weld-group method 求各 critical point 的 moment-induced demand。

對 in-plane torsional moment，常見 elastic line-group形式具有：

`q_m ∝ M r / J`

方向為 tangential，再與 direct line force vector 合成。

對 out-of-plane bending，則需依 weld-group section properties 評估由 `M_x / M_y` 引起的 normal / shear demand，具體形式取決於採用的 design model。

## 臨界點檢核

對不對稱 weld group，最大 demand 不一定在最長焊道或幾何最外角。應至少檢查：

- 距 centroid 最遠位置
- 最大 moment-induced component 位置
- direct 與 moment component 同向疊加位置
- geometry discontinuity / weld termination
- code-specified critical section

## 合成需求

不同方向 stress / line force 的組合方式必須與採用的 weld design method一致。

AI 不得看到兩個分量就自行使用：

`sqrt(τ² + σ²)`

或任意 von-Mises-like expression 宣告 PASS；必須先確認 applicable code 對 weld strength、stress direction 與 interaction 的定義。

## 母材／被連接構件

Weld metal PASS 仍不足以完成 connection design。還要依實際節點檢查：

- base metal yielding / rupture
- local plate bending
- block shear / tear-out where applicable
- HAZ where applicable
- connected angle / channel / bracket section
- eccentricity causing prying / local deformation

## 鋼材與鋁材 routing

### 鋼結構焊接

鋼結構焊接應回到適用的 AISC / AWS steel design and welding basis。不得因 filler metal 標示為 E70XX 就自動生成所有 allowable values。

### 鋁合金焊接

鋁合金 weld / HAZ 必須使用 aluminum-specific design basis。不能把 steel fillet-weld strength equations直接套在 aluminum；weld heat affected region 對 temper / strength 的影響尤其需要另外處理。

## 建議計算輸出

至少輸出：

1. weld segment geometry
2. effective throat / effective length basis
3. weld-group centroid
4. 依適用性列出 `A_w / I_x / I_y / I_xy / J`
5. applied `Fx / Fy / Fz / Mx / My / Mz`
6. direct components
7. moment-induced components
8. critical point
9. resultant demand according to applicable method
10. weld strength source
11. base-metal / connected-part checks
12. assumptions and excluded failure modes

## AI 防呆

不得：

- 用 `V/(0.707 s L)` 取代所有 eccentric weld-group analysis
- 把 `0.707s` 當 allowable strength
- 只因 E70XX 名稱就推算 weld design strength
- 把 steel weld equation 用到 aluminum
- 只檢查 weld metal 而漏掉 connected plate / bracket / HAZ
- 無 weld geometry 仍宣稱完成 weld-group calculation
- 直接把非公開專案中的焊道尺寸或配置寫進 public KB

## 公開來源 routing

- AISC current Specification for Structural Steel Buildings：鋼構 connection / weld strength design routing。
- AWS D1.1/D1.1M：Structural Welding Code—Steel。
- AWS D1.2/D1.2M：Structural Welding Code—Aluminum。
- The Aluminum Association, Aluminum Design Manual：aluminum member / connection / welded-region design routing。

版本與具體 equation 在正式設計前需重新確認 current edition；本頁不重製受版權保護標準內容。

> 本頁保留的是可泛化的 weld-group mechanics，而不是任何特定工程計算書的配置、尺寸、荷載或 acceptance value。