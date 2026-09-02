---
title: "後置式機械錨栓（Post-installed Mechanical Anchor）設計方法"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
---

# 後置式機械錨栓（Post-installed Mechanical Anchor）設計方法

本頁整理帷幕牆與建築外殼常見 **post-installed mechanical anchor**（包含 expansion / screw / undercut 類型）的設計與審查方法。

本頁不提供某一品牌或型號的通用 resistance。產品是否合格、可用於 cracked concrete、seismic、特定 embedment / edge / spacing / installation condition，必須回到 applicable qualification / evaluation evidence。

現行標準版本由 [`anchor-standards-baseline.md`](anchor-standards-baseline.md) 維護。

## 資格認證（Qualification）與設計（Design）必須分開

後置式機械錨栓至少有兩個不同問題：

1. **Qualification / evaluation**：這個產品在什麼條件下可被視為合格 anchor？
2. **Design**：在本專案實際 concrete / geometry / load condition 下，它是否有足夠 resistance？

目前 ACI routing：

- **ACI CODE-355.2-24**：post-installed mechanical anchors 的 qualification requirements；
- **ACI CODE-318-25**：structural concrete design code，包含 mechanical / adhesive anchoring to concrete 的設計要求。

因此不得把 `ACI 355.2 qualification PASS` 當成 project anchor design PASS。

同樣地，manufacturer software 或 ESR / ETA 中的某一 capacity 也不能脫離其適用條件直接引用。

## 機械錨栓（Mechanical anchor）與黏著式錨栓（adhesive anchor）不可混用

Mechanical post-installed anchor 與 adhesive anchor 不是同一 qualification family。

- mechanical anchor：ACI CODE-355.2-24；
- adhesive anchor：ACI CODE-355.4-24。

若是 post-installed reinforcing bar system，也應辨識其專屬 qualification routing，不得因外觀像植筋就任意套 adhesive-anchor design assumptions。

本頁只處理 mechanical anchor；adhesive anchor 後續可另建 canonical page。

## 最低必要輸入

若計算資料只寫：

`M10 expansion anchor × 2`

應直接判定 `INCOMPLETE`。

至少需要以下資料。

### 產品與 qualification

- manufacturer；
- exact product family / type；
- nominal diameter；
- material / corrosion class；
- applicable evaluation / qualification document；
- evaluation document edition / issue date；
- design method / governing code；
- cracked / uncracked approval；
- seismic qualification if required；
- permitted embedment variants；
- permitted installation conditions；
- installation-sensitivity / anchor category treatment where governing evidence uses it。

### 混凝土／基材

- concrete strength；
- cracked / uncracked design condition；
- concrete member thickness；
- edge distances；
- anchor spacing；
- reinforcement / supplementary reinforcement condition where governing method uses it；
- opening / recess / step / edge geometry；
- lightweight / normal-weight status if relevant to governing method。

### 安裝

- drilled-hole method；
- hole diameter / tolerance；
- effective embedment `hef`；
- nominal embedment / installation depth if separately defined；
- installation torque where applicable；
- dry / wet / submerged / temperature conditions where applicable；
- hole cleaning where applicable；
- annular gap / filling set where applicable；
- installation inspection / proof testing requirements。

### 錨板／支架

- anchor coordinates；
- base plate / bracket geometry；
- hole / slot geometry；
- stand-off / grout / spacer condition；
- plate thickness；
- plate rigidity / flexibility assumption；
- load application point。

### 荷載

- `N / Vx / Vy`；
- `Mx / My / Mz` where relevant；
- load combinations；
- load factors；
- seismic / sustained / other applicable load condition；
- source / provenance of façade reaction。

## 錨栓群受力分配（Anchor group force distribution）

不得直接把 total reaction 除以 anchor 數量，除非已證明荷載分配確實均勻。

至少應考慮：

- anchor coordinates；
- group centroid；
- load eccentricity；
- plate rigidity / flexibility；
- tension distribution；
- in-plane shear / torsion；
- slot / slip / bearing condition；
- prying or bracket deformation；
- governing individual anchor demand。

