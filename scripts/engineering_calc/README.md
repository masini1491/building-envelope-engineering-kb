# 工程計算與計算書核算工具

本目錄提供 ChatGPT、工程師與其他 AI 可執行的 deterministic calculation helpers。定位是**工程計算執行層與獨立數值核算層**，不是設計規範、材料資料庫或自動核准系統。

## 兩種使用模式

### 計算模式（Calculation Mode）

由已確認的工程輸入執行可重現的數學計算。工程假設、荷載、材料性質、allowable、support condition 與適用標準仍由對應 `knowledge/` canonical page、專案可靠來源或使用者明確輸入控制。

### 核算模式（Review Mode）

ChatGPT 從計算書抽取 reported inputs、公式、假設與 reported results，再使用本工具獨立重算並比較。工具可指出數值差異、缺少輸入與需要人工複核的項目，但不得把局部 arithmetic match 解讀成整份計算書安全或完整合格。

建議流程：

`計算書 → ChatGPT 抽取與辨識模型 → AI-facing adapter → deterministic helper 重算 → calculation-chain reconciliation → reported/recomputed comparison → ChatGPT 依 canonical methodology 判讀差異與完整性`

## 人工智慧（AI）導入入口

當 ChatGPT 已依 `CHAT_INIT.md` 與對應 canonical methodology 確認需要 deterministic numerical verification 時，優先使用：

```bash
python -m scripts.engineering_calc.review input.json
```

也可由 stdin 傳入 JSON。adapter 把 AI 抽取的結構化輸入送入既有 deterministic helper，再回傳 machine-readable 結果；它**不負責選擇工程模型或產生工程設計值**。

**Adapter-first 是預設 execution contract。**只要 `review.py` 已支援所需 `check_type`，ChatGPT 不應直接 import `audit.py`、`compare.py`、`beam.py`、`connection.py` 或其他底層 helper 來自行重建 invocation／status contract。只有 adapter 尚未支援所需能力時，才可 bounded-read 最低必要底層 module 作 fallback，並在回答中明確標示 `ADAPTER_FALLBACK` 與 fallback scope；不得把 fallback 描述成標準 adapter execution。

執行前必須確認 Python runtime、repository/package filesystem 與必要 dependency 真正可用。只具備 GitHub read access、能看到 source code，**不等於**程式已在目前 execution environment 成功執行。

### 輸入契約

最外層固定使用 `check_type / units / inputs / reported_results / tolerance`。`units` 必填且不得猜測；`reported_results` 可省略；`tolerance` 只代表 numerical agreement，不是 engineering acceptance criterion。

目前 adapter 支援：`glazing_condensation`、`beam`、`required_inertia`、`required_section_modulus`、`section_property_utilization`、`fastener_group`、`demand_capacity`、`projected_bearing_stress`、`shear_tension_demand`、`thread_engagement`、`audit_product`、`audit_force_balance`、`wind_pressure`。`thermal_bridge_2d.py` 在目前 Stage **尚未接入 `review.py`**；若需要直接使用，屬明確的 lower-level `ADAPTER_FALLBACK`，不得描述成已支援的 AI-facing `check_type`。

### 輸出契約

最外層固定回傳 `calculation_status / comparison_status / check_type / computed / comparisons / review_flags`。

- `calculation_status`：`COMPUTED / INCOMPLETE_INPUT / UNSUPPORTED_MODEL`。
- `comparison_status`：`MATCH / MISMATCH / NOT_PROVIDED / INCOMPLETE`。

這些 status 只描述**計算執行／數值比對**；不得改寫成整體工程 `PASS`。例如 visible factors 重算得到 `MISMATCH` 時，先記錄為 calculation-chain discrepancy，再查單位、遺漏係數、不同 load source、hidden multiplier 或 transcription error；在 root cause 未確認前，不得僅因 arithmetic mismatch 宣稱整體工程 `FAIL`。

### 風壓（`wind_pressure`）輸入契約

此 check_type 的自然語言 intake 不由 adapter 負責；ChatGPT 應先依 wind knowledge owner 整理／追問 project facts，再送入完整結構化 payload。最低輸入為：

