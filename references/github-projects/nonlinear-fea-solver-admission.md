# 非線性 FEA 求解器執行研究（KB-CAND-007）

查證日期：2026-10-08。Disposition：**CalculiX = ADAPT FOR EXECUTION PROBE ONLY；非線性工程解法尚未 admission**。

## 選型與授權

- CalculiX CCX：具備 `*STEP, NLGEOM`、殼與材料非線性輸入途徑。官方 upstream `Dhondtguido/CalculiX` 的 GPL-2.0 授權不得等同本 repo 的 MIT；本階段只接受使用者獨立安裝的外部執行檔，不複製、vendor 或重新授權它。
- 公開 `calculix/CalculiX-Examples@316273e9105e44ce7e3ee05059dac1bc3f256a69` 的 `Streifen/sh.inp` 為 90° 彎曲殼板示例，MIT 範例來源，但依賴 CGX 事先生成的 `all.msh`、`fix.nam`、`rot.nam`、`fix.sur`。因此 **單獨 sh.inp 不構成可重現 benchmark**。
- 其他 solver（Code_Aster／OpenSeesPy）暫為 REFERENCE ONLY；尚未進入版本鎖定或實作。

## 第一階段僅有的實作

`scripts/engineering_calc/calculix_probe.py` 是 **獨立 opt-in executable probe**；只可在具備由 caller 預先審查、且所有 include 可取得的本機 `.inp` deck 與指定 `ccx` executable 時執行。以 `subprocess.run`、argv list、不經 shell、限定 cwd／timeout／輸出長度運行。運行非 sandbox，**不接受不可信 deck／include 或 executable**；不能把進程退出碼當成 FE 收斂、結果有效、材料正確或設計 PASS。預設不執行。

已有 mock regressions 僅驗證 opt-in、安全的 argv 邊界及 process status；未在 repo CI 下載 solver 或運行非線性模型。

## 第二階段實際求解 probe（2026-10-08）

公開、合成的 `tests/fea_benchmark/geometric_truss.inp` 由 Ubuntu 24.04 官方套件 `calculix-ccx 2.21-1` 解算；`*STEP,NLGEOM` 在 GitHub Actions 實際運行。固定桿長 100 mm、E=210000 N/mm²、A=1 mm²、自由端施加 30 mm 橫向位移。獨立 Green–Lagrange 解析參考（x/y 平面）為：

- `epsilon = (1/2)*(30/100)^2 = 0.045`
- `RF_x=EA*epsilon = 9450 N`；
- `RF_y=RF_x*(30/100)=2835 N`；
- 末端 `U_y=30 mm`；固定端平面內反力需平衡。

實際 solver `.dat` 最終增量的 x/y 末端與支點反力、位移通過上述解析交叉檢核。Workflow `非線性 FEA 實際執行探針` 成功的候選 run `37717072426`、tested SHA `692a25e231ff3b7f28f0514956cdf468f8631af8`；屬於受限的 **`ANALYTIC_2D_REACTION_CHECK_PASS`**。

**重要限制：** 實際 `.dat` 也出現非零 out-of-plane (`RF_z`) 輸出，該分量未取得獨立物理／元素 formulation 解釋與 validation，**不得**將 x/y 局部解析比對當成全自由度平衡或模型全面正確。真實 90° 殼板案例需 CGX 產生包括 mesh、node sets 的全部 include；尚未 materialize 或跑 shell/plate solver benchmark，尚無 mesh convergence。Glass/metal panel execution remains `NOT_ADMITTED`。當次 workflow 實際執行不由本 Repo `review.py` 或 `calculix_probe.py` 呼叫，不得混稱兩者已整合。

## 公開 90° 非線性殼板實際執行證據

