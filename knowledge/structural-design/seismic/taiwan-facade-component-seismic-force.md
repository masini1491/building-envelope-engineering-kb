---
title: "台灣外牆非結構構材地震力方法"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
---

# 台灣外牆非結構構材地震力方法

## Purpose

本頁整理台灣《建築物耐震設計規範及解說》第四章對外牆／帷幕非結構構材地震力的工程 routing。公開 KB 只保存公式角色、輸入欄位與 guardrail；不保存任何專案的實際 `SDS / Ip / ap / Rp / Wp / hx / hn`。

## Component-force structure

現行第四章使用的基本概念可整理為：

`Fp = function(SDS, Ip, ap, Rp, Wp, hx/hn)`

其中各符號的 precise equation、上／下限與例外條件應以 current official chapter 為準。

AI / calculator 必須把以下欄位分開保存：

- `SDS`：design spectral acceleration parameter
- `Ip`：component importance factor
- `ap`：component amplification / response-related coefficient
- `Rp`：component response modification / ductility-related coefficient
- `Wp`：component operating / effective weight as required by regulation
- `hx`：component installation elevation
- `hn`：building reference height
- component category / table row
- regulation edition / source clause

## Height amplification matters

第四章公式包含 `hx/hn`，因此 component seismic force 可能隨安裝高度改變。

不得把某一樓層算出的 component force 無條件套到全棟，也不得只記「本案 seismic coefficient = X」而遺失其高度來源。

## Component category selection

外牆帷幕相關部件至少可能落在不同類別：

- wall / panel body
- wall-panel connection itself
- fixing / anchorage of the connection system

現行官方表 4-1 對這些類別給定的 `ap / Rp` 不完全一致，因此 category selection 是計算的一部分，而不是註解。

建議資料模型：

```yaml
seismic_component:
  category: external_wall | panel_connection | connection_fixing | other
  category_source: current_table_4_1
  ap: ...
  Rp: ...
  source_clause: ...
```

## Weight definition guard

`Wp` 必須依 current regulation 對該構件的定義建立，不應任意：

- 只取 panel skin 重量；
- 漏掉與 seismic load path 共同運動的 framing / hardware；
- 或反過來把不屬於該 component 的主體結構重量一起加入。

若 effective component mass / weight boundary 不明，結果應標記 `INCOMPLETE`。

## Force direction

應依 governing regulation 與 component geometry 分別處理所需方向；不要因 façade 主要受風方向是 façade-normal，就假設 seismic 只需同方向。

對轉角、突出物、懸吊構件、設備附件或具有多軸 load path 的 façade subsystem，可能需要多方向／組合檢核。

## Load combinations

本頁不硬編碼任何 load combination。地震 component force 與 dead / wind / other action 的組合應回到 current Taiwan structural design basis / project specification。

AI 不得從舊 project calculation 自行重建 load combination rules。

## Output requirements

至少輸出：

1. regulation edition / date
2. component category
3. `SDS / Ip / ap / Rp / Wp / hx / hn`
4. equation / clause reference
5. calculated component force
6. minimum / maximum cap treatment if applicable
7. force direction
8. downstream load path target
9. assumptions / missing data

## Do not assume

- `ap / Rp` 是所有 façade component 共用常數
- `Ip = 1.0` 可永遠預設
- `Wp = glass weight` 可適用所有 curtain-wall checks
- 同一建築所有樓層 seismic component force 相同
- 舊案使用過的係數可直接視為 current code

## Primary source

- 內政部國土管理署《建築物耐震設計規範及解說》總頁：https://www.nlma.gov.tw/ch/legislation/regsearch/175
- 官方第四章 PDF：https://www.nlma.gov.tw/filesys/file/chinese/publication/law/law2/111061504.pdf

> 正式工程計算前應重新查驗 current chapter，尤其是公式、上下限、component table 與最新修正。