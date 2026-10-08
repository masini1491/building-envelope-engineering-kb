# 目前任務（TASKS）

本檔是 building-envelope-engineering-kb 的 Hot coordination surface，只保存目前可執行或 current critical-path 的工作。

## 目前執行中的工作

### 高樓層屋頂局部風壓（KB-CAND-008）— ACTIVE

- Authority：使用者於 2026-10-08 明確選定此 Cold candidate；按圖 3.2 原始官方圖表與 Wind V2 接續，不延伸其他 wind features。
- 先核對 >18 m 屋頂圖 3.2 Zone 1/2/3 的負風壓、坡度 >10° 轉圖 3.1(c)/(d)、女兒牆條件與圖表 machine transcription；無原始正風壓曲線時不得偽造 roof positive GCp。
- Implementation：限定的 deterministic coefficients + route、separate suction-only boundary where relevant、風壓 test regression、adapter status 正確表示 unsupported/partial；受權驗證與 remote read-back後 closure。

### 玻璃表面溫度與結露初篩（KB-CAND-006）— QUEUED

- Authority：同次使用者選定，依序待 KB-CAND-008 current stage完成再進 Hot implementation。
- 只對已確認 U-value／surface resistance／環境温濕度或有 provenance 的局部表面溫度作 bounded surface condensation screening；不得以單一 U-value 推估 spacer／frame minimum temperature，也不宣稱完整 ISO 13788/10211 compliance。
- Implementation：獨立 deterministic thermal/dew-point/fRsi kernel、provenance／applicability 及 invalid-input fail-closed、focused test、CI、read-back；不引入材料 catalog。

## 使用規則

- Future feature、non-blocking debt、等待 trigger 的工作放在 `BACKLOG.md`，不得因存在就自動執行。
- 新工作只有在 current evidence、使用者選擇與 repository authority 已使其成為可執行／critical path 後，才加入本檔。
- Hot work完成並取得必要 validation／remote evidence後，從本檔移除；completed history由 Git history與 canonical artifacts保存。
