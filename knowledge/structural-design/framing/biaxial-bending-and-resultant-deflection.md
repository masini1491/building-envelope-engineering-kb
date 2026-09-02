---
title: "帷幕 Framing 雙軸彎曲與合成撓度"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 帷幕 Framing 雙軸彎曲與合成撓度

## 適用情境

Curtain-wall mullion / jamb / corner member / feature extrusion 不一定只承受 façade-normal bending。以下情況常需要 X / Y 兩軸分開分析：

- corner mullion
- side-return framing
- projecting fin / feature
- eccentric connection
- offset glass / panel load
- maintenance attachment
- asymmetric composite framing

## Axis discipline

首先必須明確定義 CAD section axes 與 physical load direction。不能靠 `Ix > Iy` 就把 `x` 自動稱為 strong axis，也不能假設不同 CAD / FEA 軟體的軸向命名一致。

至少保存：

- section x/y axes
- façade-normal direction
- gravity direction
- applied load components
- `Ix / Iy / Sx+/Sx-/Sy+/Sy-`

對非對稱截面，正負 extreme-fiber section modulus 可能不同。

## Independent-axis linear analysis

在線性小變形且 principal / decoupled axes 合理的情況，可分別求：

- `M_x`, `σ_x`, `δ_x`
- `M_y`, `σ_y`, `δ_y`

若 axes 非 principal 或 `Ixy` 不可忽略，應採 unsymmetrical bending / transformed principal-axis method，而不是硬把 X/Y 當完全獨立。

## Combined stress

組合應力的 acceptance equation 必須依材料設計標準與 stress state 決定。

AI 不得自行採用：

`σx/Fx + σy/Fy <= 1`

或任意平方和，除非該 interaction relation 有適用 design basis。

對簡單 elastic normal stress，可先計算各 load component 在各 extreme fiber 的 stress，再依 governing design specification 做 interaction。

## Resultant deflection

若 `δx` 與 `δy` 是互相正交方向的 displacement component，而且工程問題關心 total spatial displacement magnitude，可計算：

`δ_resultant = sqrt(δx² + δy²)`

但 serviceability criterion 可能只限制某特定方向，例如：

- glass edge normal displacement
- sealant joint movement
- visual façade-normal deflection
- clearance in a slot

因此不能永遠用 resultant magnitude 與單軸 criterion 比較。

## Corner / feature framing

對轉角或突出造型構件，要特別確認：

1. 哪個面板把風荷載傳到哪個軸
2. two façade directions 是否同時作用／如何組合
3. composite profiles 是否在兩軸都有相同 effective action
4. connection stiffness / eccentricity 是否引入 torsion
5. glass-edge relative displacement 是否控制 serviceability

## Torsion guard

Biaxial bending 不等於 torsion。若 load line 不通過 shear center、connection 偏心或 framing geometry 造成 twist，還要另外處理 torsional response；不能只靠 `Mx + My` 完成設計。

## Do not assume

- 不得用 `Ix > Iy` 自動命名 strong / weak axis。
- 不得把非對稱截面 `Sx+` 與 `Sx-` 當相同。
- 不得在 `Ixy` 明顯時仍硬拆成獨立 X/Y bending。
- 不得把 resultant deflection 當所有 gasket / glass / sealant criterion 的唯一指標。
- 不得忽略 torsion。

## Routing

- [Mullion / Transom Design Baseline](mullion-transom-design-baseline.md)
- [Multi-Part Extrusion Load Sharing](multi-part-extrusion-load-sharing.md)
- [Glass-Edge Relative Deflection](glass-edge-relative-deflection.md)
- repository `/schemas/section-properties.schema.json`

> 本頁定義分析框架，不提供 project-specific load combination 或固定 interaction equation。