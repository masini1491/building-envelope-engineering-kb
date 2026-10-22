# 長期待辦（BACKLOG）

本檔是 building-envelope-engineering-kb 的 Cold Registry，用來避免值得保留的 future capability 因換聊天室、時間間隔或 session context消失。

Cold item **不具 execution authority**。要開始實作前，必須依 current repository authority、current evidence與適用標準重新確認 premise，再 promote 到 `TASKS.md`。

## 狀態語意

- `CANDIDATE`：值得保留與未來重新評估，但尚未承諾一定實作。
- `COMMITTED`：已決定未來需要處理，但目前不是 Hot。
- `COMMITTED / BLOCKED`：已決定需要處理，但 current authority／rights／validation evidence 不足以安全實作。
- Persistence 不代表 recommendation 更正確，也不代表可跳過 current research、admission、validation 或 authority gate。

## 已承諾（COMMITTED）

### 玻璃耐風承載力 deterministic capability（KB-P1-B）

- **Status**：`COMMITTED / BLOCKED`。目前沒有合法且足以實作 E1300-24 exact kernel 的 public data path。
- **Current evidence**：ASTM E1300-24 為 current load-resistance routing；`normanrichardson/structuralglass`（MIT）可作 mechanics reference，但不是 current E1300-24 exact chart engine。
- **Boundary**：不得把第三方標準 PDF／轉錄表、surrogate 或 classical plate-theory 包裝成 ASTM E1300 exact。
- **Trigger**：取得 current E1300-24 可合法 machine-encode 的 exact data、官方／授權 reusable implementation，或其他足以關閉同等方法與 validation boundary 的 evidence。

### 鋁直料／橫料構件強度檢核（P2／KB-P2-A）

- **Status**：`COMMITTED / BLOCKED`。
- **Current evidence**：Aluminum Association 目前仍以 `Aluminum Design Manual 2020` 作結構鋁設計出版物；其公開說明確認 ADM 包含 structural-component strength、buckling、weld-affected strength、concentrated-force與 screw-chase pull-out 等 provisions，但完整設計規則為付費出版物。
- **Existing safe capability**：本 repo 已有 beam response、required section property、user-supplied allowable/capacity utilization與 local-demand arithmetic；這些 capability 不自行衍生 ADM allowable/design strength。
- **Blocker**：目前沒有足夠的 public primary evidence 可合法 machine-encode ADM member-strength／local-buckling exact equations、alloy/temper design values與完整 applicability。
- **Rejected substitute**：不得把 `M/S`、`V/A`、user-supplied allowable 比較包裝成「ADM aluminum member capacity」，也不另造與既有 helpers 重疊的假性 strength kernel。
- **Trigger**：取得 licensed/project-provided ADM design basis與可合法使用的必要數值／equations，或可驗證、license-compatible 的 current implementation。

### 自攻螺絲連接容量檢核（P2／KB-P2-B）

- **Status**：`COMMITTED / BLOCKED`。
- **Current evidence**：FGIA store 仍將 `AAMA TIR-A9-14 — Design Guide for Metal Cladding Fasteners` 標為 Active，並列 2015 errata 與 2020 addendum；其用途正是 curtain-wall framing/component fastener selection。
- **Existing safe capability**：本 repo 已有 fastener-group demand、projected bearing demand、independent shear/tension utilization及 externally-established thread-engagement comparison。
- **Blocker**：current TIR-A9 design data／tables與 applicable ADM screw/parent-material resistance provisions並非 public machine-encodable authority；manufacturer/evaluation-report capacity仍需 project/product-specific evidence。
- **Rejected substitute**：不得從舊 TIR-A9、第三方 calculator或 generic screw formula猜出 pull-out／pull-over／bearing capacity。
- **Trigger**：取得 current licensed TIR-A9/ADM design basis與 exact fastener/product evidence，或可驗證且授權相容的 current implementation。

## 候選（CANDIDATE）

### 受限非線性 FEA 後續構造能力（KB-CAND-007）

- **Current evidence**：現有受限 CalculiX 執行介面已通過合成 S8R 鋁板之位移、外插／平均應力應變及重建平移支承需求等真實 CI 研究檢查；不再沿用「沒有 validated nonlinear execution route」的過時前提。這些研究通過不等於真實帷幕牆鋁板工程 acceptance；本次受限 C3D20R 研究已由 PR #136 整合；目前無 Hot，詳細歷史請見 Git history／PR #131、#135、#136。
- **CANDIDATE／Trigger**：待現有四邊固定平板的可觀測位移／應力基準足以描述限制，並明確取得非合成工況所需的構造、邊界條件、荷載路徑及獨立驗證計畫，再分別考慮折邊／加勁肋、實際支承／扣件、局部挫屈及初始缺陷等模型；每項均須獨立 admission，不因已完成 synthetic NLGEOM 即自動實作。
- **Boundary**：不自行開發通用 FEA engine；不把平均節點應力、重建平移反力、材料牌號或供應商聲明直接升格為 ADM／其他規範強度及構件容量。

