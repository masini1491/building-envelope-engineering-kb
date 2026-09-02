---
title: "耐震連接荷載路徑"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 耐震連接荷載路徑

## 核心概念

外牆／帷幕耐震設計不能停在 component force。地震力必須沿完整 load path 傳入主體結構：

`panel / glass / framing mass → local connection → bracket / cleat → fastener / anchor → slab / beam / column`

各層 failure mode 可能不同。

## Connection demand

由 façade component seismic force 取得的 action 應依實際幾何、支點數、偏心與固定方式轉成：

- shear
- tension / compression
- moment
- torsion where applicable

不得只用：

`component force / number of bolts`

作為所有 fastener demand。

## 偏心

典型 curtain-wall seismic connection 可能存在：

- façade centerline 到 bracket plane 的偏心
- stand-off / shim
- vertical slot
- anchor spacing
- bracket leg depth
- out-of-plane offset

因此 connection group 要考慮 direct force + eccentric moment。

## Different component categories

台灣耐震規範第四章對 external wall body、panel connection 與 fixing / anchorage 可能指定不同 `ap / Rp`。因此：

- panel body force 不一定等於 connection design force；
- connection / fixing 可能需要依其 own category 重新取得 governing coefficient；
- 不得只把 panel force機械平均給 anchor。

## 破壞模式檢核表

至少考慮：

- fastener tension / shear interaction
- fastener-group eccentricity
- bearing
- pull-out / thread engagement
- local extrusion / plate bending
- bracket bending
- weld group
- cast-in / post-installed anchor failure modes
- concrete edge / breakout / pullout / pryout as applicable
- primary-structure interface

Routing：

- `../connections/fastener-group-analysis.md`
- `../connections/screw-pullout-and-thread-engagement.md`
- `../connections/local-extrusion-failure.md`
- `../connections/weld-group-analysis.md`
- `../connections/load-path-and-anchor-reactions.md`

## Movement must remain compatible

耐震連接不只需要「夠強」，也可能需要允許指定方向的層間相對位移。

因此 fixed / sliding / slot / stack joint 的 movement function 不應被 connection-strength calculation 消掉。

例如增加 bolt clamp 或把 slot 全鎖死可能提高某些短期 strength，但同時破壞原本 movement accommodation；這必須作 system-level 判斷。

## Output requirements

至少保存：

1. upstream seismic component force source
2. connection category
3. geometry / eccentricity
4. force decomposition
5. group analysis
6. each failure mode demand
7. capacity source / edition
8. movement function
9. governing ratio / status
10. missing data

## 不可推論事項

- seismic connection = wind connection with different load scalar
- bolt count alone defines load sharing
- slot means zero force in slot direction
- anchor catalogue value can be used without concrete / edge / spacing / seismic condition
- connection PASS means inter-story drift compatibility PASS

## Primary-source routing

- 內政部國土管理署《建築物耐震設計規範及解說》第四章
- applicable anchor design standard / evaluation report
- applicable aluminum / steel / fastener design standard

> 本頁保存通用 load-path methodology，不重製專案連接細節。