---
title: "結構玻璃 Structural Glass"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
---

# 結構玻璃 Structural Glass

本目錄處理玻璃不只是 cladding / infill，而是作為 beam、fin、mullion、walkable panel、point-supported member 或其他主要受力構材的 building-envelope engineering 問題。

## Core routing

結構玻璃問題應至少分成：

1. **Glass product / make-up**：annealed、heat-strengthened、fully tempered、laminated、IGU 等。
2. **Laminated effective stiffness**：interlayer 的 shear coupling、temperature、load duration、geometry 與 boundary condition。
3. **Global structural behavior**：glass fin / beam / plate 的 stress、deflection、buckling、reaction。
4. **Local discontinuities**：drilled holes、notches、point supports、bearing、clamps、shoes。
5. **Structural silicone load path**：glass-to-metal 或 glass-to-glass structural sealant glazing。
6. **Mechanical connections**：bolts、plates、welds、anchors 與 support reactions。
7. **Movement compatibility**：inter-story drift、thermal movement、joint clearance、support rotation。
8. **Post-breakage / redundancy**：單片或單層破裂後的安全性、剩餘承載與 fall-out control。
9. **Testing / validation**：必要時以 full-scale / component test、project-specific manufacturer review 或 validated analysis 補足標準 scope 的限制。

## Current public standards baseline

- **ASTM E1300-24** — Standard Practice for Determining Load Resistance of Glass in Buildings
  - 建築玻璃 load resistance 的核心 practice。
  - 其 scope 對 drilled、notched、grooved glass 等情況有限制；遇到 point-supported / drilled glass 不得只靠 E1300 宣稱 PASS。

- **ASTM E3491-25** — Standard Practice for Determination of Laminated Glass Effective Thickness
  - laminated glass effective thickness 的現行專門 practice。
  - 可用於多片玻璃、對稱／非對稱 laminate，以及 beam / column / plate 等不同結構型態；仍需正確輸入 interlayer properties、temperature、load duration、geometry 與 boundary condition。

- **ASTM E2751/E2751M-21** — Standard Practice for Design and Performance of Supported Laminated Glass Walkways
  - 適用 supported laminated glass walkways、treads、landings 等 walkable glass；特別需要處理破裂後行為與安全性。

- **ASTM C1184-23** — Standard Specification for Structural Silicone Sealants
- **ASTM C1401-23** — Standard Guide for Structural Sealant Glazing
- **ASTM C1135-19(2024)** — Standard Test Method for Determining Tensile Adhesion Properties of Structural Sealants

## Structural-glass load-path rule

不要把所有荷載都歸到同一條路徑。至少要區分：

- wind / pressure load
- glass self-weight
- live load（若為 walkable glass）
- seismic / inter-story imposed movement
- thermal movement
- local connection force

例如 structural silicone 可以承擔 wind load transfer，但 glass dead load 是否由 silicone 承擔必須依實際 approved system 設計；很多系統會另外以 setting block、shoe、bearing support、fin 或其他 mechanical support 建立 dead-load path。

## Do not assume

- laminated glass nominal thickness = structural effective thickness
- interlayer shear modulus 是固定材料常數
- drilled / point-supported glass 可直接用 ASTM E1300 完整覆蓋
- polymer sleeve / PTFE bushing 可以「消除」孔邊應力集中
- structural silicone 的 allowable design stress 或 bite 是跨品牌固定值
- glass fin 的 global stress check 可取代 hole / clamp / support 的 local stress check
- heat-soak treatment 可取代結構設計或 post-breakage design

## Public-repository rule

本目錄只保存可泛化方法與公開來源。非公開專案文件若曾用於維護者理解問題，不得在此留下專案名稱、尺寸、荷載、圖號、節點、截圖或其他可識別資訊。

## Related pages

- `laminated-glass-effective-thickness.md`
- `glass-fin-design.md`
- `point-supported-drilled-glass.md`
- `glass-to-glass-structural-silicone.md`
- `structural-glass-movement.md`
- `structural-glass-fea-modeling.md`
- `walkable-glass.md`
- `post-breakage-and-redundancy.md`

## Primary public sources

- ASTM E1300-24: https://store.astm.org/e1300-24.html
- ASTM E3491-25: https://store.astm.org/e3491-25.html
- ASTM E2751/E2751M-21: https://store.astm.org/e2751_e2751m-21.html
- ASTM C1184-23: https://store.astm.org/c1184-23.html
- ASTM C1401-23: https://store.astm.org/c1401-23.html
- ASTM C1135-19(2024): https://store.astm.org/c1135-19r24.html

> 本目錄是 engineering routing，不取代專業結構玻璃計算、有限元素模型驗證、玻璃加工廠／sealant manufacturer review 或 project-specific testing。