---
title: "預埋鋼板／Cast-in Anchor 結構設計方法"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
---

# 預埋鋼板／Cast-in Anchor 結構設計方法

本頁整理帷幕牆與建築外殼常見 **cast-in embedded plate** 的結構審查方法。重點不是提供單一通用公式，而是確保 façade reaction 能一路追溯到鋼板、錨定構件、焊接／鋼筋連接與混凝土中的完整 failure-mode coverage。

現行標準版本與 anchor 類型 routing 由 [`anchor-standards-baseline.md`](anchor-standards-baseline.md) 維護；本頁不另建立互相衝突的 current-edition snapshot。

## 核心原則

**預埋件 PASS 不等於錨筋或剪力釘 PASS。**

完整 load path 至少應拆成：

`façade reaction`
→ `bracket / bolt / weld`
→ `embedded plate`
→ `headed stud / deformed bar / hooked bar / cast-in channel`
→ `concrete / reinforcement`

其中任一層都可能 governing。

## 先辨識預埋型式

不得把所有預埋鋼板都視為相同 anchor model。至少區分：

- welded headed stud / headed anchor；
- straight deformed reinforcing bar welded or otherwise connected to plate；
- hooked reinforcing bar；
- proprietary cast-in anchor channel；
- cast-in anchor bolt / rod；
- 多種錨定構件共同工作的混合系統。

不同型式可能具有不同的 qualification、development、welding、anchor-to-concrete 與 detailing requirements。

若型式不明，結構檢核應為 `INCOMPLETE`。

## 必要輸入

建立 cast-in embedded-plate model 前，至少應確認：

### 荷載與反力

- tension / compression；
- shear in each relevant direction；
- `Mx / My / Mz` 或等效偏心；
- dead / wind / seismic / maintenance 等 load case；
- load combination 與 factor provenance；
- reaction point 相對於 plate / anchor group 的位置。

### 鋼板與連接

- plate geometry / thickness；
- steel grade / condition；
- bracket bearing area；
- weld geometry / electrode or process basis；
- bolt / slot / hole geometry；
- plate 是否足以視為 rigid，以及此假設的依據。

### 錨定構件

- anchor family；
- diameter / area；
- quantity；
- coordinates / spacing；
- embedment / development geometry；
- head / hook / bar geometry；
- steel grade；
- anchor-to-plate weld / connection detail。

### 混凝土／基材

- concrete strength；
- member thickness；
- edge distances；
- cracked / uncracked design basis（若 governing method 有區分）；
- reinforcement geometry where relevant；
- supplementary reinforcement 是否被 governing method 計入；
- actual recess / step / edge / opening geometry that may truncate a breakout surface。

缺少可能影響 governing resistance 的幾何或材料資料時，不得以「標準預埋件」補假設後直接 PASS。

## 錨栓對混凝土（Anchor-to-concrete）檢核

依 anchor type、load direction 與 governing code，至少考慮適用的 failure modes。

### 拉力方向

可能包括：

- anchor steel tension failure；
- concrete breakout / cone failure；
- pullout / bearing-related failure；
- side-face blowout；
- concrete splitting where applicable；
- reinforcement / development failure；
- anchor-to-plate weld failure。

不是每種 anchor 都使用完全相同的 failure mode 或係數。若某 failure mode 被判定 `NOT_APPLICABLE`，必須保存理由。

### 剪力方向

可能包括：

- anchor steel shear failure；
- concrete edge breakout；
- pryout；
- concrete splitting / edge interaction where applicable；
- local bearing / plate interaction；
- anchor-to-plate weld failure。

### 拉剪組合

不得只因 tension 與 shear 各自小於 individual resistance 就自動 PASS。

若 governing code 對 combined tension / shear 有 interaction requirement，必須使用對應 method；interaction formula、exponent、threshold 與 factor 不得從其他 anchor system 或舊專案複製。

## 錨栓群組（Anchor group）、投影面與偏心

預埋件通常不是單一 anchor。

應保存：

- 每個 anchor coordinate；
- anchor-group centroid；
- applied load point；
- eccentricity；
- anchor-group force distribution method；
- plate rigidity / flexibility assumption；
- governing anchor demand；
- governing method 所使用的 projected breakout area / group area；
- edge、spacing、member thickness、opening 或相鄰 anchor 對 failure surface 的截斷／重疊影響。

不得把「單根 anchor capacity × anchor 數量」當成 group capacity，除非 governing method 明確允許且 geometry 條件確實成立。

若 supplementary reinforcement 被用來改變 concrete failure treatment，必須保存 reinforcement geometry、development / anchorage、適用條件與 governing source，不能只寫「有補強筋」就套較有利 factor。