從 MIT 授權上游 `CalculiX-Examples/Streifen` 整理 `shell90/mesh.fbd`、
`shell90/shell90.inp`，以 Ubuntu 24.04 的 `calculix-cgx
2.21+dfsg-1build1` 在 `xvfb-run` 下重建 `all.msh`、`fix.nam`、
`rot.nam`、`fix.sur`，再由 `calculix-ccx 2.21-1` 解算 `*STEP, NLGEOM`。
CI 首次執行因 CGX 缺少終止指令超時，加入 `quit` 後經 Actions
`37717381484` 真正生成相依檔案並完成 CCX shell 求解，
`.sta` 記錄最終增量 `STEP TIME=1.0`，產生 `.frd`。
輸出證據由 workflow `calculix-nlgeom-probe` Actions artifact 保存。

當前程式同時建立 `check_shell90.py` 的 fail-closed 最終增量檢查，與
Green–Lagrange truss 分開執行；沒有將 shell 的 `frd`／`sta` 當作
獨立 stress／reaction／deflection 參考答案。**狀態：
`SHELL_NLGEOM_EXECUTED_REFERENCE_UNVERIFIED`，不是
`SHELL_BENCHMARK_ADMITTED`**。兩個模組的驗證 scope 不能互相外推：

- Truss：完整實際 CCX 運算＋解析 x/y 位移與反力容差檢核，
  `ANALYTIC_2D_REACTION_CHECK_PASS`；z 向反力未 admission。
- Shell：公開旋轉位移案例有實際求解流程／輸出與增量完成證據；
  **沒有**針對殼板的獨立數值答案、反力平衡驗證或網格敏感度。

剩餘主要缺口：可重現的 shell displacement/reaction independent oracle、
不同網格細化的 convergence，以及對真正玻璃／金屬板材料、支承、面外
壓力與設計 acceptance 的分別驗證。不得將上述 smoke 解讀為
`ASTM/ADM` 相關結構設計合規。

## 第三階段：殼板網格敏感度與獨立圓弧交叉檢核

- 使用同一公開 Streifen shell 範例與 CGX／CCX 2.21 執行 20／40／80 個長向分割的 NLGEOM 網格；每個案例必須收斂至最後荷載增量，依 FRD 原始座標識別自由端節點，取平均 X／Z 位移並讀取 `.dat` 固定端 Y 向彎矩。
- 獨立幾何參照採 **Euler–Bernoulli 無剪切純彎、圓弧不伸長近似**：對 L=100 mm、轉角 1.57 rad，`Ux=L(sinθ/θ−1)≈−36.30575 mm`、`Uz=−L(1−cosθ)/θ≈−63.64355 mm`。它是獨立、但**模型簡化**的近似參照，不是精確三維殼元素解。
- 正式 PR #22 的第一輪真實 workflow `37719726103` 結果：
  - 20 分割：Ux −35.99004 mm、Uz −63.12654 mm、固定端 My −2795.254 N·mm。
  - 40 分割：Ux −36.09248 mm、Uz −63.30748 mm、固定端 My −2780.688 N·mm。
  - 80 分割：Ux −36.14116 mm、Uz −63.39338 mm、固定端 My −2775.174 N·mm。
- 位移與彎矩的細化差值均縮小。CI `check_mesh_convergence.py` 對最細網格檢查圓弧參考容差、位移細化趨勢與 40→80 變化範圍、固定端彎矩細化趨勢；不因程序退出 0 而跳過 numerical gate。
- **Admission**：`BOUNDED_SHELL90_GEOMETRIC_BENCHMARK_PASS`（90° 均質彈性殼板、指定轉角案例；網格敏感度與受限位移解析 cross-check）。不代表殼板 general formulation、應力、連接、接觸、鋁板或結構玻璃的設計強度或合規。
- 仍待：獨立殼板反力／彎矩絕對量基準、全自由度反力平衡、細化品質／元素收斂階數、面外受壓板案例、玻璃與金屬板材料／邊界條件專屬 benchmark，以及與 engineering acceptance criteria 連結。不能把本次 bounded PASS 外推到 ASTM、ADM 或帷幕設計合格。

## 第四階段：純彎固定端反力矩近似基準（2026-10-08）