- `region`，以及該縣市需要細分時的 `district`
- `building_category`（1–5）
- `terrain_category`（A／B／C）
- `kzt`
- `enclosure`（`enclosed`／`partially_enclosed`；`open` 目前 fail closed）
- `h_m / effective_area_m2 / least_horizontal_dimension_m`
- `surface`（省略時為 `wall`；屋頂使用 `roof`）
- `h > 18 m` 外牆另需 `z_m`
- 低樓層屋頂另需 `roof_slope_deg`；目前支援 `0°`～`45°`
- 低樓層屋頂若要採圖 3.1(b) 註 1 的女兒牆 Zone 3→Zone 2 處理，需明確設定 `apply_parapet_zone3_as_zone2 = true`、`parapet_all_sides = true`，並提供 `parapet_height_m >= 0.9`；僅適用 `roof_slope_deg <= 7`
- 低樓層外牆若要採圖 3.1(a) 註 1 的 10% 折減，需明確設定 `apply_low_slope_wall_reduction = true` 並提供 `roof_slope_deg <= 10`
- `governing_wind_source = "code"`

`units` 仍為最外層必填。reference data 位於 `references/government/taiwan-wind-code-103-v2.json`；kernel 自動解析 `V10(C) / I / α / zg / GCpi`，並計算 `K(z) / K(h) / q(z) / q(h) / a / GCp`。部分封閉式建築物之正內風壓速度壓，目前明確採 2.2 節允許的 `q(h)`，不在缺少開口高度時猜測 `zh0`。

可比較的 reported key 包括：

- 外牆：`zone4.positive_kpa / zone4.negative_kpa`、`zone5.positive_kpa / zone5.negative_kpa`
- 低樓層屋頂：`zone1.* / zone2.* / zone3.*`
- 共通：`qh_kpa / corner_a_m`；`h > 18 m` 外牆另有 `qz_kpa`

超出 admitted applicability（例如開放式、風洞 governing、`h > 18 m` 屋頂或 `roof_slope_deg > 45`）時回 `UNSUPPORTED_MODEL`；必要 project facts／行政區資料不足時回 `INCOMPLETE_INPUT`。這些 execution status 不代表整體耐風設計 PASS／FAIL。

### 回答中的執行證據

若回答聲稱「已使用 Repository deterministic calculator 核算」，至少應能讓讀者辨識：

- 使用的 adapter `check_type`；
- `calculation_status` 與 `comparison_status`；
- reported 與 recomputed 的關鍵值；
- relevant `review_flags`；
- 若未走 adapter，明確標示 `ADAPTER_FALLBACK` 與原因。

不要求把完整 JSON 原樣貼給使用者，但不得只寫「已用 helper 重算」而無法區分真正 execution、手算、模型心算或 source-code inspection。

### 玻璃中央部位結露初篩（`glazing_condensation`）

AI-facing `review.py` 支援這個獨立 deterministic screening check_type。必填 `inputs`：
`indoor_temperature_c`、`outdoor_temperature_c`、
`indoor_relative_humidity_pct`（0–100%，且必須 >0）、
`glazing_u_value_w_m2k` 及 `interior_surface_resistance_m2k_w`，
均由工程師或可追溯產品／專案證據提供；`units` 仍須顯式提供。

限定採 1D 穩態 `T_si=T_i-U×R_si×(T_i-T_o)` 與 Magnus 近似露點（17.62／243.12）比較；
`temperature_factor_frsi` 在室內外溫度相等時為 `null`。
`NO_CONDENSATION_IN_THIS_1D_MODEL` 只表示此模型下的局部表面比較，
**不得**解讀為整窗／間隔條／窗框無結露，亦不評估黴菌、生長條件、時間累積與 ISO 13788／ISO 10211 project compliance。

## 工具邊界

