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

超出 admitted applicability（例如開放式、風洞 governing、未支援的高層屋頂正壓或 `roof_slope_deg > 45`）時回 `UNSUPPORTED_MODEL`；必要 project facts／行政區資料不足時回 `INCOMPLETE_INPUT`。這些 execution status 不代表整體耐風設計 PASS／FAIL。

### 回答中的執行證據

若回答聲稱「已使用 Repository deterministic calculator 核算」，至少應能讓讀者辨識：

- 使用的 adapter `check_type`；
- `calculation_status` 與 `comparison_status`；
- reported 與 recomputed 的關鍵值；
- relevant `review_flags`；
- 若未走 adapter，明確標示 `ADAPTER_FALLBACK` 與原因。

不要求把完整 JSON 原樣貼給使用者，但不得只寫「已用 helper 重算」而無法區分真正 execution、手算、模型心算或 source-code inspection。

### 部分封閉式內風壓速度壓選擇

規範表 2.1 註 1 的高層局部構材路由：當 `enclosure="partially_enclosed"` 時，**正值內風壓**按影響正內風壓的最高開口高度 `zh₀`，使用 `q(zh₀)`；**負值內風壓**使用 `q(h)`。選用 `positive_internal_pressure_basis="q(zh0)"` 時必須提供由工程師確認的 `opening_top_height_m`（大於 0 且不高於 `h_m`），不由程式猜測開口。

相容舊輸入的 `"q(h)"` 預設僅作 **`CONSERVATIVE_QH_FALLBACK`**：對高層部分封閉式正值內風壓，以 `q(h)` 作保守吸力值，不得標為按確定開口高度計算的規範精確值；在不允許保守假設的專案應提供 `zh₀`。封閉式建築物與低層既有路由仍使用 `q(h)`。輸出 `velocity_pressure.qi_positive` 和 `qi_negative` 分別標示兩個符號的來源，負風壓不得誤用 `q(zh₀)` 以外推其他載重情境。

### 高層屋頂局部吸力（KB-CAND-008 bounded admission）

`wind_pressure` 的 `surface="roof"` 已新增受限 `h > 18 m` 路由：

- `roof_slope_deg <= 10`：採內政部建築研究所示範例公式化的 Zone 1／2 負風壓；Zone 3 的無女兒牆曲線由國土署圖 3.2 **近似圖面轉錄**（面積平台 1／50 m²：−6.67／−4.79，半對數內插），不是官方公布的精確係數表。若明確提供 `apply_parapet_zone3_as_zone2=true`、`parapet_all_sides=true`、`parapet_height_m > 0.9`，則依圖 3.2 註 2 將 Zone 3 作 Zone 2；未啟用則使用 Zone 3 直接吸力。
- `10 < roof_slope_deg <= 45`：依圖 3.2 註 5 轉用圖 3.1(c)／(d)；不啟用圖 3.2 女兒牆折減。
- 上述第一條為 `SUPPORTED_SUCTION_ONLY`：`pressures` 只有 `negative_kpa`、`negative_kgf_m2`；本 Stage 沒有屋頂正風壓曲線，不得從外牆的正壓係數推算。若核算輸入要求 `zoneN.positive_kpa`，adapter 將標成 `UNSUPPORTED_REPORTED_KEY`。
- Zone 1／2 來源為政府研究示範例的公式化結果，Zone 3 為國土署原圖的近似端點轉錄。**不得**將本次轉錄描述為出版者數值表或包含完整屋頂正風壓的全面合規判定。

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

### 非線性 FEA 外部執行 probe（KB-CAND-007）

`calculix_probe.py` 為本 Stage opt-in 外部 CalculiX process wrapper；不是 `review.py` check_type，也不自行產生求解器模型或解析求解結果。只有 caller 已審查本機輸入 deck、所有 include、工作目錄與 solver executable 時才可設 `execute=True`。預設不執行，且即使 process exit code 為 0 亦回報 `PROCESS_EXIT_ZERO_UNVERIFIED`，**不等於 NLGEOM 收斂／工程設計驗證**。沒有 sandbox；不得執行不可信輸入。

選型與完整的受限驗證 evidence 見 [非線性 FEA 求解器研究](../../references/github-projects/nonlinear-fea-solver-admission.md)。本 repo 不打包 GPL-2.0 solver。