若 manufacturer software 假設 rigid anchor plate，而實際 bracket / plate 明顯柔弱，應另外檢查此 model assumption 對 anchor force distribution 是否仍合理。

## 群組破壞面／幾何效應

Concrete breakout / edge failure 等 group checks 不能只用「單根 resistance × anchor 數量」。

若 governing method 使用 projected failure area / group area，至少保存：

- single-anchor reference area；
- actual group projected area；
- anchor spacing；
- edge-distance truncation；
- concrete member thickness / opening / recess 對 failure surface 的影響；
- eccentricity modifier；
- cracked-concrete treatment；
- supplementary reinforcement 是否被計入，以及其配置與來源。

若這些 geometry 無法重建，就不能只接受 manufacturer report 的最終 utilization。

## 拉力 failure modes

依 governing code 與產品 evaluation，至少考慮適用的：

- anchor steel tension failure；
- concrete breakout / cone failure；
- pullout；
- side-face blowout；
- concrete splitting where applicable；
- 其他產品 qualification 明確要求的 tension failure mode。

對每一 failure mode，都要保存：

- characteristic / nominal resistance source；
- applicable geometry modifiers；
- edge / spacing / eccentricity effects；
- cracked-concrete treatment；
- resistance / strength-reduction factor；
- final design resistance；
- governing status。

只報一個「容許拉力」而沒有上述 scope，通常不足以 review。

## 剪力 failure modes

至少考慮適用的：

- anchor steel shear failure；
- concrete edge breakout；
- pryout；
- concrete splitting / edge interaction where applicable；
- shear direction / edge orientation effect；
- plate / bracket bearing and local deformation。

Edge distance 不只是幾何註記；它可能直接改變 concrete edge failure resistance。

## 拉剪組合

若 tension / shear 同時存在，必須使用 governing design method 對應的 interaction rule。

不得自行使用：

- 線性相加；
- 平方和；
- 任意 exponent；
- 舊專案 interaction equation；

除非能回到本次 governing source。

## 裂縫／非裂縫混凝土（Cracked／Uncracked concrete）

若產品 qualification 或 design method 有 cracked / uncracked 區分，專案計算必須明確指定採用哪一個條件與理由。

不得因 uncracked resistance 較高，就在沒有 structural basis 的情況下自行選 uncracked concrete。

如果 cracked status 無法確定，而它可能改變 resistance / qualification，至少應標 `INCOMPLETE` 或採經證明的 conservative bounding case。

## 安裝敏感性與 qualification

後置式 anchor 的 resistance 可能對 installation process 敏感。

Review 不應只問「有沒有照說明書安裝」，還要確認：

- qualification 是否涵蓋實際 drilling / setting method；
- required torque / embedment / hole tolerance；
- installer-sensitive steps；
- 現場是否有 inspection / proof-test requirement；
- calculation 中是否使用與 product qualification 對應的 resistance / factor treatment。

不得把歷史教材中的 anchor category 或舊版 installation factor 直接帶入 current design；如 governing method 有 category / sensitivity concept，應以本次 exact product evaluation 與 current method 為準。

## 耐震資格（Seismic qualification）

若 anchor 屬於需要承受地震 demand 的 connection，除了計算地震力外，還要確認 anchor product 本身的 seismic qualification / category / installation restrictions 是否符合 project governing requirement。

**有 seismic load calculation ≠ anchor automatically seismic-qualified。**

## 製造商軟體（Manufacturer software）／ESR／ETA 的定位

Manufacturer software 很適合：

- 保存產品 identity；
- geometry；
- concrete condition；
- anchor group；
- load combination；
- failure-mode utilization；
- evaluation-document routing。

但軟體輸出的 `OK` 仍然只對它實際建模的 scope 有效。

審查時至少確認：

