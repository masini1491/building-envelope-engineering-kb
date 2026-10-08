# 目前任務（TASKS）

本檔是 building-envelope-engineering-kb 的 Hot coordination surface，只保存目前可執行或 current critical-path 的工作。

## 目前執行中的工作

### 非線性 FEA 求解器介面（KB-CAND-007）— EVIDENCE GATED

- 使用者已明確選定此 Stage。第一階段為 **CalculiX 研究與 opt-in execution probe**，不是已驗證的玻璃／金屬板非線性分析。
- 已建立外部 executable 的 probe 與 mock regression、benchmark sourcing／license dossier；需要 PR exact-head CI、main CI 及 canonical read-back 方可結束第一階段。
- 仍待：完整公開 benchmark materialization、exact solver version、實際 NLGEOM run、位移／反力獨立驗證、mesh convergence、玻璃／金屬板各自的模型適用性。缺這些證據時維持 `EXECUTION_ONLY_NOT_NUMERICALLY_VALIDATED`，不可升格為完整工程 execution capability。
- 後續 benchmark stage 需 fresh admission；不得自動下載外部二進位檔、執行未知輸入檔或宣稱設計強度 PASS。

## 使用規則

- Future feature、non-blocking debt、等待 trigger 的工作放在 `BACKLOG.md`，不得因存在就自動執行。
- 新工作只有在 current evidence、使用者選擇與 repository authority 已使其成為可執行／critical path 後，才加入本檔。
- Hot work完成並取得必要 validation／remote evidence後，從本檔移除；completed history由 Git history與 canonical artifacts保存。