- calculator 確認 arithmetic correctness，不等於確認 engineering correctness。
- 公式算對不代表公式選對；公式選對不代表模型、荷載、材料、規範或 failure-mode coverage 正確。
- 不自行生成 allowable stress、design strength、safety factor、design pressure、standard edition 或規範等價關係。
- 單位轉換必須明確；無法確認單位時應停止或標示缺口，不可猜測。
- comparison tolerance 只代表數值一致性門檻，不是工程允許誤差。
- `connection.py` 的 capacity 必須由可追溯的規範、產品資料或專案條件明確提供；工具不內建 universal fastener capacity。
- `beam.py` 不推論支承、splice rigidity 或 semi-rigid behavior；boundary condition 不明時，ChatGPT 應把 structural model 視為 `INCOMPLETE`。
- local calculation result 不得直接升格成 overall structural PASS。
- `thermal_bridge_2d.py` 的材料導熱係數、mesh 與 boundary condition 都必須由 caller／project provenance 提供；kernel 不內建材料表、不猜 indoor/outdoor surface resistance。它會 fail closed 檢查 index／退化元素／edge-connectivity／manifold edge、duplicate／orphan vertices 與 boundary references，但不自行證明任意 caller mesh 的完整 computational-geometry conformity（例如重疊元素或 T-junction）；這仍是 mesh-generator／caller contract。其 `NUMERICAL_BACKEND_ONLY` 輸出與 Case 1／Case 2 regression PASS 都不得升格成完整 ISO 10211 compliance。

## 目前模組

- `units.py`：少量明確、可追溯的工程單位轉換。
- `compare.py`：reported 與 recomputed 數值比較。
- `section_required.py`：required section property 的 deterministic arithmetic。
- `beam.py`：線彈性 1D Euler-Bernoulli beam direct-stiffness solver。
- `beam_extrema.py`：由 beam result 重建 constant-UDL element 的跨內 shear / moment / deflection，輸出 element/global 最大絕對值與位置。
- `fastener_group.py`：平面扣件群彈性分配核算。
- `connection.py`：需求／容量比、bearing、shear/tension 與 thread-engagement arithmetic helper。
- `audit.py`：乘積鏈與靜力 force balance reconciliation。
- `wind_pressure.py`：103 年修正版《建築物耐風設計規範及解說》風壓 deterministic kernel；支援 `h > 18 m` 外牆圖 3.2 Zone 4／5，以及 `h <= 18 m` 外牆圖 3.1(a) 與屋頂圖 3.1(b)～(d) Zone 1／2／3。
- `thermal_bridge_2d.py`：二維 steady-state 熱傳 numerical kernel；接受 caller 已離散的 triangular mesh、逐 element 導熱係數、顯式 fixed-temperature nodes 與 surface-resistance exterior edges。它只回傳 node temperature 與指定 surface-resistance boundary heat flow，不建立 Ψ-value／fRsi／結露或 ISO 10211 project compliance 判定。
- `review.py`：AI-facing JSON adapter，統一 invocation、execution status、reported comparison 與 review flags。

一般 deterministic tests 位於 `tests/engineering_calc/`。熱橋 numerical regression 位於 `tests/thermal_bridge/`，只由獨立 CI job 安裝 `requirements/thermal-bridge.txt` 後執行；因此 optional thermal backend 不會擴大既有 repository validation job 的 dependency failure domain。

## 多跨梁核算使用原則

使用前，ChatGPT 必須先依計算書與 canonical methodology 明確辨識 node / support / splice、restrained DOF、每段 `E / I`、每段 UDL 與 point load / moment 位置。任意 point load 應在作用位置建立 node 後再輸入。

現階段 solver 不包含 semi-rigid rotational spring、Timoshenko shear deformation、geometric/material nonlinearity、torsion 或 3D frame behavior；需要這些效應時不得用本工具結果取代適當分析模型。

`beam_extrema.py` 只適用目前 solver 的 adjacent-node、constant-UDL element；simple-span 的跨中 `Mmax / δmax` 因此不會只靠 element end action 判斷。

## 計算書核算建議

優先把數值鏈拆成：

`design pressure → multiplier / tributary width → line load → beam response → support reaction → fastener-group demand → connection demand/capacity arithmetic`

若 adapter 回傳 `MISMATCH`，回到該步驟檢查單位、係數、effective width、boundary condition、load combination 或 hidden multiplier，不直接用後段結果覆蓋差異，也不直接把 comparison status 升格為 engineering acceptance status。施工圖、材料表與計算書的一致性仍屬 document cross-check，不能因 deterministic arithmetic `MATCH` 而省略。

## 漸進式擴充原則

只有在公式、輸入、輸出、適用條件與失敗語意可明確界定時才新增 helper。下一階段可再依 canonical methodology 與實際計算書需求加入 weld group、transom dead-load / setting-block、biaxial member check、panel/stiffener 與 structural silicone；玻璃與標準高度耦合的計算應在 edition/provenance 與驗證案例足夠後再實作。