若 plate flexibility、bracket prying 或局部板彎曲會明顯改變 anchor force distribution，就不能只用 rigid-plate centroid model 宣告整體 PASS。

完整 connection reaction routing 另見：

- [`../structural-design/connections/load-path-and-anchor-reactions.md`](../structural-design/connections/load-path-and-anchor-reactions.md)
- [`../structural-design/connections/fastener-group-analysis.md`](../structural-design/connections/fastener-group-analysis.md)

## 鋼筋型預埋件

若 embedded plate 以 deformed bar / hooked bar 錨定，除了 anchor-to-concrete capacity 外，還應依 governing concrete design provisions 檢查適用的：

- development / anchorage；
- hook geometry；
- available embedment；
- bar steel strength；
- reinforcement congestion / cover / spacing；
- bar-to-plate welded connection。

**不得把 headed-stud breakout equation 直接當成 welded rebar development check。**

同樣地，也不得只因鋼筋拉力容量足夠，就忽略 development 或其與 plate 的連接。

## 頭栓（Headed stud）型預埋件

若使用 headed stud / headed anchor，至少分開看：

1. anchor steel；
2. head / pullout mechanism；
3. concrete breakout；
4. edge / spacing / projected-area effect；
5. side-face blowout / splitting where applicable；
6. shear edge breakout；
7. pryout；
8. stud-to-plate weld；
9. plate bending / local deformation。

若採 proprietary headed stud / anchor system，仍須確認產品或系統適用的 qualification / design evidence；不能只用名義直徑與鋼材 `Fu` 推出整體 capacity。

## 預埋鋼板本體

Anchor-to-concrete PASS 之後，embedded plate 本身仍需獨立檢查。

常見項目包括：

- strong-axis / weak-axis bending；
- biaxial plate bending；
- local bending under bracket / bolt / weld reaction；
- bearing；
- net section / tear-out where holes exist；
- yielding / rupture；
- weld-group demand；
- prying-induced local demand；
- plate flexibility 對 anchor-group force distribution 的影響。

不得用「anchor capacity 足夠」取代 plate check。

## 焊接與局部連接

錨定構件與 plate 間若有焊接，至少保存：

- weld type；
- weld length / size / effective throat；
- weld material / process basis；
- base-metal strength；
- force direction；
- eccentricity；
- weld-group mechanics；
- applicable welding standard / project requirement。

焊道 methodology 另見 [`../structural-design/connections/weld-group-analysis.md`](../structural-design/connections/weld-group-analysis.md)。

## 係數稽核（Factor audit）

Cast-in anchor 計算常同時出現：

- load factors；
- concrete strength-reduction factors；
- steel resistance factors；
- cracked-concrete modifiers；
- edge / spacing / eccentricity factors；
- reinforcement-related modifiers where applicable；
- interaction exponents / thresholds。

每一個 factor 都必須能回溯到 governing method、edition、clause / product evidence 與 applied quantity。

不得只因最終 utilization `< 1.0` 就接受結果。

Factor audit 依 [`../structural-design/review/design-factor-and-hidden-multiplier-audit.md`](../structural-design/review/design-factor-and-hidden-multiplier-audit.md) 執行。

## 審查狀態建議

### 通過（`PASS`）

只有在：

- load path 完整；
- anchor family 已辨識；
- governing source 已確認；
- applicable failure modes 已覆蓋；
- group geometry / projected-area treatment 可重建；
- plate / weld / anchor / concrete 均已完成相應檢核；
- factor 與 design basis 可追溯；

才可對明確 scope 給出 `PASS`。

### 警告（`WARNING`）

例如：

- plate-flexibility sensitivity 尚未量化但不太可能改變結果；
- inspection / fabrication evidence 尚待補件；
- 使用 bounding assumption 且已明確證明保守性。

### 不完整（`INCOMPLETE`）

例如：

- anchor type 不明；
- embedment / edge / spacing 缺資料；
- concrete geometry / projected failure surface 無法建立；
- supplementary reinforcement 被用於 resistance enhancement，但配置／development／來源不明；
- weld detail 不明；
- factor 或 resistance provenance 缺失；
- 只提供最終 `O.K.` 而無法重建中間 mechanics。

## 公開來源 routing

- **ACI CODE-318-25**：現行 structural concrete code；anchor-to-concrete design 應依專案採用 code 與其 anchoring provisions。
- 產品或 proprietary cast-in system：依 applicable evaluation / qualification documentation。
- 焊接：依實際材料、焊接型式與專案採用 welding standard。

現行版本 ownership 請以 [`anchor-standards-baseline.md`](anchor-standards-baseline.md) 為準。

> 本頁提供 failure-mode 與 review methodology，不提供通用 anchor resistance、development length、strength-reduction factor、edge modifier、weld allowable 或 interaction equation。