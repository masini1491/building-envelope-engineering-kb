---
title: "直料接頭／套筒（Splice／Sleeve）建模方法"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 直料接頭／套筒（Splice／Sleeve）建模方法

## 角色

帷幕牆直料 splice / sleeve 的功能可能同時涉及：

- erection tolerance
- thermal movement
- inter-story movement
- alignment
- shear transfer
- moment transfer
- axial load transfer
- local reinforcement

因此 `splice` 不是一種單一結構條件。工程模型必須明確定義它在各自由度與各 load case 下的 force-transfer behavior。

## 建議的 splice state

至少可使用：

- `moment_release`：不假設傳遞彎矩，但仍可能傳剪力／其他反力。
- `shear_transfer_only`：只建立特定方向剪力傳遞。
- `axial_sliding`：允許軸向相對滑移，但其他方向可能有 restraint。
- `full_continuity`：有充分證據支持完整 continuity。
- `semi_rigid`：以已驗證 rotational / translational stiffness 建模。
- `effective_properties_user_supplied`：直接使用已驗證等效接頭 stiffness。
- `unknown`：目前不能可靠判斷；模型不得自行假設。

上述狀態可組合，因為同一接頭在不同方向的行為可能不同。

## 不要用單一 hinge icon 代表整個接頭

一個 mullion splice 可能：

- 對 façade-normal bending 近似 moment release；
- 對 lateral translation 仍能由 sleeve / interlock 傳遞 shear；
- 對 vertical direction 允許 thermal sliding；
- 對 torsion 又有部分 restraint。

因此工程資料應以 DOF / force component 表示，而不是只存 `hinge=true`。

## 傳力問題

每個 splice 至少回答：

1. 能否傳 `N`（axial force）？
2. 能否傳 `Vx / Vy`（shear）？
3. 能否傳 `Mx / My / Mz`？
4. 是否允許某方向滑移？
5. 是否有 gap / clearance 在受力前需先閉合？
6. positive / negative pressure 行為是否相同？
7. 接頭 stiffness 是否隨位移、接觸或 fastener slip 改變？
8. sleeve / splice 是否會改變局部 `EI`？

若答案未知，應標 `INCOMPLETE`。

## Sleeve 作為補強

Sleeve 可能只負責 alignment，也可能在有限長度內提高局部 stiffness 或傳遞 interface force。

若 sleeve 被納入 flexural stiffness，至少應確認：

- sleeve material / E
- sleeve section properties
- overlap length
- contact / fastener arrangement
- composite-action assumption
- slip / clearance
- effective length over which stiffness is credited

不能因 sleeve 幾何上插入 mullion cavity 就自動把 sleeve `I` 加到整支 mullion。

## 局部連接需求

splice / sleeve 附近可能出現：

- fastener shear
- fastener tension due to eccentricity
- bearing
- screw pull-out / thread stripping
- local extrusion wall bending
- sleeve local bending
- contact / prying

因此 global beam model 若只用 ideal hinge / spring，仍需把該 joint force 回傳到 connection-level checks。

## 半剛性模型

若接頭有可驗證 rotational stiffness `kθ`，可使用 rotational spring 等方式建立 semi-rigid model。

同理 translational slip / bearing behavior 可用 `k`、gap/contact 或 nonlinear connector 模型表示。

但 spring stiffness 必須來自：

- calculation with validated mechanics
- component test
- product technical data
- calibrated FEA
- approved project/company engineering method

不得由 AI 任意猜一個 stiffness 以讓模型收斂。

## 位移相容性

若 splice 同時作為 movement joint，需另確認：

- required movement range
- available clearance
- seal / gasket engagement
- fastener slot / slip capability
- movement at design temperature range
- inter-story drift demand
- whether movement changes structural load path

「結構上可滑」與「實際 detail 有足夠 movement capacity」是兩個不同檢核。

## 界限案例

當接頭 stiffness 不確定，可比較：

- release model
- rigid model
- validated semi-rigid model（若有）

但要對各 response 分別找 governing case：

- member stress
- member deflection
- support reaction
- joint force
- glass-edge movement

不能只挑其中一個總體上較保守或較容易 PASS 的模型。

## 建議輸出

每個 splice record 至少輸出：

```yaml
splice:
  location: ...
  translational_dof:
    x: restrained | released | spring | gap_contact
    y: restrained | released | spring | gap_contact
    z: restrained | released | spring | gap_contact
  rotational_dof:
    x: restrained | released | spring
    y: restrained | released | spring
    z: restrained | released | spring
  axial_sliding: true | false | unknown
  stiffness_source: ...
  effective_stiffness_region: ...
  verification_status: confirmed | provisional | unknown
```

## AI 防呆

不得：

- `splice = hinge` 當作通用規則
- `sleeve = full reinforcement` 當作通用規則
- 只因有長孔就假設零摩擦自由滑動
- 忽略正負風壓下 contact state 可能不同
- 忽略 splice 附近 local fastener / extrusion failure
- 在 splice behavior 未定時輸出 final structural PASS

## 相關頁面

- [Continuous Mullion Analysis](continuous-mullion-analysis.md)
- [Multi-Part Extrusion Load Sharing](multi-part-extrusion-load-sharing.md)
- [Load Path / Anchor Reactions](../connections/load-path-and-anchor-reactions.md)
- [Fastener Group Analysis](../connections/fastener-group-analysis.md)
- [Local Extrusion Failure](../connections/local-extrusion-failure.md)

## 公開來源 routing

- FGIA **AAMA CWM-19 Curtain Wall Manual**：curtain-wall movement、anchorage、splice 等一般設計原則 routing。
- The Aluminum Association **Aluminum Design Manual 2020**：aluminum member / connection design routing。
- 內政部建築研究所《帷幕牆系統結構耐風設計手冊》：台灣帷幕系統、構件與 load-path routing。

> 本頁不宣稱任何 proprietary splice / sleeve detail 的等效 stiffness 或 moment capacity。