以非線性 90° shell 20／40／80 網格固定端 `.dat` 總力矩對照**外部獨立梁理論**：
`M=EI×θ/L`，以 `E=210000 N/mm²`、`b=10 mm`、`t=1 mm`、
`θ=1.57 rad`、`L=100 mm`，得理論 `|My|=2747.5 N·mm`。

舊的 80 網格輸出 `My=-2775.174 N·mm`，與理論差 27.674 N·mm；
目前 automated gate 容許偏差 35 N·mm，另要求 20→40→80
固定端 `My` 的差值縮小，以及固定端寄生三維合力與非主軸力矩
小於相應標準化限值（5% `|My|/L`、2% `|My|`）。

PR #23 的第一輪真實 CalculiX candidate run `37722229764`
與 repository run `37722229789` 均 PASS；其適用範圍僅為
公開 90° 均質等向彈性殼板模型與近似 Euler–Bernoulli 梁理論比對。
`check_mesh_convergence.py` 仍不宣稱完整自由度 global balance：
它量測的是固定端 section-resultant 的寄生分量，並未對照各施加轉角
的端部反力；殼板應力、接觸、玻璃與金屬板工程承載力均不適用。

## 第五階段：兩端截面與節點反力診斷（尚非完整平衡）

在現有公開 `shell90` 的 CGX `mesh.fbd` 追加 `rot.sur`，
並對 `SFIX`／`SROT` 同時啟用 `*SECTION PRINT ... SOF`；另以
`*NODE PRINT,NSET=Nfix/Nrot` 輸出節點 `RF`。
對 20／40／80 分割進行實際 CCX 2.21 NLGEOM 求解，加入
`diagnose_end_reactions.py` 擷取最終荷載時間的六維截面結果、
兩端節點平移反力以及兩截面直接相加值；資料不完整即 fail-closed。
候選真實 CI `37729008135` 已 SUCCESS，配對 Repo CI
`37729008081` 已 SUCCESS。

**工程發現（80 分割、最終增量，N／N·mm）：**

- 固定端截面：`F=(+0.516657, ~0, −0.043495)`，
  `M=(-0.217474, −2775.174, −2.583286)`。
- 施加旋轉端截面：`F=(+0.000230, ~0, −0.026376)`，
  `M=(-0.131881, +2777.080, −0.001152)`。
- 截面主彎矩絕對值相近，但兩端截面 `My` 和尚差約
  `+1.906 N·mm`；合力並未直接互抵。
- 固定端 `Nfix` 節點平移反力非零；施加旋轉端 `Nrot`
  平移反力接近零。節點 RF1～RF3 **不包含足以認證所有旋轉拘束
  反力的完整資訊**。

`SECTION PRINT` 是受表面法向／切面定義影響的截面力；
`NODE PRINT RF` 是所列節點的受約束反力，不可直接拿兩者
進行全自由度平衡合格判定。最終正確 disposition：
`TWO_END_REACTION_DIAGNOSTIC_COMPLETE_NOT_GLOBAL_BALANCE_PASS`；
**全域平衡 gate 繼續 EVIDENCE GATED**。需要可追溯的外力／位移
拘束工作、含旋轉 DOF 的完整 nodal output formulation 與同一參考
座標系之 wrench transformation 後，才能考慮完整 admission。
保留目前反力差異作為 blocker，不能以近似零或放寬容差掩蓋。

## 第六階段：四邊簡支薄板面外均布壓力（受限）

使用合成、無任何專案身分的 100 × 100 × 1 mm 均質線彈性板，
`E=210000 N/mm²`、`ν=0.3`，以 CalculiX `S8R` 元素、
四邊 `Uz=0`、兩個抑制平面內剛體位移的錨點、`*DLOAD P`
以及 `*STEP,NLGEOM` 執行 4／8／16 分割網格。

獨立來源：Liu & Riggs（2005），*Structural Engineering and Mechanics* 19(3),
Table 2，均佈荷載下四邊簡支正方形 Kirchhoff 薄板中央位移：
`w=0.00406 q a^4/D`、`D=Et³/[12(1−ν²)]`；
<https://www.techno-press.org/download.php?journal=sem&num=3&ordernum=4&volume=19>。
此解析公式**僅適用小撓度線彈性薄板**；不是幾何非線性解析答案，
也不是 ASTM E1300 玻璃承載力方法。

