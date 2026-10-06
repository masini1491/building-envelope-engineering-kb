---
title: "台灣帷幕牆設計風壓工作流程"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
---

# 台灣帷幕牆設計風壓工作流程

## 權威來源基線

截至 2026-09-02，內政部國土管理署仍列示之現行《建築物耐風設計規範及解說》為 103 年修正版，104-01-01 起施行；內政部建築研究所後續已完成第三版修訂草案研究，但仍屬修訂／法制作業階段，不應把草案當成現行法規。

帷幕牆屬外部被覆物與局部構材範疇時，核心 routing 是規範第三章；若規範無法提供必要風力／風壓資料，或依法／專案條件採風洞試驗，應依風洞結果與專案規範處理。

## 四步驟工作流

依建研所《帷幕牆系統結構耐風設計手冊》：

1. 蒐集建築物與工址風環境資料。
2. 依構件位置與有效受風面積決定外風壓係數。
3. 計算各來風方向下的設計風壓。
4. 取控制之最大正風壓與負風壓，分別進入構件設計。

## 構件特定風壓

同一立面不應只用一個「全案固定風壓」無條件套到所有構件。應分辨：

- 面材（玻璃、鋁板、石材等）
- 直料 mullion
- 橫料 transom
- 繫件／anchor connection

因為各構件的位置、有效受風面積與 load path 不同，對應設計風壓可能不同。

## 荷載路徑

基本概念：

`外部被覆物 → 直料／橫料等局部構材 → 繫件／連接件 → 主體結構`

風壓計算與構件設計必須沿同一 load path 保持一致；不可只檢核鋁擠型而忽略連接件，也不可只檢核面材而未確認反力如何傳至樓板／梁／柱。

## 有效受風面積防呆

有效受風面積不是單純「整片立面面積」。應依現行耐風規範對該構件的定義與幾何決定。AI 若沒有足夠 project geometry，不得自行猜 effective wind area。

## 風洞試驗 routing

建研所說明：規範無法提供所需主要風力抵抗系統風力或外部被覆物設計風壓資料時，可採風洞試驗；高層或風力效應顯著案件亦常以風洞結果控制。

若專案已有正式風洞報告：

- 先確認報告中的 pressure tap / zone / reference height / sign convention / load combination。
- 再確認其結果是 pressure、force、coefficient 或 envelope。
- 不要把規範計算值與風洞值機械相加。
- 以專案採用的 structural design basis 判斷哪一組是 governing source。

## 不可推論事項

- 不得自行使用舊經驗風壓取代現行規範／正式風洞結果。
- 不得把正壓與負壓只取絕對值後忽略不同 failure mode。
- 不得用面材 effective wind area 直接當 mullion / anchor 的 effective wind area。
- 第三版耐風規範研究草案尚未正式生效前，不得當作法定現行規範。

## 主要來源

- 內政部國土管理署｜建築物耐風設計規範及解說：https://www.nlma.gov.tw/ch/legislation/regsearch/166
- 內政部建築研究所｜帷幕牆系統結構耐風設計手冊：https://www.abri.gov.tw/PeriodicalDetail.aspx?isShowAll=false&key=91&n=861&s=2428
- 內政部建築研究所｜建築物耐風設計規範及解說修訂草案研究：https://www.abri.gov.tw/News_Content_Table.aspx?n=807&s=315611&sms=9489

> 本頁提供 workflow 與 authority routing，不取代正式耐風計算書或專案風洞報告。

## 外牆設計風壓 V1 deterministic capability

本知識庫已定義第一版可執行外牆設計風壓能力，目的不是要求使用者先知道規範參數，而是讓 ChatGPT 先整理 project facts，再由可追溯的 machine-readable 規範資料與 deterministic kernel 完成計算。

### 自然語言 intake

使用者可以只說「幫我計算外牆設計風壓」。ChatGPT 應先辨識已提供條件，再一次性補問真正缺少、且不能由規範資料 deterministic derive 的 project facts。

使用者／專案側通常需要提供或確認：