1. software version；
2. product / evaluation document；
3. governing design method；
4. input geometry 是否與現場一致；
5. cracked status；
6. installation condition；
7. plate-rigidity assumption；
8. load input 是否與 façade calculation 對得上；
9. warnings / exclusions；
10. output 是否涵蓋所有 required failure modes；
11. group projected-area / edge / spacing treatment 是否可追溯。

**Manufacturer software PASS ≠ façade connection PASS。**

外側 bracket / plate / weld / bolt / slot / local aluminum / load path 仍須各自檢查。

## 現場施工與驗證

後置式 anchor 對施工品質通常比 cast-in anchor 更敏感。

可能需要依 project specification / evaluation / authority 要求確認：

- drilling method；
- embedment；
- installation torque；
- hole cleaning；
- edge damage；
- concrete condition；
- anchor setting inspection；
- proof / pull testing；
- inspection sampling；
- failed-anchor disposition。

不得把 installation requirement 當成純施工文件而從 structural review 中刪掉，因為某些條件直接影響 qualification / resistance。

## 係數稽核（Factor audit）

Post-installed anchor calculation 常出現多層 factors，例如：

- load factor；
- material / steel resistance factor；
- concrete resistance factor；
- installation / anchor-category factor；
- cracked-concrete treatment；
- edge / spacing / eccentricity modifiers；
- reinforcement-related modifiers where applicable；
- seismic modifiers；
- combined-load exponent / threshold。

所有 factor 都必須具名並能回到 governing source。

若計算書只顯示最後 utilization，而中間 factor 無法追溯，不能只因 utilization `< 1.0` 判 PASS。

依 [`../structural-design/review/design-factor-and-hidden-multiplier-audit.md`](../structural-design/review/design-factor-and-hidden-multiplier-audit.md) 執行 factor ledger。

## 與 cast-in embedded plate 的分界

Cast-in 與 post-installed anchor 雖然都可能檢查 concrete breakout / steel failure / edge effect，但不可因此共用所有公式或 factor。

差異可能包括：

- qualification route；
- anchor load-transfer mechanism；
- installation dependency；
- pullout mechanism；
- cracked-concrete behavior；
- seismic qualification；
- applicable resistance factor；
- product-specific limits。

Cast-in embedded plate 方法見 [`cast-in-embedded-plate-design.md`](cast-in-embedded-plate-design.md)。

## 審查狀態建議

### 通過（`PASS`）

只有在 product / qualification / geometry / substrate / loads / failure modes / factors / installation scope 都能追溯，group projected-area treatment 可重建，且 connection 的外側 plate / bracket / weld / bolt checks 也已完成時，才能對明確 scope 給 PASS。

### 警告（`WARNING`）

例如：

- proof-test / inspection record 尚待施工階段補件；
- plate-flexibility sensitivity 尚待進一步確認，但 bounding evidence 顯示不會控制；
- product evaluation 有非 governing warning，已清楚記錄。

### 不完整（`INCOMPLETE`）

例如：

- 只知道 anchor size，不知道產品；
- evaluation report / design method 不明；
- cracked status 不明；
- edge / spacing / embedment / concrete thickness 缺失；
- group projected failure area 無法重建；
- supplementary reinforcement 被用於 resistance enhancement，但配置／來源不明；
- installation condition 缺失；
- manufacturer report 的 load 無法與 façade reaction 對上；
- factor provenance 不明；
- software 只給 `OK`，但無法重建 input / failure-mode scope。

## 主要公開來源

- ACI CODE-318-25 — Building Code for Structural Concrete。
- ACI CODE-355.2-24 — Post-Installed Mechanical Anchors in Concrete—Qualification Requirements and Commentary。
- ICC-ES / manufacturer evaluation documentation where applicable。
- Alternative ETA / EAD route only when the project accepts that evaluation system and the exact product / edition / design method are established。

> 本頁只定義 post-installed mechanical-anchor review methodology；不得把任何品牌型錄、舊計算書、舊 ETAG / ETA output、歷史 safety factor 或 software default 當成本 KB 的 universal design value。