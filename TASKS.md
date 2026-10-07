# 目前任務（TASKS）

本檔是 building-envelope-engineering-kb 的 Hot coordination surface，只保存目前可執行或 current critical-path 的工作。

## 目前執行中的工作

### 二維熱橋 production kernel admission（P2／KB-P2-C2）

- **來源**：`KB-P2-C` solver reuse／benchmark admission 已取得 remote PASS evidence；PR #8 已關閉且未 merge。
- **目標**：建立最小、隔離、可 fail-closed 的 2D steady-state thermal numerical kernel，重用已驗證的 scikit-fem backend，而不把 benchmark harness、CAD、material catalog或 ISO compliance判定混進 production owner。
- **Admitted backend evidence**：
  - `scikit-fem==12.0.2`，tag revision `a9c43abbc3b17c36a059132c9f571447b755920e`，BSD-3-Clause。
  - Probe PR #8 / commit `082b4e16641a1ffe115aa0e4757da752bec6ff2a` / Actions run `37589368465` SUCCESS。
  - Case 1 max temperature error `0.0477770670 °C`。
  - Case 2 max temperature error `0.0387100955 °C`；heat-flow relative error約 `0.07745%`。
- **本 Stage contract**：
  1. backend dependency採 isolated pin／isolated CI placement；不得讓單一 optional capability擴大既有 repository validation failure domain。
  2. production kernel接受 caller 已離散的 2D triangular mesh、每 element conductivity、以及顯式 thermal boundary conditions；不負責 CAD/geometry authoring或材料資料庫。
  3. conductivity與boundary facts皆保持 caller/project provenance，不自行猜值。
  4. output至少包含 node temperature field、指定 boundary heat flow、backend identity/provenance、validation scope；不得宣稱 project-specific ISO 10211 compliance。
  5. backend unavailable、可由 kernel／backend structural checks 辨識的 invalid mesh（例如 index／退化元素／edge-connectivity／manifold edge、duplicate／orphan vertices）、non-finite／non-positive conductivity、boundary conflict或其他已宣告 contract violation時 fail closed；任意 mesh 的完整 computational-geometry conformity（例如重疊元素／T-junction）仍是 caller／mesh-generator provenance，不得宣稱 kernel 已全面驗證。
  6. Case 1／Case 2 永久 regression必須經 generic production kernel重現，benchmark geometry不得寫死在 production module。
- **STOP boundary**：本 Stage不接 `review.py`／自然語言 adapter，不建立 Ψ-value／fRsi／condensation acceptance、material catalog、DXF importer、3D solver或 UI。
- **完成條件**：implementation + focused regression + repository-required validation + PR CI + merge後 main CI + canonical remote read-back全部成立，才關閉此 Hot；任何 backend／dependency／validation blocker則記錄後 fail closed。

## 使用規則

- Future feature、non-blocking debt、等待 trigger 的工作放在 `BACKLOG.md`，不得因存在就自動執行。
- 新工作只有在 current evidence、使用者選擇與 repository authority 已使其成為可執行／critical path 後，才加入本檔。
- Hot work完成並取得必要 validation／remote evidence後，從本檔移除；completed history由 Git history與 canonical artifacts保存。
