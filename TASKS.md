# 目前任務（TASKS）

本檔是 ChatGPT-Only 專案的 Hot coordination owner；完整歷史、方法及 PR/CI provenance 以 Git history 與 canonical dossier 為準，勿將本檔當作第二份 changelog。

## 目前執行中的工作

### 非線性 FEA 求解器介面（KB-CAND-007）— EVIDENCE GATED

- **Current admitted capability**：已完成 Stage 1–33，最新受限執行入口為 `tests/fea_benchmark/envelope_panels/run_synthetic_panel.py`，只允許 Repo 自建 synthetic glass／aluminum、S8R NLGEOM、P1 high-load、網格 4／8／16；必須 opt-in、外部可信 CCX、空白工作目錄、求解完成及內力／外力診斷都成立才輸出 `SYNTHETIC_BENCHMARK_EVIDENCE_PASS`。Stage 33 PR #57 的六組真實 CI 與合併後 main CI 成立；**並非任何工程 acceptance**。
- **已通過的研究邊界**：合成 S8R 板件的已知拘束三向平移力平衡、真正 expanded P1 follower pressure、expanded geometric-moment partition 與 CalculiX 2.21 隔離 GPL 插樁之 MEANROT／cascade term-count observations；不得把 reconstructed supports、projected RF 或 internal `fmpc` 當成獨立支承反力矩。詳見 `references/github-projects/nonlinear-fea-solver-admission.md`。
- **目前仍缺**：完整 MPC term identity lineage、獨立旋轉支承反力／反力矩、一般六分量全域平衡； arbitrary shell/solid/contact、材料非線性、屈曲、幾何缺陷、真實專案支承／荷載／產品強度與 ASTM E1300／ADM capacity 均未 admission。
- **下一個 bounded critical path**：以 Stage 33 adapter 的 `failure-atomic` execution/status/evidence schema、solver identity 與跨 working-directory 可重現操作為目標研究正式介面可行性。任何超出 canonical six-fixture model 的輸入能力都需新的 method/source/verification admission，不能因目前 CI SUCCESS 自動擴大。
- **工程狀態**：`EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。只要未取得充分工程觀測證據，就維持研究用途，不宣稱玻璃或鋁板可進入正式強度設計。

## 使用規則

Cold／trigger-based future work 使用 `BACKLOG.md`；Hot 完成並取得 exact-head/main CI、canonical remote read-back 後才收斂。完整 Stage 1–33 研究來源與限制以單一 canonical dossier 為準。
