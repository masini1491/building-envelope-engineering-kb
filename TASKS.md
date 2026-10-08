# 目前任務（TASKS）

本檔是 building-envelope-engineering-kb 的 Hot coordination surface，只保存目前可執行或 current critical-path 的工作。

## 目前執行中的工作

### 高樓層屋頂局部風壓（KB-CAND-008）— PARTIAL / SOURCE-GATED

- 使用者已於 2026-10-08 授權本項；bounded implementation PR #14 已 merge 至 main `373c2e8030921ecf556def39f14ccddd8e93c6cf`，其 exact-main CI `37712301407` 兩個 jobs SUCCESS。
- 已納入：h > 18 m、坡度 ≤10°、屋頂四周女兒牆高度嚴格 >0.9 m 且明確啟用 Zone 3→Zone 2 時，依內政部建築研究所示範例 formulaized Figure 3.2 Zone 1/2 負壓係數計算 suction-only；坡度 >10°～45° 依 Figure 3.2 註 5 路由 Figure 3.1(c)/(d)。
- **仍未完成**：無合格女兒牆時 Figure 3.2 Zone 3 原始曲線的可靠 machine transcription、獨立端點／中間值 cross-check；此類輸入目前必須 `UNSUPPORTED_MODEL`。Figure 3.2 low-slope 的屋頂正壓也不會猜測。
- 下一步只有在原始官方曲線或可合法追溯的授權表格可精確核對時，才能繼續 general coverage；不得以外牆係數、另一法規圖表或臆測曲線補齊。
- 如無新的 source evidence，此項保持 `SOURCE-GATED`，不宣稱 full feature admission，也不自動放寬工程適用範圍。

已完成的玻璃表面溫度／結露初篩（KB-CAND-006）不再占用 Hot：production PR #13 merge `e6652f5516713f56e6e84209fc62e79c5738ef46`，exact-main CI `37711950722` SUCCESS。交付 `glazing_condensation.py`、`review.py` adapter、deterministic regression及 1D 中央玻璃 scope；非整窗、邊框、間隔條及 ISO 完整合規評估。

## 使用規則

- Future feature、non-blocking debt、等待 trigger 的工作放在 `BACKLOG.md`，不得因存在就自動執行。
- 新工作只有在 current evidence、使用者選擇與 repository authority 已使其成為可執行／critical path 後，才加入本檔。
- Hot work完成並取得必要 validation／remote evidence後，從本檔移除；completed history由 Git history與 canonical artifacts保存。
