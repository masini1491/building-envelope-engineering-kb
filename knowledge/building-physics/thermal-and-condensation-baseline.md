---
title: "建築外殼熱傳與結露基線"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
---

# 建築外殼熱傳與結露基線

## 核心觀念

Building-envelope thermal performance 不能只看單一材料的 conductivity。實際牆體／帷幕系統的 U-factor、surface temperature、thermal bridge 與 condensation risk 取決於完整 assembly。

## 主要標準 routing

- **ASTM C1363-24** — Thermal Performance of Building Materials and Envelope Assemblies by Means of a Hot Box Apparatus
  - 用於在受控條件下量測 building assembly 的 heat transfer。
- **AAMA 1503-09** — Voluntary Test Method for Thermal Transmittance and Condensation Resistance of Windows, Doors and Glazed Wall Sections
  - FGIA 目前 store 標示為 Active。
  - 用於 steady-state 下量測 thermal transmittance / U-factor 與 condensation resistance factor 等。

專案若採 NFRC、ISO、CNS 或其他 energy-code 方法，仍應依指定體系處理；本頁不宣告不同體系完全等價。

## 帷幕牆／玻璃外牆熱傳路徑

至少拆成：

1. glass center-of-glass
2. IGU spacer / edge-of-glass
3. aluminum framing
4. thermal break
5. pressure plate / cap / fastener penetration
6. spandrel zone
7. insulation continuity
8. slab edge / anchor / steel bracket thermal bridge
9. perimeter seal and adjacent wall interface

## 結露判斷邏輯

結露不是只由「室內外溫差」單一因素決定。至少與：

- indoor temperature
- indoor relative humidity
- outdoor design temperature
- local interior surface temperature
- air leakage
- thermal bridge
- glazing edge condition
- framing conductivity

相關。

判斷時應區分：

- center-of-glass condensation
- edge-of-glass condensation
- frame condensation
- concealed condensation inside spandrel / cavity
- air-leakage-driven condensation

## 熱橋防呆

即使 main mullion 有 thermal break，以下位置仍可能形成局部熱橋：

- steel anchor / bracket
- fasteners crossing insulation
- slab edge
- perimeter closure
- panel reinforcement
- parapet / canopy interfaces

因此「型錄 frame U-value」不能直接代表整棟 facade 的 assembly performance。

## 試驗與計算的區分

Hot-box test、AAMA 1503 test、2D/3D thermal simulation、material conductivity data 各自只證明其實際 scope。

- test specimen PASS 不自動代表所有 project dimensions / interfaces
- simulation 結果依賴 geometry、boundary conditions、material properties
- material R-value 不可直接當整體 wall R-value

## 不可推論事項

- `有 thermal break = 不會結露` 不成立。
- `Low-E glass = frame condensation solved` 不成立。
- `insulation thickness 相同 = thermal performance 相同` 不成立。
- 單一 component U-factor 不等於 whole-envelope U-factor。

## 主要來源

- ASTM C1363-24: https://store.astm.org/standards/c1363
- FGIA AAMA 1503-09: https://store.fgiaonline.org/AAMA-1503-09/

> 本頁是 building-physics routing；正式 energy-code compliance 與 condensation analysis 仍應依專案規範與指定計算方法。