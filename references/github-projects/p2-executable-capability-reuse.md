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

- Case 1：half-square homogeneous conduction，28 個 evaluation points，公開說明 acceptance difference為 0.1 °C。
- Case 2：heterogeneous concrete／wood／insulation／aluminum cross-section，公開 geometry dimensions、conductivities、surface resistances、expected total heat flow與 evaluation-point temperatures；公開說明 temperature與heat-flow validation tolerances。

這些公開 reproduction可作 independent regression evidence，但不能因此宣稱本 repo 已取得或可重製 ISO 10211 全文。

### 可重用候選

#### 有限元素 backend 候選：kinnala/scikit-fem

- disposition：`ADAPT_CANDIDATE`
- reviewed revision：`53d7555ec355477e3b88f6397e206979b689d14c`
- license：BSD-3-Clause
- runtime：Python 3.10+
- minimal dependencies：NumPy、SciPy
- capability：triangular／quadrilateral FEM assembly、sparse systems、boundary DOFs與post-processing primitives
- adoption boundary：可作 numerical backend；本 repo 自己擁有 thermal-bridge input/output contract、material/boundary provenance與validation semantics。不得把 scikit-fem examples 當 ISO authority。

#### 熱橋應用參考：schoenenbach/thermal-bridge

- disposition：`REFERENCE_ONLY`
- license：AGPLv3
- observation：project宣稱已用 ISO 10211 test cases驗證，且含 declarative geometry／adaptive mesh／temperature與Ψ/fRsi outputs。
- boundary：不直接 copy、vendor或改寫其 implementation；只作 architecture/reuse landscape evidence。

## 下一個 Hot gate

先完成 **solver reuse + benchmark admission**，再決定是否新增 production dependency／kernel。至少要回答：

- dependency pinning與CI是否可接受；
- Case 1／Case 2 是否可在本 repo 的 proposed contract 下可重現；
- material conductivity與boundary condition如何保持 project-supplied provenance；
- numerical-method PASS 如何與 project-specific ISO compliance 分開；
- 若只完成2D cases，輸出必須明確標示其 validation coverage，不得宣稱完整 3D high-precision method。

在以上 gate 關閉前，不建立 Ψ-value compliance、condensation acceptance、DXF importer、3D solver或 UI。

## 來源（Sources）

- The Aluminum Association, Aluminum Design Manual 2020: https://www.aluminum.org/aluminum-design-manual-2020
- The Aluminum Association, Aluminum Structures FAQ: https://www.aluminum.org/sites/default/files/2021-09/DesigningAluminumStructuresFAQs20201012_0.pdf
- FGIA, AAMA TIR-A9-14: https://store.fgiaonline.org/AAMA-TIR-A9-14/
- ISO, ISO 10211:2017: https://www.iso.org/standard/65710.html
- COMSOL, Thermal Bridges in Building Construction — 2D Square Column
- COMSOL, Thermal Bridges in Building Construction — 2D Composite Structure
- GitHub, kinnala/scikit-fem
- GitHub, schoenenbach/thermal-bridge
