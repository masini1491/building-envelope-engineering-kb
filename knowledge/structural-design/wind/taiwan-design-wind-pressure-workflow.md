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