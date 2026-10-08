# 目前任務（TASKS）

本檔是 building-envelope-engineering-kb 的 Hot coordination surface，只保存目前可執行或 current critical-path 的工作。

## 目前執行中的工作

### 風壓 P1 correctness 與既有 Cold 對帳（KB-WIND-RECONCILE）

- 使用者於 2026-10-08 授權：檢查與修正 103 年規範第 3.2 節部分封閉式正內風壓 `q(h)`／`q(zh₀)` 選擇；保留合法 `q(h)` 預設，選用 `q(zh₀)` 時需確認開口最高高度、僅適用 `h > 18 m` 的相應路由；負內風壓仍採 `q(h)`。
- 同步修正 `taiwan-wind-code-103-v2.json` 上層 scope 與 Zone 3 直接吸力已納入之事實，明確保留近似圖面轉錄與 suction-only 限制。
- 補官方 Figure 3.2 讀圖的獨立中間點檢查與坡度／內風壓 route regressions；不能拿相同端點推導的期望值假裝獨立驗證。
- 更新 Cold：已完成的 KB-CAND-006、KB-CAND-008 不得留作未執行候選；history 由 Git/README/dossier 保留。
- 完成條件：候選測試、PR exact-head CI、merge、main CI、canonical read-back；禁止相鄰功能擴充。


## 使用規則

- Future feature、non-blocking debt、等待 trigger 的工作放在 `BACKLOG.md`，不得因存在就自動執行。
- 新工作只有在 current evidence、使用者選擇與 repository authority 已使其成為可執行／critical path 後，才加入本檔。
- Hot work完成並取得必要 validation／remote evidence後，從本檔移除；completed history由 Git history與 canonical artifacts保存。