### 鋁板完整塑性本構研究（KB-CAND-007-MATERIAL-PLASTICITY）

- **Status**：`CANDIDATE / EVIDENCE GATED`。Stage 49–50 已有合成 C3D8 塑性／卸載 oracle，Stage 52 已有私人硬化點列結構預檢，**不代表 3003-H14／3004-H12／3004-O 真實塑性材料卡已驗證**。
- **Why deferred**：一般彈性應力、撓度與受限支承需求研究不必以完整拉伸硬化曲線作為先決條件；優先補足幾何／邊界條件／場值物理基準，而不是反覆增加合成塑性測試。
- **Trigger**：有實際需要超降伏、塑性重分布、卸載殘餘變形或成形行為的明確工況，並取得對應產品／板厚／temper／加工狀態、方向、批次及使用權利相符的真實應力–應變原始資料及獨立驗證方法。
- **禁止推論**：不得以降伏強度、抗拉強度與伸長率推造完整硬化曲線；不得在未完成材料、支承、失效準則及正式設計依據 admission 前宣稱工程容量。

### 深入 MPC／RF 反力與非共線力矩重建（KB-CAND-007-MPC）

- **Status**：`CANDIDATE / DEFERRED`，依 2026-10-14 使用者工程應用優先序，Stage 70 非共線力矩與一般 MPC／rigid-body RF 研究不再是 current Hot。
- **Evidence**：Stage 68／69 已確認合成 SPRING2 與兩項 `*EQUATION` 的受限單軸位移、固定端 raw RF、外力解析平衡，但原始 slave/master RF 不是已獨立量得的 MPC constraint multiplier；元素力無可採信的原生數值列。技術原始證據在 `references/github-projects/nonlinear-fea-solver-admission.md`。
- **Trigger**：具體帷幕鋁板／加勁肋／連接研究的工程輸出無法由現有受限模型可靠提供，且能提出真正需 MPC moment／constraint-reaction 的力學問題、獨立解析／試驗 oracle 與可辨識的工程收益。
- **Boundary**：Cold 不授權自動 Stage 70 執行，不由局部單軸 PASS 推論任意 MPC／六分量平衡或扣件設計力。


### KB-CAND-007｜研究結案後的工程准入與證據保存

- **Status**：`CANDIDATE / EVIDENCE BLOCKED`；非目前 Hot，不授權自動研究或新模擬。合成 C3D20R n8／n16／n24、固定四站 Z-only 雙向 SPRING2、受限輸入、抗拉統計候選與繁中研究摘要，已以 PR #136／main `f808bfaec7c45c86a001ad25732b1eb3939a526b` 交付數值研究工具；`RESEARCH_COMPLETED` 只適用於驗證過的合成研究，不等於真實鋁植釘或工程設計認可。
- **保留禁止升格狀態**：`ENGINEERING_ACCEPTANCE_NOT_ADMITTED`、`CONTACT_NOT_ADMITTED`、`MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED`。原 S8R 不平衡研究及 fail-closed CI 留 PR #131／Issue #134，PR #135 保留原始合成研究脈絡；不合併其失敗依賴。
- **Trigger**：未來若確實需要實際設計，須取得能對應試體、構造及方向的接頭荷載—位移／滑移（含拉、壓、剪與開離）及獨立驗證、專案風壓／組合、角碼及實際支承、材料與合法適用設計標準；另案定義模型與工程 acceptance。既有破壞荷載統計不能推回彈簧剛度；`(mean−sample SD)/SF` 與合成站點力比值不是設計使用率。
- **證據保留提醒**：Hot 2 原始求解 Artifact #12401885093，SHA-256 `d35d73f6b9f0d5f94f45e53b1c81c607d9839c77c25ea54ba654e033993933a7`，GitHub 顯示 2026-11-05 到期；PR #136 exact-head research CI #39735595282、Repository CI #39735595238、既有 FEA 探針 #39735595096 均 SUCCESS。Artifact 過期後不能宣稱仍可從原連結重播；若未來需要重驗，須取得並完整驗證具相同輸入契約與求解器來源的可信原始 solver evidence。保存期限提醒不形成自動執行／擴張權限。