Stage 33 另提供**合成 benchmark 專用**的受限執行入口 `tests/fea_benchmark/envelope_panels/run_synthetic_panel.py`。於 repo 根目錄、確認本機 `ccx` 是可信已安裝版本後，可先建空白工作目錄，再明確 opt-in 執行：

```bash
mkdir -p /tmp/kb-ccx-synthetic-glass4
python tests/fea_benchmark/envelope_panels/run_synthetic_panel.py --material glass --mesh 4 --workspace /tmp/kb-ccx-synthetic-glass4 --ccx /usr/bin/ccx --execute
```

該入口只接受 `glass`／`aluminum` 與 4／8／16 網格，固定為 Repo 產生的 synthetic S8R NLGEOM P1 高荷載模型，**不接受外部 input deck**；預設不帶 `--execute` 就不執行。成功時要求 CCX process、最後增量、DAT／FRD、三向平移平衡及幾何力矩分解均可驗證；另於執行前後確認 deck／solver SHA-256 未改變，並在成功回覆附上主要 artifact 的 SHA-256 追溯資訊，回傳 `SYNTHETIC_BENCHMARK_EVIDENCE_PASS`，同時維持 `engineering_acceptance=NOT_ADMITTED` 和 `six_component_global_balance=NOT_ADMITTED`。無 sandbox，不能執行不可信外部 solver。這不是 `review.py` check_type、正式玻璃／鋁板強度設計功能或一般 nonlinear FEA adapter。


### 鋁板參數研究介面（Stage 37–38）

已支援另一個**僅限研究模型**之入口 `tests/fea_benchmark/envelope_panels/run_aluminum_research.py`：明確提供 JSON 檔案、空白的既有工作目錄和可信本機 CCX，且加上 `--execute` 才會運行。輸入需包含 `width_mm / height_mm / thickness_mm / youngs_modulus_mpa / poisson_ratio / pressure_n_mm2 / mesh / support / units / material_provenance`。目前僅接受 `support="four_edges_clamped"`、`units="N-mm-MPa"`、`mesh=4/8/16` 及程式所定研究限制，所有材料與面壓值由呼叫者提供。

範例（僅為合成研究，不能當成實際建材參數）：

```json
{"width_mm":120.0,"height_mm":80.0,"thickness_mm":2.5,"youngs_modulus_mpa":70000.0,"poisson_ratio":0.32,"pressure_n_mm2":0.3,"mesh":8,"support":"four_edges_clamped","units":"N-mm-MPa","material_provenance":"explicit synthetic values for research"}
```

```bash
mkdir -p /tmp/kb-aluminum-research
python tests/fea_benchmark/envelope_panels/run_aluminum_research.py --input aluminum.json --workspace /tmp/kb-aluminum-research --ccx /usr/bin/ccx --execute
```

成功時 `execution_status=ALUMINUM_PARAMETRIC_RESEARCH_EVIDENCE_PASS` 僅指這個受限模型的 numeric checks 成立，非 admissible ADM capacity，也不是任意板件／支承／材料／屈曲、接觸或全六分量平衡驗收。Stage 38 的不同參數實測與細節可查 canonical dossier。

Stage 40–44 已另以實際 CalculiX CI 對低荷載合成鋁板完成受限驗證：4／8／16 網格與一項 Kirchhoff／Rayleigh–Ritz 位移近似、最終原始 S8R 節點 U／平移支承合力重建摘要、expanded C3D20 節點外插／平均 S／E 六分量，以及同模型兩倍均布面壓的逐節點 U／S／E 比例檢查和法向 Hooke 定律應力／應變交叉比對。成功結果在 `research_observations` 中提供 node ID、單位與未認證標記；此處**最大值只在現有輸出節點內比較**，不代表積分點／整板場極值，不提供獨立轉動反力、剪切本構驗證、ADM 容量或真實構件 engineering PASS。真實 CCX 仍須可信外部程式與 `--execute`。完整來源、數值研究門檻與限制只以 canonical dossier 為準。


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


### 三種中鋁質別的明確輸入前處理（研究專用）

