# 長期待辦（BACKLOG）

本檔是 building-envelope-engineering-kb 的 Cold Registry，用來避免值得保留的 future capability 因換聊天室、時間間隔或 session context消失。

Cold item **不具 execution authority**。要開始實作前，必須依 current repository authority、current evidence與適用標準重新確認 premise，再 promote 到 `TASKS.md`。

## 狀態語意

- `CANDIDATE`：值得保留與未來重新評估，但尚未承諾一定實作。
- `COMMITTED`：已決定未來需要處理，但目前不是 Hot。
- Persistence 不代表 recommendation 更正確，也不代表可跳過 current research、admission、validation 或 authority gate。

## CANDIDATE

### KB-CAND-001｜耐風設計風壓 V2：低樓層與屋頂區域

- **Why**：目前 `wind_pressure` V1 只支援 `h > 18 m` 外牆 Zone 4／5；低樓層與屋頂仍是明確 capability gap。
- **Evidence**：現有 V1 已將這些 case fail closed；外部 calculator review 顯示使用者實務上會需要 `h <= 18 m` 與 roof Zone 1／2／3。
- **Trigger**：使用者要求計算 V1 範圍外的低樓層／屋頂風壓，或決定擴充完整台灣耐風規範 coverage。
- **Current obligation**：僅保存候選方向；實作前重新以現行官方耐風規範建立 applicability、係數與 regression evidence。

### KB-CAND-002｜玻璃耐風承載力 deterministic capability

- **Why**：風壓算出後，目前 KB 尚不能直接回答指定玻璃 make-up 是否具有足夠 load resistance／deflection performance。
- **Evidence**：KB 已有 glass standards routing，明確將 ASTM E1300 類 load-resistance design 與產品標準分開；外部 calculator review 顯示 glass-strength workflow具有高實用價值。
- **Trigger**：使用者要求由 design pressure 接續做玻璃厚度／承載力檢核，或決定建立 wind-pressure → glass 的 executable chain。
- **Current obligation**：保持 `CANDIDATE`；實作前重新確認 current ASTM E1300 edition、可合法 machine-encode 的方法與 validation examples，不複製外部網站未驗證演算法。

### KB-CAND-003｜鋁直料／橫料構件強度檢核

- **Why**：KB 已有 beam solver 與 mullion/transom methodology，但缺少 aluminum member capacity／local-buckling execution layer。
- **Evidence**：現有 calculator 可求 beam response；外部 calculator review 顯示「風壓 → line load → member capacity」是常用工作流。
- **Trigger**：需要把現有 beam result 接到鋁構件 flexure／shear／local element capacity。
- **Current obligation**：實作前確認 current Aluminum Design Manual／專案 design basis、alloy/temper與 section classification；不得把外部 calculator 的簡化公式當 authority。

### KB-CAND-004｜自攻螺絲連接容量檢核

- **Why**：KB 已有 fastener-group demand 與 screw pull-out/thread-engagement knowledge，但尚無 code／product-evidence-based pull-out、pull-over、bearing capacity kernel。
- **Evidence**：現有 connection methodology已區分 screw body、parent material、pull-out／thread stripping與 bearing 等 failure modes；外部 calculator review顯示可形成完整 connection chain。
- **Trigger**：使用者需要從 fastener-group demand 接續檢核 individual screw／connected material failure modes。
- **Current obligation**：先建立 current AAMA/FGIA、Aluminum Design Manual、manufacturer/evaluation-report authority mapping與適用範圍，再決定 deterministic formulas。

### KB-CAND-005｜二維熱橋 deterministic solver

- **Why**：KB 現有 thermal／condensation knowledge仍是 methodology；缺少 2D steady-state conduction、surface temperature、heat-flow與 Ψ-value execution capability。
- **Evidence**：現有 thermal baseline 已要求 assembly-level與 thermal-bridge analysis；外部 calculator review顯示 ISO 10211 類 benchmark-driven 2D solver可提供實質能力。
- **Trigger**：需要計算 bracket、slab edge、frame／insulation interface等局部熱橋或 condensation screening。
- **Current obligation**：先研究 mature solver/library reuse、ISO 10211 current requirements與 benchmark suite；不為形式自建 FEA solver。

### KB-CAND-006｜玻璃熱傳與結露 screening

- **Why**：常見 façade 問題需要由已知 U-value／optical properties／boundary conditions推導表面溫度、fRsi或 dew-point risk。
- **Evidence**：KB 已有 thermal-and-condensation baseline；外部 calculator review顯示 U-value／condensation screening可作為較輕量 executable capability。
- **Trigger**：使用者提供可追溯的 glazing thermal properties並要求 thermal／condensation calculation。
- **Current obligation**：只考慮 verified user/project/manufacturer inputs；不吸收外部網站未完成原廠追溯的產品 catalog。

### KB-CAND-007｜玻璃／金屬板非線性 FEA execution adapter

- **Why**：KB 已有 glass 與 metal-panel FEA governance，但沒有可直接執行的 validated nonlinear solver route。
- **Evidence**：現有 canonical pages已定義 mesh、nonlinearity、boundary、reaction與validation要求；外部 calculator review顯示此能力有價值，但 implementation／validation成本高。
- **Trigger**：出現無法由既有 analytical helpers可靠處理、且 repeated consumer justification 足夠的 nonlinear glass／sheet-metal use case。
- **Current obligation**：優先 bounded reuse discovery與 solver adapter／benchmark architecture；不預設自行開發完整 FEA engine。
