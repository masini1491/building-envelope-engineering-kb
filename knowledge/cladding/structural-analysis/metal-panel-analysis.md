---
title: "金屬面板結構分析"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 金屬面板結構分析

## 適用範圍

本頁處理 solid metal sheet / plate、折盒板與具周邊折邊之 façade panel 的結構分析。複合板、蜂巢板另需依其 sandwich construction 與產品資料處理。

## 荷載路徑優先

分析前先明確定義：

`pressure → panel skin → return / stiffener → connector → perimeter support → façade framing`

如果其中任一介面不清楚，不能只靠 panel skin FEA 宣稱整體系統 PASS。

## 幾何模型

至少保存：

- panel plan dimensions
- nominal / actual thickness
- folded returns / hems / ribs
- openings / penetrations
- stiffener locations
- attachment locations
- support lines / points
- local offsets / eccentricity

折邊若對剛度有貢獻，不應只建平板；反之若實際接頭允許相對滑移，也不能把所有折邊與補強視為完全剛接。

## 材料模型

至少保存：

- alloy / temper
- elastic modulus `E`
- Poisson ratio `ν`
- yield / design strength source when strength check is performed
- material status / edition / provenance

若資料不足，只可完成 elastic-response analysis，不得自動宣告 strength PASS。

## 分析輸出

至少分開檢視：

- out-of-plane deflection
- membrane / bending stress as applicable
- support / connector reactions
- local deformation near attachments
- stiffener demand
- folded-return demand

## 服務性與強度

面板最大位移可能控制視覺或接縫相容性；局部應力則可能控制材料強度。兩者的 acceptance criterion 來源可不同。

不要把：

`deflection PASS`

等同於：

`strength PASS`

也不要把 panel stress PASS 等同於 connector / stiffener / support PASS。

## 局部峰值

FEA 在以下位置常出現局部 peak：

- point restraint
- sharp corner
- zero-radius fold idealization
- concentrated load
- tied / rigid connection edge
- mesh transition

若 peak 隨 mesh refinement 持續增大，應先判斷 singularity / modeling artifact，再依適用 design method選擇合理的 stress extraction / averaging / local submodel；不得直接拿單一最高 node value 做結論。

## 挫屈／幾何非線性

薄金屬板可能受 local buckling、large deflection 與 membrane action 影響。若線性小變形 plate analysis 已接近幾何非線性範圍，應評估是否需要：

- geometric nonlinearity
- initial imperfection
- buckling analysis
- material nonlinearity
- full-size test

不能把線性 FEA 的低應力結果當成已排除 buckling。

## 平整度／oil canning 防呆

結構分析中的 elastic deflection 不等於完成面 oil canning prediction。完成面視覺仍受 residual stress、leveling、fabrication、thermal cycle、installation restraint 等影響。

## AI 防呆

AI 不得：

- 把 panel 當成只有 skin、忽略 folded return / stiffener / connector
- 以單一 FEA contour 圖宣告系統 PASS
- 將 peak node stress 不加判讀直接當 governing stress
- 在 connection assumption 不明時假設 full composite
- 把 linear static analysis 當成已驗證 buckling / post-buckling
- 將非公開專案的實際 panel geometry 寫進 public KB

## 相關頁面

- [Stiffener Analysis](stiffener-analysis.md)
- [Panel-to-Stiffener Connection](panel-to-stiffener-connection.md)
- [Plate / Shell FEA Modeling](plate-fea-modeling.md)
- [Aluminum Panel Flatness and Oil Canning](../../engineering-notes/aluminum-panel-flatness-and-oil-canning.md)

> 本頁提供可重用的 engineering workflow，不提供固定 panel thickness、stiffener spacing 或 allowable value。