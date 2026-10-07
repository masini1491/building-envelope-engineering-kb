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

### 高樓層屋頂 Zone 1／2／3 wind-pressure coverage（KB-CAND-008）

- **Why**：current Wind V2 已支援 `h > 18 m` 外牆與 `h <= 18 m` 屋頂，但官方 Figure 3.2 同時定義 `h > 18 m` 屋頂 Zone 1／2／3。
- **Trigger**：需要 `h > 18 m` 屋頂局部構材／外部被覆物設計風壓。
- **Current obligation**：另行設計 Figure 3.2 roof coefficient/routing；不得順手併入其他 Stage。

### 玻璃熱傳與結露 screening（KB-CAND-006）

- **Why**：需要由已知 U-value／boundary conditions推導表面溫度、fRsi或 dew-point risk。
- **Current obligation**：只使用 verified project/manufacturer inputs；不吸收未追溯產品 catalog。

### 玻璃／金屬板非線性 FEA execution adapter（KB-CAND-007）

- **Why**：現有 glass／metal-panel FEA governance沒有 validated nonlinear execution route。
- **Current obligation**：優先 solver adapter／benchmark architecture；不預設自行開發完整 FEA engine。