`tests/fea_benchmark/envelope_panels/prepare_aluminum_material_input.py` 可接受 `3003-H14`、`3004-H12`、`3004-O` 的**使用者宣告選擇**，產生與原 `aluminum_research_input.py` 完全相同的十欄 JSON。原求解入口與 `--execute` 門檻不變。輸入仍**必填** `youngs_modulus_mpa`、`poisson_ratio`、尺寸、厚度、面壓、網格與支承，禁止由牌號自動推導任何數值。`manufacturer` 需為 `CS Aluminum`，`property_evidence_status` 需為 `USER_DECLARED_UNVERIFIED`；這只是未驗證來源聲明，不表示產品保證值或材料卡獲認證。工具不讀取客戶版 PDF、不帶入降伏強度、抗拉強度或塑性曲線，也不會執行求解。

範例（全部數值僅是使用者自訂**合成**研究資料，非中鋁產品保證性質）：

```json
{"alloy_temper":"3004-H12","manufacturer":"CS Aluminum","property_evidence_status":"USER_DECLARED_UNVERIFIED","width_mm":120.0,"height_mm":80.0,"thickness_mm":2.5,"youngs_modulus_mpa":70000.0,"poisson_ratio":0.32,"pressure_n_mm2":0.0002,"mesh":8,"support":"four_edges_clamped","units":"N-mm-MPa"}
```

從 `tests/fea_benchmark/envelope_panels` 執行：

```bash
python prepare_aluminum_material_input.py --selection selection.json --output research_input.json
```

產出的 `research_input.json` 才能依前述受限 opt-in 方式交給 `run_aluminum_research.py`。原始 JSON 的 source label 會明示 `USER_DECLARED_UNVERIFIED`。不要把來源標籤當作已驗證材料性質，或把 `ALUMINUM_PARAMETRIC_RESEARCH_EVIDENCE_PASS` 當成正式工程 strength/capacity PASS。

可選用 `--evidence evidence.json` 啟用**使用者宣告 metadata 的一致性檢查**。此時 selection JSON 必須額外包含 `product_id`，evidence JSON 必須精確包含 `manufacturer / alloy_temper / product_id / product_form / material_condition / source_visibility / evidence_claim / thickness_range_mm / elastic_properties`；目前只接受 `product_form="sheet"`、`material_condition="AS_SUPPLIED"`、`evidence_claim="USER_DECLARED_NOT_VERIFIED"`，以及 `source_visibility="PUBLIC"` 或 `"PRIVATE"`。數值 `thickness_range_mm` 的單位是 mm；`elastic_properties` 需提供 `youngs_modulus_mpa` 與 `poisson_ratio`，與 selection 的明確輸入完全相同。省略 `--evidence` 時保留 PR #76 的舊模式；若另有產品識別但未提供 evidence 會拒絕，不會靜默忽略。驗證成功的輸出仍**只有既有十欄 research JSON**，不包含 `product_id`、私人來源內容或廠商強度。
 
重要：`DECLARED_METADATA_CONSISTENCY_ONLY` **僅證明兩個使用者提供的 JSON 在程式支援的欄位上相符**，不代表官方資料真偽、材料保證值、真實產品合格、允許輸入未核對的應力–應變曲線或 ADM capacity。客戶版及非公開原始證據保留在 Repo 外，禁止上傳；實驗／熱加工後等狀態不在本前處理器的 `AS_SUPPLIED` 支援範圍。

### 製造商聲明的使用者採信（受限研究）

中鋁正式提供的產品技術資料可以作為工程估算與材料參數的**製造商聲明依據**，不必把「未做第三方逐項複驗」視為一律無法引用。不過必須由使用者明確選擇 `property_evidence_status="MANUFACTURER_DECLARATION_ACCEPTED_BY_USER"`，並在獨立的 `--evidence` metadata 內填入同名的 `evidence_claim`，經產品識別、牌號質別、供貨狀態、厚度範圍及 E／ν 一致性檢查，才能取得 `USER_ACCEPTED_MANUFACTURER_METADATA_CONSISTENCY_ONLY`。未明確選擇時維持 `USER_DECLARED_UNVERIFIED`；不同狀態互相衝突時拒絕，不自動升級。

此狀態的語意是**使用者接受製造商文件作為來源、且兩份宣告資料一致**，不是文件真偽的獨立鑑定、批次 MTC 試驗或任何強度／容量保證。材料性能仍須符合特定供貨產品、牌號／temper、厚度、加工與熱處理狀態以及適用設計規範。客戶版 PDF 及其非公開數值不進入公開 Repository。轉出的原始十欄 FEA 研究 input contract 不變、所有 E／ν／幾何及面壓仍須明確提供，`MATERIAL_PLASTICITY_NOT_ADMITTED` 與 `MATERIAL_CAPACITY_NOT_ADMITTED` 不變。

