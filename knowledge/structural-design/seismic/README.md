---
title: "帷幕牆／外牆非結構構材耐震設計 Routing"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
---

# 帷幕牆／外牆非結構構材耐震設計 Routing

本目錄整理台灣建築外牆／帷幕系統作為附屬於建築物之部分構體、非結構構材與其接合系統時的地震設計 routing。

## 現行權威來源基線

截至 2026-09-02，內政部國土管理署《建築物耐震設計規範及解說》總頁列示：

- 111-06-14 修正，111-10-01 生效；
- 111-07-08 勘誤部分章節；
- **113-03-01 再修正部分規定，並自即日生效**。

官方目錄仍明確將**第四章**定義為：

> 附屬於建築物之結構物部分構體、非結構構材與設備之地震力。

正式設計前應重新確認 current master page 與對應章節，不應只看舊計算書封面年份判斷規範版本。

## Façade seismic design 要拆成兩條主線

### 1. 受力路徑

`façade / panel / framing mass → seismic component force → connection / anchor → primary structure`

處理：

- component seismic force
- connection force
- anchorage / fastener / bracket capacity
- load transfer to primary structure

### 2. 位移路徑

`building story deformation → support / anchor relative movement → mullion / panel / glass / joint compatibility`

處理：

- inter-story drift
- support movement
- slot / stack joint / splice movement
- glass edge clearance
- sealant / gasket / joint deformation

**Force PASS 不代表 movement PASS；movement compatible 也不代表 attachment strength 已完成。**

## 第四章結構原則

第四章要求固定於建築物的部分構體、永久性非結構構材及其附件依規定地震力設計；其中附件包含 anchorage 與所需支撐。

規範同時說明：依公式決定的地震力不只作用於構材本體，也應用於：

- 構材與結構體的接頭與錨定；
- 將地震力傳遞至主抗震結構系統的構材與接頭。

因此 curtain-wall seismic check 的 load path 不應停在 façade member 本體。

## 外牆分類不可視為相同

現行官方第四章表 4-1 對「外部非結構牆及其接合」至少分成：

- 外部非結構牆／牆本體
- 牆版接合本體
- 接合系統之固定物

其 `ap / Rp` 並非全部相同。

這表示 AI / calculator 不得只保存：

`facade seismic coefficient = X`

而應保存**component category + coefficient source + edition**。

## 相關頁面與 routing

- [Taiwan Façade Component Seismic Force](taiwan-facade-component-seismic-force.md)
- [Seismic Connection Load Path](seismic-connection-load-path.md)
- [Seismic Movement Compatibility](seismic-movement-compatibility.md)
- [Load Path / Anchor Reactions](../connections/load-path-and-anchor-reactions.md)
- [Continuous Mullion Analysis](../framing/continuous-mullion-analysis.md)
- [Splice / Sleeve Modeling](../framing/splice-and-sleeve-modeling.md)
- [Glass-edge Relative Deflection](../framing/glass-edge-relative-deflection.md)

## 不可推論事項

- 不得從舊案直接複製 `SDS / Ip / ap / Rp`。
- 不得把外牆本體、panel connection、anchor / fixing 使用同一組係數。
- 不得只算 component inertia force 而漏掉 connection / anchorage。
- 不得只做 strength check 而漏掉 inter-story movement compatibility。
- 不得把美國 ASCE 7 component coefficient 直接當台灣法規值。

## 主要來源

- 內政部國土管理署｜建築物耐震設計規範及解說：https://www.nlma.gov.tw/ch/legislation/regsearch/175
- 官方第四章 PDF：https://www.nlma.gov.tw/filesys/file/chinese/publication/law/law2/111061504.pdf

> 本目錄保存 current Taiwan seismic routing；正式計算仍須依專案所在地、建築用途、樓層高度與 current governing regulation 取得輸入值。