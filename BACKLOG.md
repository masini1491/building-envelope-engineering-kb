# 長期待辦（BACKLOG）

本檔僅保存未來值得重新評估的工作、實際阻塞與啟動條件。此處不是可直接執行的工作清單；提升至 [TASKS.md](TASKS.md) 前，必須重新核對當前證據、專案治理與授權。

## 已承諾（COMMITTED）

### 玻璃耐風承載力檢核（KB-P1-B）

- **狀態**：`COMMITTED / BLOCKED`。
- **阻塞**：缺少具合法使用權、適用版本且足以實作 ASTM E1300 exact 計算的完整設計資料或可信實作。
- **Trigger**：取得可合法 machine-encode 的適用標準資料／官方或授權實作，並建立獨立驗證。
- **邊界**：第三方轉錄表、近似板理論或 `structuralglass` 力學參考不得冒稱 E1300 exact 計算。

### 鋁直料／橫料構件強度檢核（KB-P2-A）

- **狀態**：`COMMITTED / BLOCKED`。
- **阻塞**：缺少合法可用且對應材料／質別／構件的 Aluminum Design Manual 設計規則、參數與適用性驗證。
- **Trigger**：取得可授權使用的設計依據／經驗證實作及獨立測試。
- **邊界**：既有梁反應、截面需求與使用者提供容量的比較，不等於自動推導 ADM 構件強度。

### 自攻螺絲連接容量檢核（KB-P2-B）

- **狀態**：`COMMITTED / BLOCKED`。
- **阻塞**：缺少合法可用、版本與產品條件相符的 AAMA TIR-A9／ADM 設計依據及扣件容量證據。
- **Trigger**：取得授權標準資料、實際扣件／母材適用證據和可獨立驗證的計算方法。
- **邊界**：既有螺絲群荷載需求及外部容量比較，不得冒稱已驗證的拔出、拉穿或承壓容量。

## 候選（CANDIDATE）

### 實際板肋、支承及植釘工程模型（KB-CAND-007）

- **狀態**：`CANDIDATE / EVIDENCE BLOCKED`。受限 C3D20R 合成數值研究已由 [PR #136](https://github.com/masini1491/building-envelope-engineering-kb/pull/136) 交付，`RESEARCH_COMPLETED` 僅適用於該模型；正式工程仍為 `ENGINEERING_ACCEPTANCE_NOT_ADMITTED`。
- **Trigger**：有實際工程需求，並取得對應構造及拉／壓／剪／開離行為的接頭荷載—位移／滑移證據、材料與適用設計依據、專案荷載組合及真實支承條件，建立獨立驗證後才另案考慮折邊、加勁肋、接頭、局部挫屈等能力。
- **邊界**：既有 0／50／500 N/mm 為未校準合成彈簧；破壞荷載統計不能反推剛度，有號站點力比值不是設計使用率；不得以合成 CI PASS 替代工程准入。
- **研究與後續問題**：數值範圍見 PR #136，未解 S8R 接觸與獨立平衡見 [Issue #134](https://github.com/masini1491/building-envelope-engineering-kb/issues/134)；`CONTACT_NOT_ADMITTED` 仍有效。重播原始求解證據依賴具有保留期限的 GitHub Artifact，後續重驗不得省略原始求解來源核對。

### 鋁板塑性材料本構（KB-CAND-007-MATERIAL-PLASTICITY）

- **狀態**：`CANDIDATE / EVIDENCE GATED`；既有合成塑性／卸載研究不代表 3003-H14、3004-H12、3004-O 的真實材料模型已驗證。
- **Trigger**：出現須分析超降伏、塑性重分布、卸載殘留變形或成形的實際問題，並取得構造與質別匹配、合法可用的真實應力—應變資料及獨立驗證方法。
- **邊界**：不能從降伏、抗拉強度及伸長率推造完整硬化曲線；原研究見 [非線性 FEA 研究紀錄](references/github-projects/nonlinear-fea-solver-admission.md)。

### 接觸反力與 MPC／S8R 力矩重建（KB-CAND-007-MPC）

- **狀態**：`CANDIDATE / DEFERRED`；不是目前 Hot。
- **Trigger**：真實工程輸出確實需要 constraint reaction／非共線力矩且具獨立力學 oracle、工程收益與新證據，再由 [Issue #134](https://github.com/masini1491/building-envelope-engineering-kb/issues/134) 重新評估。
- **邊界**：既有合成 SPC／MPC 單軸 PASS 不等於獨立 MPC multiplier、S8R 接觸平衡或一般六分量反力驗證；`MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED`。
