# 長期待辦（BACKLOG）

本檔是 building-envelope-engineering-kb 的 Cold Registry，用來避免值得保留的 future capability 因換聊天室、時間間隔或 session context消失。

Cold item **不具 execution authority**。要開始實作前，必須依 current repository authority、current evidence與適用標準重新確認 premise，再 promote 到 `TASKS.md`。

## 狀態語意

- `CANDIDATE`：值得保留與未來重新評估，但尚未承諾一定實作。
- `COMMITTED`：已決定未來需要處理，但目前不是 Hot。
- Persistence 不代表 recommendation 更正確，也不代表可跳過 current research、admission、validation 或 authority gate。

## 已承諾（COMMITTED）

### 玻璃耐風承載力 deterministic capability（KB-P1-B）

- **Status**：`COMMITTED / BLOCKED`。P1-A Wind V2 已完成；本項已完成 current exact-method／reuse admission，但目前沒有合法且足以實作 E1300-24 exact kernel 的 public data path，因此保持 Cold，不建立假性 Hot work。
- **Origin**：原 `KB-CAND-002`；使用者已明確選定 P1，故未來仍需處理，不因本次 blocker退回一般 candidate。
- **Why**：風壓算出後，目前 KB 尚不能直接回答指定玻璃 make-up 是否具有足夠 ASTM E1300 load resistance／deflection performance。
- **Current evidence**：KB current standard owner確認 ASTM E1300-24 為現行 load-resistance routing。bounded reuse discovery確認 `normanrichardson/structuralglass`（MIT）適合作 mechanics／stress-deflection ADAPT reference，但不是 E1300-24 exact load-resistance chart engine；另檢查的 E1300 surrogate、舊版 implementation與 classical plate-theory替代路徑都只能作 REFERENCE-ONLY。
- **Authority / rights blocker**：目前公開一手來源不足以合法、完整地重建 E1300-24 所需 chart/table data。第三方 repository 中的標準 PDF、轉錄表或 surrogate calibration不得直接吸收到 public KB；近似 plate theory／NCSEA mechanics也不得改名成 ASTM E1300 exact。
- **Rejected substitute**：本次已明確評估「先做 generic glass plate-response／user-supplied allowable adapter」作為 P1替代；依現有 engineering goal與設計占卜均不採用，因其不能回答原 P1 的 E1300 load-resistance問題，且會製造 capability naming／authority混淆。
- **Trigger**：取得 current E1300-24 可合法 machine-encode 的 exact chart/table data、官方／授權 reusable implementation，或其他足以關閉同等方法與驗證邊界的 evidence後，fresh-reconcile並 promote到 `TASKS.md`。
- **Current obligation**：保留 blocker與 reuse findings；未達 trigger前不要重複用 surrogate／plate-theory繞過 exact-method gate。

## 候選（CANDIDATE）

### 鋁直料／橫料構件強度檢核（KB-CAND-003）

- **Why**：KB 已有 beam solver 與 mullion/transom methodology，但缺少 aluminum member capacity／local-buckling execution layer。
- **Evidence**：現有 calculator 可求 beam response；外部 calculator review 顯示「風壓 → line load → member capacity」是常用工作流。
- **Trigger**：需要把現有 beam result 接到鋁構件 flexure／shear／local element capacity。
- **Current obligation**：實作前確認 current Aluminum Design Manual／專案 design basis、alloy/temper與 section classification；不得把外部 calculator 的簡化公式當 authority。

### 自攻螺絲連接容量檢核（KB-CAND-004）

- **Why**：KB 已有 fastener-group demand 與 screw pull-out/thread-engagement knowledge，但尚無 code／product-evidence-based pull-out、pull-over、bearing capacity kernel。
- **Evidence**：現有 connection methodology已區分 screw body、parent material、pull-out／thread stripping與 bearing 等 failure modes；外部 calculator review顯示可形成完整 connection chain。
- **Trigger**：使用者需要從 fastener-group demand 接續檢核 individual screw／connected material failure modes。
- **Current obligation**：先建立 current AAMA/FGIA、Aluminum Design Manual、manufacturer/evaluation-report authority mapping與適用範圍，再決定 deterministic formulas。

### 二維熱橋 deterministic solver（KB-CAND-005）

- **Why**：KB 現有 thermal／condensation knowledge仍是 methodology；缺少 2D steady-state conduction、surface temperature、heat-flow與 Ψ-value execution capability。
- **Evidence**：現有 thermal baseline 已要求 assembly-level與 thermal-bridge analysis；外部 calculator review顯示 ISO 10211 類 benchmark-driven 2D solver可提供實質能力。
- **Trigger**：需要計算 bracket、slab edge、frame／insulation interface等局部熱橋或 condensation screening。
- **Current obligation**：先研究 mature solver/library reuse、ISO 10211 current requirements與 benchmark suite；不為形式自建 FEA solver。

### 玻璃熱傳與結露 screening（KB-CAND-006）

- **Why**：常見 façade 問題需要由已知 U-value／optical properties／boundary conditions推導表面溫度、fRsi或 dew-point risk。
- **Evidence**：KB 已有 thermal-and-condensation baseline；外部 calculator review顯示 U-value／condensation screening可作為較輕量 executable capability。
- **Trigger**：使用者提供可追溯的 glazing thermal properties並要求 thermal／condensation calculation。
- **Current obligation**：只考慮 verified user/project/manufacturer inputs；不吸收外部網站未完成原廠追溯的產品 catalog。

### 玻璃／金屬板非線性 FEA execution adapter（KB-CAND-007）

- **Why**：KB 已有 glass 與 metal-panel FEA governance，但沒有可直接執行的 validated nonlinear solver route。
- **Evidence**：現有 canonical pages已定義 mesh、nonlinearity、boundary、reaction與validation要求；外部 calculator review顯示此能力有價值，但 implementation／validation成本高。
- **Trigger**：出現無法由既有 analytical helpers可靠處理、且 repeated consumer justification 足夠的 nonlinear glass／sheet-metal use case。
- **Current obligation**：優先 bounded reuse discovery與 solver adapter／benchmark architecture；不預設自行開發完整 FEA engine。