實際候選 CalculiX run `37735614743` 的結果（mm）：

| 網格 | 微小壓力 q=0.0001 N/mm² | 較高壓力 q=0.5 N/mm² |
|---|---:|---:|
| 4 | 0.002149116 | 3.577855 |
| 8 | 0.002133544 | 3.664268 |
| 16 | 0.002129700 | 3.668193 |

微小壓力獨立 Kirchhoff 理論為 `0.0021112 mm`，16 分割結果
偏差約 0.88%，符合明定 3% 容差；兩負載的網格細化差異均逐步縮小。
較高壓力下的實測中心位移遠低於小撓度線性外推的約
`10.6485 mm`，支持此**指定模型**出現 `NLGEOM` 膜內增剛的
定性趨勢，但**沒有**獨立的大撓度精確參考、獨立 global reaction
equilibrium gate 或可用於玻璃／金屬板的工程 acceptance。

Admission 限定為 `BOUNDED_UNIFORM_PRESSURE_PLATE_PROBE`：
可重現 S8R 受壓板件求解＋小撓度獨立參考＋兩種荷載網格細化。
不得由此推導玻璃耐風承載力、金屬板強度、材料破壞或 ASTM／ADM 合規。

## 第七階段：玻璃與鋁板各自的合成受壓基準（2026-10-08）

由 `tests/fea_benchmark/envelope_panels/generate.py` 建立兩類 **100 × 100 × 2 mm 合成均質線彈性板**，以 `S8R`、`NLGEOM` 和 4／8／16 分割進行真正 CCX 求解。兩者皆使用 `0.0001` 與 `0.6 N/mm²` 的數值**測試荷載**，絕非服務風壓或設計壓力，亦未納入破壞。

- Glass proxy：`E=70000 N/mm²`、`ν=0.20`、四邊簡支，獨立小撓度係數 `w=0.00406qa⁴/D`。
- Aluminum proxy：`E=69000 N/mm²`、`ν=0.33`、四邊固定，獨立小撓度係數 `w=0.00126qa⁴/D`。
- 這些只是可追溯的代表性 *linear isotropic material parameters*；玻璃實際組成、熱處理、缺陷／破壞機率與鋁材牌號、加工硬化、屈服／屈曲／焊接均未 modeling，也沒有有限元材料失效準則。

真實 CalculiX CI `37740531071` 在上述合成配置通過；最終中心位移絕對值（mm）：

| 代理材料 | 4 網格、小壓力 | 8 網格、小壓力 | 16 網格、小壓力 | 4 網格、高壓力 | 8 網格、高壓力 | 16 網格、高壓力 |
|---|---:|---:|---:|---:|---:|---:|
| 玻璃代理 | 0.00086351 | 0.00085212 | 0.00085182 | 3.348888 | 3.342554 | 3.343355 |
| 鋁板代理 | 0.00018197 | 0.00022967 | 0.00023822 | 0.9972199 | 1.168893 | 1.198758 |

獨立 Kirchhoff 解析小撓度值：玻璃 `0.00083520 mm`、鋁板
`0.00024408 mm`；16 網格相對差約 1.99%、2.40%，低於
事前設定的 5% bounded 容差。大壓力下兩者位移均小於
小撓度線性比例外推的 95%，呈現定性幾何非線性增剛，且
網格細化差值減小；**大撓度尚缺獨立解析／數值 gold standard**。

本 Stage 限定 `SYNTHETIC_GLASS_AND_ALUMINUM_PANEL_BOUNDED_PASS`；
不代表玻璃、鋁板風壓容量，亦不代表 ASTM E1300、ADM 或
其他結構規範合規。仍待真實支承、風壓分佈／反力平衡、
材料非線性、破壞與荷載組合、材料產品證據及精確驗收門檻。

## 第八階段：玻璃／鋁板均佈壓力與支承節點反力診斷（未通過全域平衡 admission）

