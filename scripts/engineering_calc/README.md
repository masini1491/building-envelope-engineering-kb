# 工程計算與計算書核算工具

本目錄提供 ChatGPT、工程師與其他 AI 可執行的 deterministic calculation helpers。定位是**工程計算執行層與獨立數值核算層**，不是設計規範、材料資料庫或自動核准系統。

## 兩種使用模式

### 計算模式（Calculation Mode）

由已確認的工程輸入執行可重現的數學計算。工程假設、荷載、材料性質、allowable、support condition 與適用標準仍由對應 `knowledge/` canonical page、專案可靠來源或使用者明確輸入控制。

### 核算模式（Review Mode）

ChatGPT 從計算書抽取 reported inputs、公式、假設與 reported results，再使用本工具獨立重算並比較。工具可指出數值差異、缺少輸入與需要人工複核的項目，但不得把局部 arithmetic match 解讀成整份計算書安全或完整合格。

建議流程：

`計算書 → ChatGPT 抽取與辨識模型 → deterministic helper 重算 → reported/recomputed comparison → ChatGPT 依 canonical methodology 判讀差異與完整性`

## 工具邊界

- calculator 確認 arithmetic correctness，不等於確認 engineering correctness。
- 公式算對不代表公式選對；公式選對不代表模型、荷載、材料、規範或 failure-mode coverage 正確。
- 不自行生成 allowable stress、design strength、safety factor、design pressure、standard edition 或規範等價關係。
- 單位轉換必須明確；無法確認單位時應停止或標示缺口，不可猜測。
- comparison tolerance 只代表數值一致性門檻，不是工程允許誤差。
- local calculation result 不得直接升格成 overall structural PASS。

## 第一階段模組

- `units.py`：少量明確、可追溯的工程單位轉換。
- `compare.py`：reported 與 recomputed 數值比較。
- `section_required.py`：required section property 的 deterministic arithmetic。
- `beam.py`：目前只提供明確邊界條件的 closed-form beam sanity check。
- `fastener_group.py`：平面扣件群在 direct in-plane force 與 `Mz` 下的彈性分配核算。

對應 deterministic tests 位於 `tests/engineering_calc/`。

## 漸進式擴充原則

只有在公式、輸入、輸出、適用條件與失敗語意可明確界定時才新增 helper。複雜連續梁、焊道群、tributary-load distribution 與高階 audit orchestration 應在各自 canonical methodology 與驗證案例足夠後再加入，不以一支大型萬用 calculator 混合所有工程責任。