---
title: "帷幕牆背撐材／次結構支撐設計（Back Bracing / Secondary Support）"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
---

# 帷幕牆背撐材／次結構支撐設計（Back Bracing / Secondary Support）

本頁處理帷幕固定反力由 back brace / secondary steel 傳至主結構的設計方法。

## 核心原則

背撐設計不是只驗一支角鋼的軸力。

完整 system 至少包含：

`façade support reaction`
→ `brace geometry`
→ `brace member force / stability`
→ `brace-end connection`
→ `supporting steel / slab interface`
→ `primary structure`

任何一層都可能 governing。

## 必要輸入

至少確認：

- façade reaction magnitude / direction；
- support spacing / tributary meaning；
- brace angle；
- brace clear length / effective length；
- section / material；
- end restraint；
- connection eccentricity；
- upper / lower support geometry；
- receiving beam / slab / column geometry；
- movement / tolerance requirement；
- load cases / combinations；
- revision / source provenance。

## 構件本體

依 brace force direction 與 model，可能需要檢查：

- axial tension；
- axial compression；
- global buckling；
- slenderness；
- flexure from eccentricity；
- combined axial + bending；
- local section behaviour；
- connection flexibility effects。

不得使用固定角鋼尺寸表取代 actual length / force / support model。

## 背撐角度與力放大（Brace angle）

斜撐角度會改變 brace axial force 與端部 reaction。

若 horizontal reaction 由斜撐分解承擔，brace 越平，通常 axial demand 越大；實際 relation 應由清楚的 free-body diagram / structural model 推導。

因此不能只比 horizontal span 或 height 就直接選固定型號。

## 上下端連接

至少檢查適用的：

- bolt / high-strength bolt；
- weld group；
- plate bending；
- bearing；
- tear-out；
- local steel / aluminum deformation；
- anchor if connected to concrete；
- prying / eccentricity。

Routing：

- [`../connections/fastener-group-analysis.md`](../connections/fastener-group-analysis.md)
- [`../connections/weld-group-analysis.md`](../connections/weld-group-analysis.md)
- [`../../anchors/anchor-standards-baseline.md`](../../anchors/anchor-standards-baseline.md)

## 支承構件局部效應（Supporting member local effects）

Back brace 把 concentrated / eccentric load 導入 receiving steel 時，除了 primary member global strength，還可能需要檢查：

- beam torsion；
- flange local bending；
- web local yielding / crippling / buckling；
- stiffener requirement；
- load introduction plate；
- weld / bolt local transfer。

詳見 [`supporting-steel-local-effects.md`](supporting-steel-local-effects.md)。

## 位移與施工相容性

背撐不可只看 strength。

還應確認：

- 是否限制原本應允許的 thermal movement；
- 是否限制 story drift / stack-joint movement；
- slot / sliding direction 是否仍有效；
- structure tolerance 是否能吸收；
- fabrication / erection tolerance 是否能吸收；
- 與 steel SHOP DWG / deck / MEP / existing bracing 是否衝突；
- 工具是否可施工／鎖固／焊接／檢查。

`strength PASS ≠ movement / constructability PASS`。

## 責任分界（Responsibility boundary）

若帷幕廠負責 back brace，但 primary beam reinforcement 由主結構技師負責，必須明確切出 interface。

例如：

`curtain wall`
→ `fixing`
→ `back brace`
→ `brace end plate`
→ **DESIGN INTERFACE**
→ `primary beam / stiffener`

詳見 [`secondary-support-interface-and-responsibility.md`](secondary-support-interface-and-responsibility.md)。

## 不可推論事項

- `brace member PASS = whole secondary-support system PASS`：錯誤。
- `brace axial force = façade reaction`：不一定，需依幾何分解。
- `短一點就一定安全`：不完整，仍受 connection / local effects / angle 影響。
- `加 stiffener 一定保守`：不一定，可能改變 load path / stiffness / movement。
- `主梁很大支撐點就不需檢查 local effect`：錯誤。

> 本頁不提供 universal brace size、angle limit、slenderness limit、stiffener threshold 或 connection allowable；所有數值須回 governing code / project design basis。