`tests/fea_benchmark/envelope_panels/check_reactions.py` 於既有兩種材料、
兩種壓力、4／8／16 分割 S8R 模型讀取最後增量的 `EDGE` 節點
`RF1/RF2/RF3` 總和；並輸出 `NALL` 節點位移，保留未來追蹤
受壓板件變形幾何所需的輸出。此 Stage 僅比較／診斷，**不提供平衡 PASS**。

小壓力 `q=0.0001 N/mm²`，初始面積 `100×100 mm²`，
獨立總外力參照 `|qA₀|=1.000000 N`，實際 CCX 2.21
節點邊界反力 Z 合計（N）：

| 代理材料 | 4 分割 | 8 分割 | 16 分割 |
|---|---:|---:|---:|
| 玻璃代理 | −0.81249924 | −0.911457544 | −0.957030544 |
| 鋁板代理 | −0.81250000 | −0.911458280 | −0.957031214 |

故小荷載下反力缺口依網格約為
**18.750%／8.854%／4.297%**，兩個不同支承／材料模型
有近乎一致的網格相關偏差。候選 CI 最初正確在 3% 門檻
**失敗**（run `37744144365`）。後續將檢查器改為
fail-closed 缺少輸出／非有限值，但對已確認的物理數值不一致
輸出明確的 `UNRESOLVED_SMALL_LOAD_FORCE_GAP` 與
`GLOBAL_BALANCE_NOT_ADMITTED`，不以放寬容差或假定反力總和
正確而將 benchmark 標示為 PASS。真實診斷 CI `37744330901`
已完成；其 SUCCESS 只表示診斷成功執行，不是物理平衡成功。

較大壓力 `q=0.6 N/mm²`：初始 `qA₀=6000 N`，
16 分割玻璃 `ΣRFz≈−5704.082 N`、鋁板
`ΣRFz≈−5741.547 N`；但幾何非線性 follower
pressure 可能依變形後面法線／面積分配，**不可**把
`qA₀` 當作最終外力的精確基準，故只做診斷。

主要 unresolved prerequisite：確認 CalculiX `S8R` 壓力的
完整離散節點外力、內部節點與 constraint/MPC 實際反力語意；
必要時以獨立幾何積分計算 follower pressure 的全域合力，
並保留對照的元素／版本／網格精度證據。釐清之前
**玻璃及金屬板的總外力／支承反力平衡未 admission**，
更不代表玻璃破壞、鋁板屈服／屈曲或 ASTM／ADM capacity。

## 第九階段：S8R 均佈壓力節點力與小荷載平衡檢核（bounded）

CalculiX 官方 `*NODE PRINT` 的 `RF` 包含支承反力與施加在所列節點上的外力；因此四邊支承同時施加 `*DLOAD,P` 的 S8R 板，不能把 `EDGE RF` 直接當作純支承力。參見 CalculiX User's Manual 的 `*NODE PRINT` / `RF` 段落（https://www.dhondt.de/ccx_2.21.pdf）。這是 Stage 8 誤差的候選解釋，不以手冊描述代替實際 CI。

`check_pressure_equilibrium.py` 從實際生成的合成 `panel.inp` 讀取 8 節點 S8R connectivity、幾何、`EDGE` 與 `*DLOAD`，以獨立 3×3 Gauss 積分計算相容壓力等效節點力；只接受初始平面、正向、矩形 S8R 和目前指定邊界條件，拒絕扭曲元素、MPC、轉換座標、缺失／重複 RF、非有限結果及平衡殘差。對規則 n×n 解析預期 `F_edge,load/(qA0)=(2n+1)/(3n²)`，在 n=4／8／16 分別為 0.1875／0.0885416667／0.04296875；與 Stage 8 的觀測缺口高度吻合。