### 三種質別之合成材料標籤隔離回歸（Stage 48）

真實 CalculiX CI 會用 **完全相同且明確輸入的合成 E、ν、板厚、尺寸、面壓**，分別宣告 `3003-H14`、`3004-H12`、`3004-O`，生成三份獨立研究輸入並求解。必須確認原始 deck SHA-256 相同、solver SHA-256 相同、各筆 `material_provenance` 含正確牌號，及研究觀測 payload 完全一致；任何差異都拒絕，且單元測試涵蓋錯誤來源、輸入漂移、結果篡改與材料容量狀態升級。此測試只證明**牌號標籤沒有偷偷改變數值模型**；**不能據此宣稱三種真實鋁板材料等效**。此回歸仍為 linear-elastic research-only，`MATERIAL_PLASTICITY_NOT_ADMITTED`、`MATERIAL_CAPACITY_NOT_ADMITTED` 不變。

### 私人製造商硬化曲線：結構完整性預檢（Stage 52）

`tests/fea_benchmark/envelope_panels/validate_private_hardening.py` 是**只讀的本地 JSON 預檢器**，支援使用者保存在 Repo 外的中鋁 `3003-H14`／`3004-H12`／`3004-O` 材料試驗資料。輸入必須明確包含 `alloy_temper`、無專案身分的 `product_id`、`manufacturer="CS Aluminum"`、`state="AS_SUPPLIED"`、`data_origin="PRIVATE_USER_SUPPLIED_MANUFACTURER_DECLARATION"`、`units="N-mm-MPa"`、`curve_type="TRUE_VON_MISES_STRESS_EQUIVALENT_PLASTIC_STRAIN"`、`elastic_modulus_mpa`、`poisson_ratio`，及至少三個 `points=[[true_stress_mpa, equivalent_plastic_strain], …]`。

預檢器只核對資料形狀、數值有限且正值、首列塑性應變為零、後續塑性應變嚴格遞增、應力非遞減、指定硬上限與 exact keys；**不**以降伏／抗拉／伸長率插值或合成完整應力–應變曲線，**不**驗證製造商文件真偽、拉伸方向／頸縮前有效區間、材料批次或工程設計適用性。接受此 JSON 不表示 CalculiX 材料卡或正式工程 capacity 已 admission，狀態一律 `NOT_ADMITTED`。

執行：`python validate_private_hardening.py /私有路徑/硬化試驗資料.json`。結果只列驗證狀態及點數，不輸出原始資料、產品代號或應力／應變值。不產生任何 `*PLASTIC` deck、無檔案寫入／上傳步驟。**客戶版 PDF、試驗資料 JSON 與實際產品資訊不得提交至公開 Repo**；CI 只執行明確合成且不對應中鋁實際試驗值的 unit fixtures。

### 四邊固定鋁板之獨立低荷載彎曲場近似（研究）

