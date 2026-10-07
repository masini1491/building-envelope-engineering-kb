---
title: "P2 可執行能力 reuse 與 authority admission"
verification_status: "RESEARCH_REVIEWED"
verified_at: "2026-10-07"
document_type: "reuse-admission"
---

# 可執行能力 reuse 與 authority admission（P2）

## 範圍

本 dossier 只處理 P2 三條 executable capability 的 authority／reuse admission：

1. 鋁直料／橫料構件強度
2. 自攻螺絲連接容量
3. 二維熱橋 steady-state numerical solver

它不是設計標準，也不保存受版權保護標準的完整公式、表格或設計值。

## 鋁構件強度

### 權威來源（Authority）

The Aluminum Association 目前公開 bookstore／standards surface 仍列 **Aluminum Design Manual 2020**。官方發布資訊說明此版包含 structural-component strength、buckling、weld-affected strengths、concentrated-force provisions 與 screw-chase pull-out 等更新。

### 納入判定（Admission）

`BLOCKED_EXACT_STANDARD_KERNEL`

本 repo 已有 beam response、required section property 與 externally supplied allowable/capacity comparison，因此沒有必要為了「看起來完整」再造一層同義 wrapper。真正缺的是 ADM governed member/local-element capacity，而公開一手 evidence 不足以安全重建完整 equations、tables、alloy/temper strengths 與 applicability。

## 自攻螺絲連接容量

### 權威來源（Authority）

FGIA store 在 2026-10-07 read-back 仍把 **AAMA TIR-A9-14 — Design Guide for Metal Cladding Fasteners** 標示為 Active，並列出 2015 errata 與 2020 addendum。其公開描述明確涵蓋 metal curtain wall framing members/components 的 fastener selection。

### 納入判定（Admission）

`BLOCKED_EXACT_STANDARD_KERNEL`

現有 `connection.py` 已能計算 demand-side bearing stress、shear/tension magnitude、externally supplied capacity utilization與 externally established thread-engagement requirement。缺口是 authoritative pull-out／pull-over／bearing resistance，不應由舊版表格、第三方網站或通用公式猜測。

## 二維熱橋 solver

### 現行標準（Current standard）

ISO 官方頁面確認 **ISO 10211:2017, Edition 2** 仍為 current；其 scope 包括 2D／3D thermal-bridge numerical models、heat flows、surface temperatures、boundary conditions與 thermal properties。

### 公開 benchmark 證據

COMSOL 公開 application documentation重現 ISO 10211:2017 的 2D validation cases：

- Case 1：half-square homogeneous conduction，28 個 evaluation points，公開 acceptance difference為 0.1 °C。
- Case 2：heterogeneous concrete／wood／insulation／aluminum cross-section，公開 geometry dimensions、conductivities、surface resistances、expected total heat flow與 evaluation-point temperatures；公開 temperature tolerance 0.1 °C、heat-flow tolerance 0.1%。

這些公開 reproduction可作 independent numerical-backend regression evidence，但不能因此宣稱本 repo 已取得或可重製 ISO 10211 全文，也不能把兩個 2D benchmark PASS 升格成完整 ISO 10211 project compliance。

### 可重用候選

#### 有限元素 backend：kinnala/scikit-fem

- disposition：`ADAPT_CANDIDATE / BENCHMARK_VERIFIED`
- reviewed upstream head：`53d7555ec355477e3b88f6397e206979b689d14c`
- probe package：`scikit-fem==12.0.2`
- package tag revision：`a9c43abbc3b17c36a059132c9f571447b755920e`
- license：BSD-3-Clause
- runtime：Python 3.10+
- minimal dependencies：NumPy、SciPy
- capability：triangular／quadrilateral FEM assembly、sparse systems、boundary DOFs與 post-processing primitives
- adoption boundary：可作 numerical backend；本 repo 自己擁有 thermal-bridge input/output contract、material/boundary provenance與 validation semantics。不得把 scikit-fem examples 當 ISO authority。

#### 熱傳 backend probe evidence

Temporary non-merge probe：