小荷載的比較量為 `corrected_support_z = sum(EDGE RFz) - sum(EDGE equivalent applied Pz)`，和總合力 `qA0=1 N` 比對；若相對殘差或水平寄生反力大於 `1e-4` 則測試失敗。既有 `check_reactions.py` 仍保留原始診斷。此檢核只針對小位移下的合成線彈性板；大荷載 `NLGEOM` 的 follower pressure 不使用未變形面積替代實際外力，不宣稱 full nonlinear equilibrium、材料容量或 ASTM/ADM acceptance。實際 PR #28 exact-head `dacb6869ae0e936ee2261cd2b5667be86c4a28bc` 的 CalculiX CI `37756874281` 與 Repo CI `37756874261` 均 SUCCESS；合併至 `main@6ff1047efa344dcaf0216a02fbdb09fecff75494` 後 Repo CI `37757010107` SUCCESS，已完成 canonical read-back。六組小荷載經修正後支承反力分別為玻璃 −0.999999240／−0.999999211／−0.999999294 N，以及鋁板 −1.000000000／−0.999999947／−0.999999964 N；最大相對平衡殘差約 7.9×10⁻⁷。此為 **`S8R_SMALL_PRESSURE_BALANCE_BOUNDED_PASS`**，不是大變形全域平衡或工程容量 acceptance。

## 第十階段：變形中面 follower pressure 的獨立三維診斷（不構成平衡 admission）

於既有合成 `glass/aluminum` 模型之 `q=0.6 N/mm²`、4／8／16 S8R 網格，讀取實際 `NALL` 節點末增量平移位移及 `EDGE RF`。使用 S8 解析形函數導數、3×3 Gauss 積分與變形後切向量叉積，分別估算中面壓力三維合力及 `EDGE` 相容節點荷載，進而輸出修正支承合力與差額。

`check_follower_pressure.py` 僅接受原有規則、軸向矩形初始網格及無 MPC 的輸入；缺漏節點、重複／非有限數值、翻轉積分點應拒絕。其物理界線明確：CalculiX 的 `S8R` 殼元素在 CCX 中會展開成三維單元，壓力作用面與 expanded shell face／厚度旋轉效應可能不同於所算中面。因此中面積分只是**獨立幾何診斷**，不可將 `corrected RF + midpoint follower resultant` 的小殘差當作真實全域平衡 PASS，也不得為數值吻合調整容差。

相關一手文件：CalculiX 2.21 User's Manual 的 shell elements、`*DLOAD`、`*NODE PRINT`（https://www.dhondt.de/ccx_2.21.pdf）；套件與 workflow 版本仍依 Repo 既有 CI。

最終真實 CI：首次 PR #30 candidate `456259569cc6aa32e95f9931045abc8956553d47` 的 `37758509709` 因缺少明確 `NSET=NALL`，於 `MISSING_NALL_DISPLACEMENTS` 中止，非平衡驗證失敗。修正後 exact-head `fa9b9fa4c7a6cd62f63be93dc25ff1982691b088` 的 CalculiX `37759647404` 與 Repo CI `37759647455` 均 SUCCESS；merge `8f7baadeecde993e64755a72e628bcc4f35ec545` 的 main CI `37759837478` SUCCESS，已 canonical read-back。

最終高壓 `q=0.6 N/mm²`：變形中面之法向積分總 Z 力、扣除中面節點荷載後推算的支承 Z 力及其差額（單位 N）：

| 合成模型 | 4 網格 | 8 網格 | 16 網格 |
|---|---|---|---|
| Glass 中面總 Z 力 | +5980.47755 | +5980.62611 | +5980.61979 |
| Glass 推算支承 Z 力 | −5961.35233 | −5960.79661 | −5960.67006 |
| Glass Z 殘差 | +19.12522 | +19.82950 | +19.94973 |
| Aluminum 中面總 Z 力 | +6000.00000 | +6000.00000 | +6000.00000 |
| Aluminum 推算支承 Z 力 | −5997.82984 | −5998.82605 | −5999.40968 |
| Aluminum Z 殘差 | +2.17016 | +1.17395 | +0.59032 |

