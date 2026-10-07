# 目前任務（TASKS）

本檔是 building-envelope-engineering-kb 的 Hot coordination surface，只保存目前可執行或 current critical-path 的工作。

## 目前執行中的工作

### P1 耐風 V2 正確性修正（KB-P1-A-FIX）

- **來源**：2026-10-07 對已完成 P1-A 的 official-source read-back audit。
- **目標**：修正已 admission 的低樓層 Figure 3.1 implementation，不擴張到新的高樓屋頂 capability。
- **已確認 defect**：
  - Figure 3.1(c) `7° < θ <= 27°` 正外風壓係數控制點方向反轉；應為小面積較大、面積增大後下降。
  - Figure 3.1(b) 女兒牆條件雖已存於 reference JSON，但 kernel 未提供可啟用的 explicit routing。
  - canonical wind 文件仍殘留 V1 wording drift。
- **修正 contract**：
  - Figure 3.1(c) positive control values修正為 ASCE basis `0.5 -> 0.3`（Taiwan `×2.083`），並以 official Figure 3.1(c)曲線方向與端點作 regression。
  - 女兒牆 Zone 3→Zone 2 只在使用者明確 opt-in、`θ <= 7°`、四周女兒牆成立且 `parapet_height_m >= 0.9` 時啟用；不得自動推定。
  - `h > 18 m` 屋頂 Figure 3.2 routing不在本修正 Stage 擴張；另存 Cold candidate。
  - 同步收斂 V1/V2 文件 wording。
- **Validation**：保留既有 V1/V2 regression，新增 Figure 3.1(c) positive endpoint/semilog regression、parapet eligibility/fail-closed regression、adapter regression；跑 current `PRE_PUSH_VALIDATION.md` 與 remote CI。
- **完成條件**：candidate CI、merge後 main CI、canonical read-back均成立後移除本 Hot item，再進 P2。

## 使用規則

- Future feature、non-blocking debt、等待 trigger 的工作放在 `BACKLOG.md`，不得因存在就自動執行。
- 新工作只有在 current evidence、使用者選擇與 repository authority 已使其成為可執行／critical path 後，才加入本檔。
- Hot work完成並取得必要 validation／remote evidence後，從本檔移除；completed history由 Git history與 canonical artifacts保存。
