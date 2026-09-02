---
title: "活動窗／可開啟外牆構件結構子系統"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
---

# 活動窗／可開啟外牆構件結構子系統

本目錄整理 operable window / sash / vent 在 curtain wall 或 façade system 中的結構 load path、五金受力與整窗性能 routing。

## 核心 load path

活動窗不應只看五金螺絲。至少要拆成：

`wind / dead load / operating load`

→ `sash / vent frame`

→ `hinge / stay / lock / keeper / restrictor / hardware`

→ `hardware fastener`

→ `local extrusion / reinforcement`

→ `outer frame / curtain-wall framing`

→ `main façade support system`

每一層都可能 governing。

## 四層 verification

### 1. Sash / vent structural response

- frame bending / torsion
- glass or infill support
- deflection / racking
- corner-joint behavior
- local deformation near hardware

### 2. Hardware demand

- hinge / stay reactions
- locking-point reactions
- restrictor / stopper demand
- eccentricity / lever arm
- hardware-group force distribution

### 3. Fastener / local extrusion

- screw / bolt body tension / shear
- pull-out / thread engagement
- bearing
- local extrusion bending / tear-out / wall deformation
- reinforcement load transfer

### 4. Whole-product performance

- structural performance under pressure
- air / water performance as applicable
- operability after required loading
- operating-cycle / durability requirements where applicable

**Local connection PASS 不等於 whole-window performance PASS。**

## 現行公開標準 routing

截至 2026-09-02，FGIA Store 將下列文件列為 Active：

- **AAMA/WDMA/CSA 101/I.S.2/A440-26 (NAFS)** — North American Fenestration Standard/Specification for windows, doors, and skylights。
- **AAMA 910-24** — Life Cycle Specifications and Test Methods for AW Class Windows and Doors。

ASTM **E330/E330M-14(2021)** 仍為 exterior windows / doors / skylights / curtain walls uniform static air-pressure structural performance 的 Active test method。

這些標準是 performance / test routing；它們不直接取代 sash / hinge / screw / local extrusion 的 engineering calculation。

## 相關頁面與 routing

- [Sash / Frame Structural Analysis](sash-frame-analysis.md)
- [Operable Hardware Load Path](hardware-load-path.md)
- [Hinge / Lock / Stay Connections](hinge-lock-stay-connections.md)
- [Whole-window Performance and Life Cycle](performance-and-life-cycle.md)
- [Fastener Group Analysis](../structural-design/connections/fastener-group-analysis.md)
- [Screw Pull-out / Thread Engagement](../structural-design/connections/screw-pullout-and-thread-engagement.md)
- [Local Extrusion Failure](../structural-design/connections/local-extrusion-failure.md)

## 不可推論事項

- `sash frame PASS = hardware PASS` 不成立。
- `hardware catalogue load = installed connection capacity` 不成立。
- `number of screws × single-screw capacity` 不一定等於 hardware connection capacity。
- `NAFS rated product` 不代表任意修改 hardware、size、glass、reinforcement 或 anchorage 後仍保有原 rating。
- `E330 test PASS` 不代表 operating-cycle durability 已完成。
- 五金位置／數量若改變，load path 需要重新確認。

## 公開來源

- FGIA Store, AAMA/WDMA/CSA 101/I.S.2/A440-26
- FGIA Store, AAMA 910-24
- ASTM E330/E330M-14(2021)

> 本目錄保存 generic engineering methodology，不保存非公開專案的窗型、尺寸、五金型號、螺絲配置、荷載或試驗結果。