# 目前任務（TASKS）

本檔是 building-envelope-engineering-kb 的 Hot coordination surface，只保存目前可執行或 current critical-path 的工作。

## 目前執行中的工作

### 二維熱橋 solver reuse 與 benchmark admission（P2／KB-P2-C）

- **來源**：原 `KB-CAND-005`；使用者已明確要求進入 P2，並在完成 P1 Wind V2 correctness read-back 後 promote。
- **目標**：在不自行重造完整 FEA engine、不複製受版權標準的前提下，關閉 2D steady-state thermal-bridge solver 的 reusable backend、validation benchmark 與 production boundary。
- **Current authority**：
  - ISO 官方確認 `ISO 10211:2017`（Edition 2）仍為 current，適用於 thermal bridge 的 2D/3D heat-flow 與 surface-temperature numerical calculation。
  - COMSOL 公開 application examples 提供 ISO 10211:2017 Case 1／Case 2 的可公開交叉驗證 geometry、boundary conditions 與 expected-result reproduction。
- **Reuse decision**：
  - `kinnala/scikit-fem`：`ADAPT_CANDIDATE`。pure Python FEM assembler，BSD-3-Clause，Python 3.10+，minimal dependencies 為 NumPy／SciPy；current reviewed head `53d7555ec355477e3b88f6397e206979b689d14c`。
  - `schoenenbach/thermal-bridge`：`REFERENCE_ONLY`。已有 ISO test claim，但為 AGPLv3；不得直接複製／vendor 進本 repo 或用其實作取代本 repo 自己的 engineering contract。
- **本 Stage 只做**：
  1. 以 public benchmark evidence 定義 Case 1／Case 2 的最小 validation contract。
  2. 驗證 scikit-fem 是否能作 isolated numerical backend，且不要求吸收其 docs example code。
  3. 固定 production input/output boundary：geometry／mesh、material conductivity、thermal boundary conditions、temperature field、boundary heat flow、validation status。
  4. 明確區分「numerical solver verified」與「ISO 10211 compliant project calculation」；在完整 applicable validation 未成立前不得宣稱後者。
  5. 若 benchmark／dependency／license 任一 gate 不成立，回到 `COMMITTED / BLOCKED`，不得改用未驗證自製 solver 補洞。
- **STOP boundary**：本 Stage 不建立 Ψ-value project compliance、condensation acceptance criterion、material catalog、DXF importer、3D solver或 UI。
- **完成條件**：reuse／benchmark evidence 可重現且 current validation 全綠後，才另行 admission production kernel；否則保存 blocker後 STOP。

## 使用規則

- Future feature、non-blocking debt、等待 trigger 的工作放在 `BACKLOG.md`，不得因存在就自動執行。
- 新工作只有在 current evidence、使用者選擇與 repository authority 已使其成為可執行／critical path 後，才加入本檔。
- Hot work完成並取得必要 validation／remote evidence後，從本檔移除；completed history由 Git history與 canonical artifacts保存。