相對殘差（3D norm／中面總力 norm）：Glass `0.00319794`／`0.00331562`／`0.00333573`；Aluminum `0.000361693`／`0.000195659`／`0.0000983869`。Glass 差異並未隨網格細化消失。此數值僅表示**中面近似**與 solver RF 不完全相同，尚不能歸因於單一厚度、旋轉或 pressure face mechanism。**`FOLLOWER_PRESSURE_MIDSURFACE_DIAGNOSTICS_COMPLETE`；`GLOBAL_BALANCE_NOT_ADMITTED`**。完整殼單元壓力作用面／厚度轉換及真正支承約束反力定義仍須獨立驗證。

## 真正 benchmark admission 的最低缺口

1. Pin exact CalculiX / CGX version、binary provenance、運作平台及 licensing boundary。
2. Materialize 完整 public test deck／mesh／node sets／include，以及來源版本與 SHA；不得帶入私有專案模型。
3. 執行帶 `NLGEOM` 的大型轉角殼板參考案例，擷取 increment convergence log、位移／反力、平衡殘差；確定 expected values 來自**獨立** reference，而非程式輸出自身。
4. 進行網格敏感度、元素選型及幾何／材料／邊界假設稽核。玻璃／鋁板需各自另有 validation 與可追溯 acceptance criteria。
5. 只有上述完整證據通過才能將狀態由 `EXECUTION_ONLY_NOT_NUMERICALLY_VALIDATED` 提升；不得直接宣稱 ISO、ASTM、ADM 合規。

## 來源

- CalculiX GPL-2.0：https://github.com/Dhondtguido/CalculiX/blob/master/LICENSE
- 公開 90° 彎曲案例：https://github.com/calculix/CalculiX-Examples/tree/316273e9105e44ce7e3ee05059dac1bc3f256a69/Streifen
- 本 Repo 既有 FEA owners：`knowledge/cladding/structural-analysis/plate-fea-modeling.md`、`knowledge/structural-glass/structural-glass-fea-modeling.md`；數值結果須遵守現有 FEA governance。

## 第十一階段研究：展開殼單元作用面與反力來源（EVIDENCE GATED）

**目前僅研究路線，不構成 admission。** Stage 10 在大壓力玻璃板中面 follower pressure 積分與 `EDGE RF` 校正之差約 0.32–0.33%，且網格細化不消失；鋁板約 0.0362% 降至 0.00984%。此差異不能直接歸因於特定厚度、曲率或求解器錯誤。

- 先以官方 CalculiX 2.21 的 shell expansion、`*DLOAD` 壓力面、`*NODE PRINT RF` 語義及輸出格式為一手研究範圍；必須證實 S8R→expanded-solid 的面與符號對應，不可由中面推測實際壓力面。
- 先設計不變更 production kernel 的 **A/B diagnostic**：同一 4／8／16 網格，分別收集 small/large load 的殼中面位移、可驗證的 shell face／expanded element evidence，以及 RF／外力分量；需有獨立幾何積分 oracle 和完整輸出覆蓋／非有限數／重複節點 negative guards。
- 對厚度偏移與 rotations 的幾何 reconstruction，若沒有可驗證的 expanded-node 位置、元素面 connectivity、載荷方向與反力定義，應回報 `SHELL_FACE_GEOMETRY_UNRESOLVED`；**不得**把 `C3D20R` 面荷載與中面 Gauss 積分視為相同，亦不得調整 tolerance 強行 PASS。
- 真正全域平衡 admission 另須確定完整支承反力來源、可能的 in-plane 及 moments／constraints、pressure follower resultant；需用真實 CCX exact-head CI、數值獨立 oracle、main read-back 才可考慮，仍排除 ASTM E1300／ADM capacity。

**Stage 11 起始研究結果：** 目前 repository `generate.py` 只輸出 S8R `*NODE`／`*ELEMENT`、`NALL U` 與 `EDGE RF`；`check_follower_pressure.py` 的 Gauss 積分只重建變形後中面，沒有 expanded C3D20R 的面 connectivity 或壓力面座標。故在現有已 admission evidence 下，**無法直接宣稱已取得精確壓力面全域平衡**。下一步須先取得 solver-level expanded-face 的可追溯輸出或可靠原始碼／手冊映射，再實作對帳。