`tests/fea_benchmark/envelope_panels/check_aluminum_ritz_stress.py` 對既有 Stage 43 的低荷載合成鋁板，以三項對稱、滿足四邊固定幾何條件的 Kirchhoff–Rayleigh–Ritz 多項式、解析多項式積分和獨立 3×3 線性方程，建立**中心撓度與中心薄板上下表面彎曲應力**近似。它再比對真實 CalculiX 2.21 原始 S8R 中心 U 及 expanded C3D20 節點 FRD 外插／平均的中心上下表面 SXX／SYY，並檢查非彎曲（membrane）殘量、完整表面節點覆蓋與有限值。只使用公開 synthetic E／ν／厚度／面壓，無真實中鋁材料卡。**Ritz 多項式截斷與 CCX expanded-node 外插／平均都有各自誤差**；研究差異篩選門檻（撓度 12%、彎曲應力 30%、非彎曲殘量 18%）不是獨立精確真值、通用求解器誤差上限或容許應力。此觀測不能外推為積分點尖峰、折板／加勁肋／扣件、挫屈、塑性或 ADM 工程設計驗收，維持 `EVIDENCE GATED`／`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。CI 必須在相同 PR exact-head 實際執行合成 CCX case 後才能稱受限研究篩選通過。


### 鋁板中心彎曲應力跨長寬比與網格受限研究（Stage 55）

現有 Stage 40 的兩組 synthetic 四邊固定板（100×100×3 mm 與 120×80×2.5 mm），各有 4／8／16 網格且由真實 CalculiX 2.21 執行。新增 `tests/fea_benchmark/envelope_panels/check_aluminum_ritz_mesh_stress.py` **重用相同六組實際求解產物**，逐組檢查 config、report status、deck／DAT／FRD SHA-256 provenance、expanded C3D20 FRD 節點覆蓋；**只在 16 網格使用 Stage 54 的中心撓度／彎曲 SXX、SYY 近似門檻**，4／8 網格僅擷取實際中心表面應力觀測，不宣稱通過細網格門檻；同時計算每種形狀、每個方向從 4→8→16 的中心彎曲應力變化是否縮小（非精確收斂速率、無解析極限外推）。粗網格及窄板之三項式 Ritz 近似差異可能與 FE 離散誤差重疊；所有門檻僅適用這兩組合成低荷載幾何，不是對真實材料或一般板件的精度保證。輸出持續 `NOT_ADMITTED`，不觀測 Gauss-point 應力峰值、屈曲／缺陷／連接／旋轉反力矩，也不計算 ADM 容量。


### 理想簡支與四邊固定鋁板邊界研究（Stage 56）

`tests/fea_benchmark/envelope_panels/check_simple_supported_aluminum.py` 僅從現有 synthetic aluminum low-load S8R deck 產生固定幾何／材料的理想簡支邊界對照（全周限制面外平移，兩個角點最小面內 rigid-body 約束；保留旋轉自由），不新增任意 user-deck／專案支承輸入或 `run_aluminum_research.py` 的支承選項。使用 100×100×2 mm、synthetic E=69000 MPa、ν=0.33、q=0.0001 N/mm²、n=4／8／16。CI 會真實以 CCX 對各 n 的簡支與既有四邊固定算例求解，透過獨立 Kirchhoff–Navier 奇數雙正弦級數（41／61 項截斷互比）取得理想簡支中心撓度參考，要求簡支撓度大於固定、簡支跨網格變化縮小、n=16 相對 Navier 誤差不超過僅供研究篩選的 12%。同時驗證合成模型身分、材料、拓樸、兩組邊界與受限平移平衡，並提供 SHA-256 來源。這種簡支是假設性理想支承，不代表真實帷幕牆的折邊、扣件、框架接觸、實際支承旋轉勁度、離散錨固或局部挫屈，也不提供 ADM 容量與一般六分量全域平衡驗證；結果仍為 `NOT_ADMITTED`。


### 合成 U 型折邊薄壁懸臂梁殼模型（Stage 57）

`tests/fea_benchmark/envelope_panels/check_u_fold_cantilever.py` 建立固定 synthetic U 型薄壁截面殼元素：長 300 mm、主面寬 40 mm、兩側垂直折邊高 20 mm、板厚 1.5 mm；合成彈性材料 E=69000 MPa、ν=0.33。三段殼共用折角節點、S8R 二次殼元素，沿長度設 8／16 網格；根部六向自由度固定，自由端沿 U 截面以二次線元素一致分配總 1 N 面外集中合力。這是**懸臂梁式 U 型試體**，並非整片受均布風壓的實際帷幕牆折板。

獨立近似以薄壁中面長度積分求中性軸 z=5 mm、Iy=5000 mm⁴，Euler–Bernoulli 懸臂梁理論自由端撓度 `FL³/(3EI)=0.0260869565 mm`（**非精確殼場真值**）。於真實 CalculiX CI 比較荷載功共軛的自由端加權平均位移、根部三向平移反力其中的 z 分量與兩層網格差異；絕對撓度相對梁近似 25%、網格間差 15% 為本合成案例的初步研究篩選門檻，而非通用工程容許差。須確認 exact-head 真實 CCX CI 通過才能宣稱有限元研究對照 PASS。尚未 admission 完整六分量平衡、截面局部翹曲極值、實際折彎圓角與成形材料改變、扣件、接觸、風壓板件、局部挫屈或任何 ADM 承載力；全部維持 `NOT_ADMITTED`。


### 合成 U 型折邊主板均布面壓（Stage 58）

`tests/fea_benchmark/envelope_panels/check_u_fold_web_pressure.py` 僅從 Stage 57 固定 synthetic S8R U 型懸臂殼導出載入方式不同的受限 deck：主面寬 40 mm、長 300 mm、折邊高 20 mm、t=1.5 mm，E=69000 MPa、ν=0.33；主面 WEB element set 接收 `*DLOAD,P,0.0001 N/mm²`，**兩側折邊不直接施加壓力**；根部固定，網格 8／16，材料與節點拓樸不變。獨立 Euler–Bernoulli 理論：中面截面 Iy=5000 mm⁴、名義主面荷載 1.2 N、固定根部彎矩需求 180 N·mm、自由端撓度近似 0.0117391304 mm。這些是小撓度梁近似及初始幾何名義荷載，不是 exact S8R shell 解或任意非線性 follower pressure 合力。

CI 僅採用有可追溯 provenance 的實際 CalculiX 2.21 解，針對 WEB 自由端節點以 Simpson 權重取得 z 向位移，與獨立梁理論交叉比對；要求 16 網格相對差 ≤25%、8→16 變化／理論值 ≤15% 及小撓度範圍成立。使用 `*NODE PRINT ROOT RF` 的原始 RF z 只作有界方向／量級診斷，因 constrained edge 也受到 `*DLOAD`，**不得把原始 RF 升格為獨立純支承力或全域六分量平衡**。本案例只研究合成 U 殼、固定端與均布面壓，不處理四邊支承折板、實際扣件／接觸、折角圓弧與材料成形、局部挫屈、應力場極值或 ADM 構件容量；持續 `EVIDENCE GATED`／`NOT_ADMITTED`。研究篩選門檻不代表工程容許值。


### 合成四邊固定鋁板中心連續加勁肋受限研究（Stage 59）

`tests/fea_benchmark/envelope_panels/check_center_rib_plate.py` 只生成固定合成幾何：100×100×2 mm 的等向線彈性 S8R 平板，E=69000 MPa、ν=0.33、面壓 `WEB,P,0.0001 N/mm²`；沿中心線採共用中面殼節點的連續直立薄壁加勁肋（肋高 0／4／8 mm；肋厚與板厚均 2 mm），板面四邊固定、肋件端部不另指定現場扣件約束，板網格 8／16。僅 WEB 面直接受壓，肋不直接受壓；加肋模型的 shared shell nodes 是**理想連續連接**而非實際焊接、螺絲或接觸的認可。

以四邊固定 Kirchhoff 平板單項 Rayleigh–Ritz 近似取得未加肋中心撓度；另外用同一假設位移形狀的「板彎曲能＋中心薄壁梁彎曲能」取得加肋後預期趨勢。後者採中面肋件 `I=T h³/3` 的理想化能量模型，**不含相容性、局部翹曲、板肋耦合的全場精確解**，只能作受限交叉參考及勁度趨勢合理性檢查，不能作真實截面／材料強度設計。真實 CalculiX 2.21 CI 要求六組合成模型完成、deck／DAT／STA／FRD provenance 可核對、各網格中心撓度隨肋高增加而下降、未加肋細網格接近固定平板 Ritz（研究門檻 20%）、各肋高的兩網格撓度差不超過該組細網格結果的 15%。本案例不能確立正式收斂階數、完全六分量平衡、支承反力矩、薄壁局部挫屈、初始缺陷、材料塑性、連接／扣件容量或 ADM 合格與否；維持 `EVIDENCE GATED` 與 `NOT_ADMITTED`。


### 中心加勁肋端部理想固定的荷載傳遞（Stage 60）

`tests/fea_benchmark/envelope_panels/check_rib_end_transfer.py` 沿用 Stage 59 的固定 100×100×2 mm、E=69000 MPa、ν=0.33、中心高度 8 mm 合成 S8R 板肋共用節點模型。主面 WEB 唯一受 P=0.0001 N/mm²，板面四周固定；僅額外比較「肋端自由」與「肋端上部 16 個節點完全理想固定」這一個位移約束差異，不新增真實扣件、接觸、支承柔度參數或材料容量。本研究在 n=8／16 網格、四組真實 CCX 輸出之間重播。現有 Stage 59 的六組研究仍保留；此模型只是更窄的端部連接剛性邊界比較。

採用板面 WEB 節點的 S8R 平面形狀函數（四角各 -1/12、四邊中點各 +1/3）積分整片原始主面 U3，作為名義固定方向均布荷載的**功共軛平均位移代理（work-conjugate proxy）**；線彈性理論上，同一外力在更受限位移子空間之下的 compliance 不得上升。因本算例用 `NLGEOM` follower pressure，只能在此合成**小位移**下以該線彈性定理作篩選，**不是一般非線性定理**。CI 要求額外約束使平均位移下降，兩網格差異低於研究性 15% 門檻、端部新增 RF 訊號與端部／根部 DAT node coverage 均成立，並以完整 deck／DAT／STA／FRD SHA-256 防止混檔。觀測原始 RF **不能**代表經獨立分離荷載後的純扣件力、支承反力矩或完整六分量平衡。

此功能不提供任意支承輸入、不驗證現場加勁肋焊接／機械扣件、局部板肋應力極值、挫屈或 ADM 容量，`EVIDENCE GATED`、`MATERIAL_CAPACITY_NOT_ADMITTED` 與 `GENERAL_GLOBAL_BALANCE_NOT_ADMITTED` 持續成立。以上篩選門檻僅供 synthetic engineering research。


### 中心加勁肋端部 Z 向有限剛度彈簧研究（Stage 61）

`tests/fea_benchmark/envelope_panels/check_rib_end_spring.py` 復用 Stage 60 同一模型的無額外支承 8／16 網格、同一面壓、材料和四邊固定板面，額外只對 16 個高於板面的肋端節點加入 `SPRING1` DOF 3（Z 向接地彈簧），每個節點分別採合成常數 1000 或 10000 N/mm。每網格另做兩組真實 CCX，無彈簧比較組從**同一次 CI** Stage 60 的輸入／DAT／STA／FRD 重新核對後取用；材料與折板幾何不變。此處不模擬真實角碼、螺絲、焊接、扣件、節點接觸或轉動勁度，亦不把彈簧剛度反推為廠商性能。

使用 WEB 表面 S8R 形狀函數面積積分之 U3 荷載功共軛平均位移代理，比較同一網格的無彈簧／低剛度／高剛度是否逐步降低；並驗證兩網格相對差不超過受限 15% research screening。**同一死荷載的線彈性正半定彈簧勁度**具有能量單調性，但由於此模型採 NLGEOM follower pressure，僅以小變形近似作定性檢查，**不可宣稱是一般非線性定理**。彈簧總力一律標示為 `k × u` 的衍生數值，並非 CCX 獨立量到的連接力／純支承反力；不進行六分量全域平衡或旋轉反力矩 admission。保持 `EVIDENCE GATED`、`MATERIAL_CAPACITY_NOT_ADMITTED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。