- 案址（縣市；若該縣市風速分區需要鄉鎮市區，需再提供行政區）
- 建築物用途／類別
- 地況 A／B／C；若不知道，可先描述周邊環境，再由 ChatGPT 依 2.3 節提出候選分類並請使用者確認
- 地形係數 Kzt；若沒有既定值，不得默認特殊地形不存在，需確認是否屬獨立山丘、山脊或懸崖近頂端等情況
- 建築封閉類型：封閉式、部分封閉式或開放式
- 建築物平均屋頂高度 h
- 欲計算之外牆位置高度 z
- 該構件的有效受風面積 A
- 建築物最小水平尺寸 B
- 是否已有正式風洞報告／專案指定 governing wind source

下列數值原則上不要求使用者自行查表輸入；在 applicability 已確認後，由 KB reference data／kernel 自動解析或計算：

`V10(C) / I / α / zg / GCpi / K(z) / K(h) / q(z) / q(h) / a / GCp`

已在同一輪對話提供的條件不得重新詢問。分類仍有歧義時，先請使用者確認分類，不得把自然語言猜測直接送入 calculator。

### 第一版（V1）適用範圍

目前 `wind_pressure` V1 只支援：

- 103 年修正版《建築物耐風設計規範及解說》
- 外牆之局部構材與外部被覆物
- `h > 18 m`
- 封閉式或部分封閉式建築物
- 圖 3.2 牆面 Zone 4／Zone 5
- 依有效受風面積作對數軸內插
- 規範法（`governing_wind_source = code`）

目前不支援並應 fail closed：

- `h <= 18 m`
- 開放式建築物（不得只把 `GCpi=0` 後繼續套圖 3.2）
- 已由正式風洞結果 governing 的案件
- 圖 3.2 以外的屋頂、其他幾何或其他 provision
- 需要超出目前 admitted reference dataset 的行政區／係數或規範版本

### 公式與 reference ownership

machine-readable 規範資料由：

`references/government/taiwan-wind-code-103-v1.json`

保存。它只收錄本 V1 真正會執行的 103 年規範資料、來源與適用界線；外部網站計算器只可作 reference-only cross-check，不得成為 canonical engineering truth。

V1 的風速壓採 2.6 節：

`q(z) = 0.06 K(z) Kzt [I V10(C)]²`

其中 `q` 的規範基礎單位為 `kgf/m²`，kernel 再使用固定換算 `1 kgf/m² = 0.00980665 kPa` 產生 SI 輸出。地況係數：

`K(z) = 2.774 (z/zg)^(2α)`

且 `z <= 5 m` 時依規範採 5 m 計算。

對部分封閉式建築物的正內風壓，2.2 節允許內風速壓採 `q(zh0)` 或 `q(h)`。為使 V1 deterministic 且不在缺少開口高度時猜測，V1 明確固定採規範允許的 `q(h)`；若未來要支援 `q(zh0)`，必須另行擴充 input contract 與 regression。

圖 3.2 的牆面 `GCp` 以圖中 2 m² 與 50 m² 平台為 anchor，中間依圖的對數面積軸做線性內插；圖 3.2 解說採 ASCE 7-02 `GCp × 2.083` 的換算。角隅區：

`a = max(0.10 B, 0.9 m)`

### 計算與呈現責任

`scripts/engineering_calc/wind_pressure.py` 只接受已確認的結構化輸入，不負責自然語言判斷。它保留 raw computational values，再另外產生 display values；顯示用 rounding 不得回寫污染後續計算。

`scripts/engineering_calc/review.py` 以 `check_type = "wind_pressure"` 提供統一 adapter。adapter 的 `MATCH / MISMATCH` 只表示 reported 與 recomputed numerical agreement，不代表整體耐風設計 `PASS / FAIL`。

若 input 不足，回傳 `INCOMPLETE_INPUT`；若條件超出 V1 applicability，回傳 `UNSUPPORTED_MODEL`。不得為了得到數值而自行補造 `Kzt`、地況、封閉類型、有效受風面積或 governing wind source。