- PR：`#8`
- branch：`chatgpt/p2-thermal-backend-probe`
- probe commit：`082b4e16641a1ffe115aa0e4757da752bec6ff2a`
- GitHub Actions run：`37589368465`（run 253）
- tested environment：Ubuntu runner、Python 3.12、`numpy==2.5.3`、`scipy==1.18.1`、`scikit-fem==12.0.2`
- repository engineering tests：44 tests PASS
- Case 1：最大 evaluation-point temperature error = `0.0477770670 °C`，小於等於 0.1 °C
- Case 2：最大 evaluation-point temperature error = `0.0387100955 °C`，小於等於 0.1 °C
- Case 2：total heat flow = `9.4926417761 W/m`；相對於 9.5 W/m 的 relative error = `0.0007745499`（約 0.07745%），小於等於 0.1%
- probe workflow conclusion：`SUCCESS`
- PR disposition：`CLOSED / NOT MERGED`

這組 evidence 足以 admission「scikit-fem 12.0.2 可作目前 2D steady-state numerical backend 候選」；它不 admission production API、永久 dependency、Ψ-value/fRsi、condensation criterion、3D solver或任何 project-specific ISO compliance claim。

#### 熱橋應用參考：schoenenbach/thermal-bridge

- disposition：`REFERENCE_ONLY`
- license：AGPLv3
- observation：project宣稱已用 ISO 10211 test cases驗證，且含 declarative geometry／adaptive mesh／temperature與Ψ/fRsi outputs。
- boundary：不直接 copy、vendor或改寫其 implementation；只作 architecture/reuse landscape evidence。

## Production kernel admission 邊界

下一個 Hot 可以開始 production kernel，但必須維持下列 boundary：

- numerical backend 採 scikit-fem adapter/reuse，不自行重寫 FEM engine；
- production kernel只接受 caller 已離散完成的 2D mesh與 project-supplied material/boundary facts，不把 CAD importer、material catalog或 geometry authoring混入 solver owner；
- material conductivity保持 caller/project provenance；solver不得自行補 catalog value；
- thermal boundary condition必須顯式提供；不得由場景名稱猜 indoor/outdoor surface resistance；
- dependency應隔離於 thermal capability；缺 backend 時 fail closed，不得退回模型手算或未驗證自製 solver；
- output只可宣稱 numerical result與實際 validation scope；Case 1／Case 2 regression PASS 不等於完整 ISO 10211 compliance；
- benchmark regression應保留 temperature與 heat-flow兩種 evidence，避免只驗單一輸出；
- production adapter尚未 admission前，不接 `review.py`／自然語言入口。

## 下一個 Hot gate

進入 **2D thermal production kernel contract／implementation**，先固定：

1. isolated dependency pinning與 CI placement；
2. triangle mesh／per-element conductivity／boundary-condition input schema；
3. temperature field／selected boundary heat-flow／backend provenance／validation-scope output；
4. invalid mesh、non-finite／non-positive conductivity、boundary conflict、missing backend 的 fail-closed semantics；
5. Case 1／Case 2 永久 regression如何由 generic production kernel重現，而不是把 benchmark geometry寫死進 kernel。

STOP boundary仍為：不建立 Ψ-value project compliance、condensation acceptance criterion、material catalog、DXF importer、3D solver、UI或自然語言 adapter。

## 來源（Sources）

- The Aluminum Association, Aluminum Design Manual 2020: https://www.aluminum.org/aluminum-design-manual-2020
- The Aluminum Association, Aluminum Structures FAQ: https://www.aluminum.org/sites/default/files/2021-09/DesigningAluminumStructuresFAQs20201012_0.pdf
- FGIA, AAMA TIR-A9-14: https://store.fgiaonline.org/AAMA-TIR-A9-14/
- ISO, ISO 10211:2017: https://www.iso.org/standard/65710.html
- COMSOL, Thermal Bridges in Building Construction — 2D Square Column
- COMSOL, Thermal Bridges in Building Construction — 2D Composite Structure
- GitHub, kinnala/scikit-fem
- GitHub, schoenenbach/thermal-bridge