### 合成中心加勁肋端部彈簧平移方向對照（Stage 62）

`tests/fea_benchmark/envelope_panels/check_rib_end_direction.py` 只使用 Stage 61 已測試的相同 100×100×2 mm 四邊固定 S8R 主面、中線高 8 mm 肋與 `P=0.0001 N/mm²`，在 16 個肋端高於板面的節點配置每節點 `10000 N/mm` 之 `SPRING1`，針對 global DOF1 (X) 與 DOF2 (Y) 新增 n=8／16 四組真實 CalculiX 合成研究；無彈簧基準從**相同 CI workflow** Stage 60 精確回讀，DOF3 (Z) 從 Stage 61 精確回讀，不重複執行已有案例。試驗唯一變因是彈簧平移作用方向，**未增加 DOF4–6 或旋轉彈簧，也未模擬連接件方向實測與現場扣件**。

以同一主面 S8R 形狀函數的名義荷載功共軛 U3 平均位移代理比較 X／Y／Z，驗證有限、完整輸出與 mesh 相對差 ≤15%。同一線彈性受限系統增加正半定勁度時荷載功不應上升，但 NLGEOM follower pressure 僅把這原理作小荷載 screening：本研究允許與無彈簧**近似相同**，且僅以高於自由 baseline 0.5% 觸發拒絕，**不強制非荷載同向彈簧產生顯著變化，不宣稱任意非線性單調性定理**。彈簧力、能量僅由輸出位移與 `k u` 衍生，不是獨立反力或扭轉力矩；正交方向殼耦合結果須依 real CCX 看待，沒有預設各方向大小排序。研究持續 `EVIDENCE GATED`、`MATERIAL_CAPACITY_NOT_ADMITTED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`，未 admission 工程構件、連接或 ADM 容量。