### 第十一階段原始碼交叉核對：受壓面 1 與 P1（研究證據，尚未認證）

本次定位 upstream `Dhondtguido/CalculiX@master` 下列檔案；**master 是目前讀到的 upstream source，尚未證明與 CI 安裝之 CalculiX 2.21-1 binary 完全一致**，不得冒充 exact-version authority：

- `src/gen3dfrom2d.f`：展開 20-node solid 時，原始 S8R 的 corner nodes 1–4 對應 solid face 1 corners；原始 midside nodes 5–8 對應 solid face 1 midsides（expanded connectivity slots 9–12）；相對面為 solid face 2（slots 5–8、13–16）。展開表面座標涉及厚度、offset、node normal。
- `src/dloads.f`：對 `lakon` 殼元素的一般非 EDNOR、非 I distributed load，標籤分支設定 `label(1:2)='P1'`；**需確認實際 `*DLOAD PLATE,P` 是否通過該分支**。
- `src/dload.f`：此為 user subroutine DLOAD 範例／lubrication coupling，雖列出 `ifaceq` 的 face 1 slots `(4,3,2,1,11,10,9,12)`，**不是足以獨立證明普通均布壓力之 production load integration 路徑**；不得直接將其當作 solver ordinary pressure oracle。

以上只能支持 **candidate face mapping**，不能據此宣稱已精確重建 CCX 實際 follower force。Stage 11 下一個必需的證據是 pin CalculiX 2.21 對應 source revision、普通 `*DLOAD,P` 的內部 load integration path、變形後 expanded face coordinates／rotational MPC 的取得方法。缺任一項，結果為 `SHELL_FACE_GEOMETRY_UNRESOLVED` 並保持 `GLOBAL_BALANCE_NOT_ADMITTED`。原有 Stage 10 的 0.33% 差異不可直接歸因厚度或旋轉。


### 第十一階段套件版本實證與原始碼來源定位（尚未認證受壓面平衡）

- 2026-10-08 GitHub Actions PR #34，exact-head `ca5d200871f3b36c4a733c477be761ab2552e106`、CalculiX run `37773447955` SUCCESS；其執行日誌證明 Ubuntu 24.04.5 LTS 安裝 `calculix-ccx 2.21-1`，套件 archive `calculix-ccx_2.21-1_amd64.deb` 的 apt metadata SHA-256 為 `796f7e0c518817651c4b82d3fb14e38ceebc2b8d2cd503db9e5c2fec21ae2fd3`，實際 `/usr/bin/ccx` SHA-256 為 `6adaabf5bf0382fc2bfd692b984320ed375dba777f7dc8297562f818043faa1b`。以上是 binary provenance，**不等於 source-to-binary reproducible-build proof**。
- 版本相符的公開來源已定位為 [Debian Sources `calculix-ccx/2.21-1`](https://sources.debian.org/src/calculix-ccx/2.21-1/) 與 [Debian 2.21-1 source package](https://packages.debian.org/source/sid/calculix-ccx)（`calculix-ccx_2.21.orig.tar.bz2` 加 Debian packaging/patches）；[Ubuntu noble source package](https://packages.ubuntu.com/source/noble/calculix-ccx) 亦標示 `2.21-1`。**目前尚未逐檔讀取並校驗此 exact source package 的 `dloads.f`、`gen3dfrom2d.f`、ordinary pressure integration routine 與 patches**，不能用 upstream master 取代。
- CI artifact `calculix-nlgeom-probe` 已包含 `tests/fea_benchmark/provenance/calculix-package.txt`。後續須在 exact source package 中交叉核對 `*DLOAD,P`→expanded solid face、quadratic surface integration 與 NLGEOM deformed coordinates；若不能證實，維持 `SHELL_FACE_GEOMETRY_UNRESOLVED`、`GLOBAL_BALANCE_NOT_ADMITTED`、`EVIDENCE GATED`。
