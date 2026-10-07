# 目前任務（TASKS）

本檔是 building-envelope-engineering-kb 的 Hot coordination surface，只保存目前可執行或 current critical-path 的工作。

## 目前執行中的工作

### 耐風設計風壓 V2：低樓層與屋頂區域（KB-P1-A）

- **來源**：由 BACKLOG 的 `KB-CAND-001` 經使用者明確選定 P1、current evidence reconciliation 與設計占卜修正後 promote。
- **目標**：在既有 `wind_pressure` capability 上擴充 103 年修正版耐風規範的 `h <= 18 m` 局部構材／外部被覆物計算，涵蓋低樓層外牆 Zone 4／5 與屋頂 Zone 1／2／3。
- **Current authority**：現行官方《建築物耐風設計規範及解說》圖 3.1 為係數／適用範圍 authority；政府公開示範例只作圖表公式化與 regression cross-check；WebCalc／其他第三方 calculator 只作 reference-only comparison。
- **Implementation boundary**：
  - 延用同一 `check_type = "wind_pressure"`，不另造平行 calculator。
  - 支援封閉式／部分封閉式與 `governing_wind_source = code`；開放式、風洞 governing、圖 3.1 以外幾何仍 fail closed。
  - 低樓層外牆採圖 3.1(a)，並將「低坡度牆面 GCp 可減 10%」做成 explicit option，不得自動套用。
  - 屋頂依坡度 routing 到圖 3.1(b)／(c)／(d)；係數若無法由 current official figure／admitted public evidence建立可重現 machine transcription，該分支保持 `UNSUPPORTED_MODEL`，不得猜值。
  - 低樓層角隅寬度依圖 3.1 note：`a = max(min(0.4h, 0.1B), 0.9m, 0.04B)`。
  - 保留 raw computational value → display rounding 的可重現 contract。
- **Validation**：
  - 保持既有 Wind V1 regression 全部通過。
  - 新增 Figure 3.1 endpoint／semilog interpolation、坡度 boundary、`h = 18 m`、角隅寬度、optional 10% reduction、unsupported routing 與 adapter regression。
  - 執行 `PRE_PUSH_VALIDATION.md` 的 current required checks與 remote CI。
- **STOP boundary**：不得為了完成 coverage 把第三方 calculator、未確認 ASCE 係數、模型反推值或受版權限制來源中的未 admission data 當 canonical truth。
- **完成後下一步**：remote completion evidence成立後，本 Hot item移除；再 fresh-reconcile `KB-P1-B` 玻璃耐風承載力 capability。

## 使用規則

- Future feature、non-blocking debt、等待 trigger 的工作放在 `BACKLOG.md`，不得因存在就自動執行。
- 新工作只有在 current evidence、使用者選擇與 repository authority 已使其成為可執行／critical path 後，才加入本檔。
- Hot work完成並取得必要 validation／remote evidence後，從本檔移除；completed history由 Git history與 canonical artifacts保存。
