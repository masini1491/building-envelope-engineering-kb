# 目前任務（TASKS）

本檔是 ChatGPT-Only 專案的 Hot coordination owner；完整歷史、方法及 PR/CI provenance 以 Git history 與 canonical dossier 為準，勿將本檔當作第二份 changelog。

## 目前執行中的工作

### 非線性 FEA 求解器介面（KB-CAND-007）— EVIDENCE GATED

- **Current admitted capability**：已完成 Stage 1–44（含 Stage 40–44 受限鋁板研究擴充），固定合成算例入口為 `tests/fea_benchmark/envelope_panels/run_synthetic_panel.py`，只允許 Repo 自建 synthetic glass／aluminum、S8R NLGEOM、P1 high-load、網格 4／8／16；必須 opt-in、外部可信 CCX、空白工作目錄、求解完成及內力／外力診斷都成立才輸出 `SYNTHETIC_BENCHMARK_EVIDENCE_PASS`。Stage 33 PR #57 的六組真實 CI、Stage 35 PR #59 的 SHA-256 provenance 以及 Stage 36 PR #60 的跨工作目錄重播與各自 main CI 均成立；**並非任何工程 acceptance**。
- **已通過的研究邊界**：合成 S8R 板件的已知拘束三向平移力平衡、真正 expanded P1 follower pressure、expanded geometric-moment partition 與 CalculiX 2.21 隔離 GPL 插樁之 MEANROT／cascade term-count observations；不得把 reconstructed supports、projected RF 或 internal `fmpc` 當成獨立支承反力矩。詳見 `references/github-projects/nonlinear-fea-solver-admission.md`。
- **目前仍缺**：完整 MPC term identity lineage、獨立旋轉支承反力／反力矩、一般六分量全域平衡； arbitrary shell/solid/contact、材料非線性、屈曲、幾何缺陷、真實專案支承／荷載／產品強度與 ASTM E1300／ADM capacity 均未 admission。
- **已選定鋁板研究方向**：Stage 37（PR #62）新增 `run_aluminum_research.py`、`aluminum_research_input.py`；受限輸入為矩形、四邊固定、等向線彈性、均布 P1 pressure、使用者給定 E／ν／厚度及 4／8／16 S8R 網格，不接受任意 deck。Stage 38（PR #63）以不同寬高／厚度／面壓和真實 CCX 驗證參數映射。Stage 40（PR #65）完成低荷載一項 Ritz 近似與 4／8／16 網格趨勢研究；Stage 41（PR #66）增加最終節點位移與重建平移反力 JSON；Stage 42（PR #67）加入 expanded-node 外插／平均 S、E 六分量觀測；Stage 43（PR #68）通過兩組壓力獨立 CCX 逐節點比例縮放；Stage 44（PR #69）通過低荷載法向 Hooke compliance 交叉比對。 材料研究優先以 3003-H14／3004-H12／3004-O 為主；公開供應商數值僅為 research provenance，未具可用於 ADM design/capacity 的來源與適用條件，無自動材料參數或強度判定。**這些都是 synthetic numeric research，非絕對場值／材料強度驗證。** **Stage 47 研究證據**：3003-H14 液壓成形試驗、3004-O FLC／成形性實驗及 3004-H12 型錄已建立各自來源界線，**尚無三種目標質別可直接用於 CCX 的完整硬化曲線**，不可合成或轉用不同 temper；canonical 研究詳見 nonlinear FEA dossier。 **最新研究驗證**：Stage 48／PR #79 已通過三種質別的合成 E／ν／厚度／面壓標籤隔離與真實 CCX 結果一致性；Stage 49／PR #80 已通過合成 C3D8 彈性、塑性獨立本構 oracle；Stage 50／PR #81 已通過相同合成材料塑性峰值後部分卸載的兩步驟 CCX 與獨立應力回復／PEEQ 不變檢驗。上述數值**均非實際中鋁材料曲線或工程容量**；所有材料塑性與 capacity admission 維持 NOT_ADMITTED。 **下一道門**：進一步擴張 material models、support/edge conditions、獨立數值 benchmark 或真實工程輸入前必須 separately admission；ADM member capacity 仍 COMMITTED / BLOCKED，需有效授權設計依據，不能直接執行強度設計。
- **工程狀態**：`EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。只要未取得充分工程觀測證據，就維持研究用途，不宣稱玻璃或鋁板可進入正式強度設計。

## 使用規則

Cold／trigger-based future work 使用 `BACKLOG.md`；Hot 完成並取得 exact-head/main CI、canonical remote read-back 後才收斂。完整研究來源、Stage 49–50 的驗證與適用限制以單一 canonical dossier 及 Git history 為準。
