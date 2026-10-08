# 目前任務（TASKS）

本檔是 building-envelope-engineering-kb 的 Hot coordination surface，只保存目前可執行或 current critical-path 的工作。

## 目前執行中的工作

### 非線性 FEA 求解器介面（KB-CAND-007）— EVIDENCE GATED

- 使用者已明確選定此 Stage。第一階段為 **CalculiX 研究與 opt-in execution probe**，不是已驗證的玻璃／金屬板非線性分析。
- 已建立外部 executable 的 probe 與 mock regression、benchmark sourcing／license dossier；需要 PR exact-head CI、main CI 及 canonical read-back 方可結束第一階段。
- 第二階段候選：以 Ubuntu 官方 apt 的 CalculiX CCX 2.21-1／CGX 2.21+dfsg-1build1 執行 **真正** NLGEOM truss 與 90° shell；truss 只完成 x/y 解析反力比對；shell 現有增量完整性與 FRD 產生證據，**尚無殼板獨立數值答案與 mesh convergence**。詳見 `references/github-projects/nonlinear-fea-solver-admission.md`。
- 第三階段候選：公開 90° 殼板的 20／40／80 長向網格已由真實 CGX+CCX CI 成功執行，從 FRD／DAT 提取自由端位移及固定端彎矩；以獨立圓弧梁近似檢核最細網格 X／Z 位移，兩項位移及彎矩細化趨勢 PASS。證據與限制見 `references/github-projects/nonlinear-fea-solver-admission.md`；仍須 exact-head PR、merge/main CI 後才算正式完成此 bounded Stage。
- 第四階段：加入 shell90 固定端彎矩 `EIθ/L` 獨立梁理論近似、固定端寄生力／非主軸矩的 bounded 檢查，真實 CalculiX 與既有 CI 均通過；見研究 dossier 與 PR #23。
- 第五階段候選：現有 shell90 新增施加轉角端 `SROT` 截面、兩端節點 `RF` 輸出與 fail-closed 診斷腳本。真實 CalculiX CI 驗證 20／40／80 網格取得結果；兩端截面 `My` 未完全抵消，節點 RF 並非完整旋轉約束反力，**不宣稱 full global balance PASS**。詳見 `references/github-projects/nonlinear-fea-solver-admission.md`。
- 第六階段候選：合成四邊簡支 100×100×1 mm 均佈受壓 `S8R` 板，4／8／16 網格以真實 CCX `NLGEOM` 驗證；小撓度與獨立 Kirchhoff 係數 `0.00406` 比較，16 分割偏差約 0.88%，較大壓力呈現幾何非線性膜內增剛，均有網格細化趨勢。僅限 bounded plate benchmark，待 exact-head CI／main CI closure。詳見 `references/github-projects/nonlinear-fea-solver-admission.md`。
- 第七階段候選：玻璃／鋁板獨立合成面外壓力 benchmark，各有物性及四邊簡支／固定支承；4／8／16 S8R 網格、兩壓力，真實 CCX NLGEOM 已驗證，小撓度 Kirchhoff 獨立理論 5% 以內、網格趨勢及定性大變形增剛。僅為 synthetic elastic proxy，見 `references/github-projects/nonlinear-fea-solver-admission.md`；最終需 exact-head/main CI read-back。
- 第八階段：以玻璃／鋁板合成 `S8R` 受壓板的 `EDGE RF` 輸出作壓力／邊界反力診斷；小壓力下 4／8／16 網格總反力相對 `qA₀` 分別不足約 18.75%／8.85%／4.30%，缺口隨網格細化減少。**物理平衡 gate 未通過**：診斷腳本保留 mismatch，CI SUCCESS 僅代表診斷可重現，不代表平衡驗證 PASS；詳見 `references/github-projects/nonlinear-fea-solver-admission.md`。
- 第九階段候選：依 CalculiX `RF` 輸出語意，新增獨立 S8R 等效節點壓力積分與原始 `EDGE RF` 修正後的小荷載平衡 fail-closed gate。此為 bounded synthetic panels 驗證；只有 exact-head 真實 CCX 與 repo CI 通過、canonical main read-back 後才能正式 admission。大變形 follower pressure 仍未平衡認證。
- **仍待**：釐清 `S8R` 壓力離散／所有反力來源並對照實際 follower pressure 全域合力，完成兩種板件外力與拘束反力獨立平衡，以及真實材料、支承、風壓與失效／屈曲準則、產品資料、大撓度獨立答案和工程 acceptance；維持 `EVIDENCE GATED`，不宣稱 ASTM E1300／ADM capacity。
- 後續 benchmark stage 需 fresh admission；不得自動下載外部二進位檔、執行未知輸入檔或宣稱設計強度 PASS。

## 使用規則

- Future feature、non-blocking debt、等待 trigger 的工作放在 `BACKLOG.md`，不得因存在就自動執行。
- 新工作只有在 current evidence、使用者選擇與 repository authority 已使其成為可執行／critical path 後，才加入本檔。
- Hot work完成並取得必要 validation／remote evidence後，從本檔移除；completed history由 Git history與 canonical artifacts保存。
