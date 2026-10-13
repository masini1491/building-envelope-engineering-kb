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

## 第十二階段：CalculiX 2.21 原始碼與展開面積分診斷（EVIDENCE GATED）

研究日期：2026-10-09。依維護者提供的原始碼檔案，實際核對 `2.21-1` source package；以 `.dsc` 列示的 SHA-256 驗證兩份 archive：

- `calculix-ccx_2.21.orig.tar.bz2`：`51d229aee320cf685216d360f7c04f9a57af0148fbe840483a964c86c315da82`（1,794,485 bytes）。
- `calculix-ccx_2.21-1.debian.tar.xz`：`6c2a934b66491c9e916cbf6328167d417f7e985b380e200facf92c3e953d255f`（20,872 bytes）。

已檢查 Debian 四個 patches 之修改檔案路徑（Makefile／其他拼字修正／CalculiX.h），未直接修改這次核對的 `dloads.f`、`loadadd.f`、`rhs.f`、`e_c3d_rhs.f`、`shape8q.f`、`gen3dfrom2d.f`、`gauss.f`。未驗證 `.dsc` PGP signature，也尚未重建出與 CI `/usr/bin/ccx` 相同雜湊的 executable，**不能稱為 reproducible binary identity**。

### 已確認的原始碼路徑

- `src/dloads.f`（約 369–386、491–508 行）：一般 S8R 殼壓力 `*DLOAD, PLATE,P,q` 的標籤，非 `EDNOR` 分支轉成 `P1`；`src/loadadd.f` 儲存 face-load 資料。不能外推成所有 load 類型。
- `src/gen3dfrom2d.f`（約 106–111、145–184 行）：S8R 展開所用的 thickness、normal、offset 形成三維節點；上下面不是原 S8R 中面。原本 `NALL U` 不足以獨立重建 rotation/MPC 調整後全部 expanded node。
- `src/rhs.f`（約 156–161 行）在 distributed forces 路徑呼叫 `e_c3d_rhs`；`src/e_c3d_rhs.f`（約 59–64、397–405 行）之 `P1` C3D20 face slot 順序為 `(4,3,2,1,11,10,9,12)`。
- `src/e_c3d_rhs.f`（約 426–439、476–505、536–549 行）依變形狀態使用 `co + vold` 的面座標、`gauss2d2` 四點及 `shape8q` Jacobian，在節點 force accumulator 使用 `-N_i × q × J_vector × weight`；`src/shape8q.f`（約 61–114 行）確認二次形狀函數及有向面 Jacobian。源碼路徑由版本相符 archive 核對，不再以 moving upstream `master` 代替。

### 本階段獨立幾何診斷之認證界線

`tests/fea_benchmark/envelope_panels/check_expanded_face.py` 只接受明確提供的 **20 個 C3D20 expanded node 最終三維座標**及正壓力，獨立運算 P1 面的 2×2 Gauss 等效節點力與總合力；`test_expanded_face.py` 使用合成平面、傾斜面解析參考及 failure-path guards 進行 sanity check。不得把輸入自動視為真正 CCX expanded solid data；此測試也沒有從 8-node 中面 `U` 推定 expanded node `U`。

本階段最多可稱 `EXACT_SOURCE_FACE_PATH_RECONCILED` 與 `EXPANDED_FACE_SYNTHETIC_ORACLE_PASS`（僅限 source route 與合成解析幾何）。**未取得實際 CCX expanded-face 當前座標、完整 MPC/rotation 轉換與全部 reaction 定義**；Stage 10 玻璃約 0.33% 殘差仍無確定歸因；保持 `SHELL_FACE_GEOMETRY_UNRESOLVED`、`GLOBAL_BALANCE_NOT_ADMITTED`、`EVIDENCE GATED`，不宣稱 E1300／ADM 工程 capacity。

來源：[Debian CalculiX 2.21-1 source package](https://sources.debian.org/src/calculix-ccx/2.21-1/)；本 Repo 不複製或重新授權 GPL-2.0 原始碼。

## 第十三階段：實際 FRD 展開節點證據與 P1 幾何合力（待 CI 實測）

研究日期：2026-10-10。使用 SHA-256 已核對的 CalculiX 2.21 原始碼，進一步確認 `src/frd.c`（座標／C3D20 拓撲）、`src/frdvector.c`（節點位移）及 `src/noelfiles.f`（`*NODE FILE,OUTPUT=3D`）可形成 **候選** 的三維展開節點取證路徑；`src/frd.c` 會重新排列 C3D20 的 20 節點順序，不能直接將 FRD 連接表當作 CCX 內部 slot。

- 合成板件 deck 明確要求 `*NODE FILE,OUTPUT=3D` 的 `U`，保留既有 `NALL U` 與 `EDGE RF` 診斷；CI 保存 `.frd`。
- `check_expanded_frd.py` 解析 ASCII FRD 的參考節點座標、C3D20 拓撲與最後一步位移；還原 CCX 內部元素 slot，嚴格要求所有展開面相關節點都有參考座標及位移，且最後 time=1.0；否則拒絕。輸出由真實 CCX 形成的 P1 受壓合力供研究，不得當作平衡 PASS。
- `test_expanded_frd.py` 使用 synthetic FRD fixture 驗證排列、固定欄寬、缺少展開位移、元素種類錯誤、非最終時間、重複／非有限座標及缺檔路徑。fixture PASS 不能代替真實 CCX FRD coverage。
- **Gate**：若 CI 證明 `OUTPUT=3D` 仍未產生完整 expanded-node `U`，必須保持 `EXPANDED_FACE_COVERAGE_UNRESOLVED`，不可自動從中面 U、rotations 或推測的 MPC 補齊。即使真實 FRD 合力已取得，仍缺完整支承反力及壓力作用節點反力定義；保持 `GLOBAL_BALANCE_NOT_ADMITTED`、`EVIDENCE GATED`，不宣稱 ASTM E1300／ADM capacity。

### 第十三階段實測結果與第十四階段差異診斷（2026-10-10）

PR #37 的 exact-head 真實 CalculiX CI `38005598716` 與 Repo CI `38005598674` 均 SUCCESS，合併 main `76b66958af96da48115fc85172ec4fe18831469c`，main CI `38005697877` SUCCESS。FRD 的 20-node C3D20 拓撲、參考座標、最終 3D U 均由真正 CCX 輸出取得；不是合成座標推估。六個高壓案例（q=0.6 N/mm²）實際 P1 三維合力如下：

| 合成材料 | 網格 | 原始 S8R 節點數 | FRD 節點數 | P1 受壓面 Z 合力（N） |
| --- | ---: | ---: | ---: | ---: |
| glass | 4 | 65 | 155 | +5960.505913 |
| glass | 8 | 225 | 531 | +5960.653713 |
| glass | 16 | 833 | 1955 | +5960.641960 |
| aluminum | 4 | 65 | 155 | +6000.000000 |
| aluminum | 8 | 225 | 531 | +6000.000000 |
| aluminum | 16 | 833 | 1955 | +6000.000000 |

這些值來自實際 FRD 的 P1 面積分；僅為獨立外力幾何診斷，尚非反力平衡。Stage 10 中面積分的 glass Z 合力約 +5980.48／+5980.63／+5980.62 N，和實際 P1 面約差 20 N，足以證明先前中面近似**不能當作**真正受壓面；不能把差異單獨歸因於 thickness、rotation 或 offset。

第十四階段增加 `compare_pressure_surfaces.py`，並以兩項定向測試驗證：同時列出 P1 − 中面外力差及 P1 +「先前用中面節點外力修正」的 EDGE inferred support 差。後者是 **mixed discretization diagnostic**，不具完整平衡物理意義；絕不把其殘差較小當作 `GLOBAL_BALANCE_PASS`。仍須查明 CCX 原始 `RF` 如何包含外力、約束及 MPC 反力，並獨立核對完整邊界力後，才可能討論全域平衡 admission。狀態維持 `EVIDENCE GATED`。

## 第十五階段：RF 源碼投影與 NALL／EDGE 證據交叉核對（候選）

研究日期：2026-10-10；由維護者提供並以 `.dsc` SHA-256 校驗的 CalculiX 2.21 source archive 實際檢查：

- `src/results.c` 的 `resultsmechmt` 聚合 `fn`（節點 internal force），再呼叫 `resultsforc`；`src/resultsforc.c` 對 MPC dependent/independent terms 做係數與 `fmpc` 的轉換，不是直接輸出支承外力；`src/printout.f` 的 `RF` 分支可能先呼叫 `map3dto1d2d` 將展開實體力映回原殼節點，`src/printoutnode.f` 輸出的是 `fn(j,node)`，而非只含拘束反力的向量。
- `*NODE PRINT,NSET=NALL` 現要求 `U,RF`，保留 `EDGE RF`；`audit_rf_projection.py` 僅檢查同一個 CCX `.dat` 的原殼 NALL/EDGE RF 在共同節點的投影一致性、完整性與節點力和，**不是**獨立平衡式。四項 synthetic parser tests 為負向守門；真實 CI 執行後才可標記 real-CCX coverage。
- 源碼含 MPC 與 shell mapping，直接從 `RF` 當作支承反力是不成立的。仍須對完整 `fext`（含 pressure、constraint/MPC redistribution）與映回 `fn` 的語意建立對應，不能以 `NALL RF` 求和替代外力／支承力平衡。保持 `GLOBAL_BALANCE_NOT_ADMITTED`／`EVIDENCE GATED`。

## 第十六階段：RF 觀察更正與投影範圍限定（2026-10-10）

第十五階段 PR #39 的修正後 exact-head CalculiX CI `38021387071` 與 Repository CI `38021387075` 均 SUCCESS；merge `1ce79f26f305da861546a22568955ae8cc25185b`，合併後 main CI `38021467115` SUCCESS。前一輪曾提出「加入 NALL RF 使 EDGE RF 改變」的推測，**已由同一批 CI 日誌交叉核對否定，撤回該推測**。

| 模型 | 網格 | Stage 10/14 EDGE RF Z (N) | Stage 15 EDGE RF Z (N) | 判讀 |
| --- | ---: | ---: | ---: | --- |
| glass | 4 | −4841.926 | −4841.926 | 一致 |
| glass | 8 | −5432.08052 | −5432.08052 | 一致 |
| glass | 16 | −5704.08197 | −5704.08197 | 一致 |
| aluminum | 4 | −4872.7044 | −4872.7044 | 一致 |
| aluminum | 8 | −5467.47016 | −5467.47016 | 一致 |
| aluminum | 16 | −5741.547032 | −5741.547032 | 一致 |

Stage 15 新增的 `NALL RF` 不是「獨立支承反力」，其完整節點 Z 向加總約為 +0.00050／−0.00044／−0.000228 N（glass 4／8／16）及 +0.00040／−0.00007／−0.000467 N（aluminum 4／8／16），主要表示投影後內部節點力互相抵消；不能用這個接近零的結果宣稱 external load + boundary reaction 的全域平衡。現有 `EDGE RF` 和 `NALL RF` 共用 CCX internal-force projection path，故兩者的一致性僅為**同來源交叉核對**，不是獨立數值 oracle。

**下一個證據缺口**：需要釐清 `resultsforc`、`map3dto1d2d` 及 `RF` 寫檔之前如何處理 external follower pressure、MPC dependent-node load redistribution 與拘束自由度的真正 reaction。不得直接將 `NALL RF` 或 `EDGE RF` 的全域求和視為反力平衡證明。狀態繼續 `GLOBAL_BALANCE_NOT_ADMITTED`／`EVIDENCE GATED`。

## 第十七階段：NALL RF 輸出選擇的隔離 A/B 實驗（候選）

2026-10-10：建立 `check_output_selection_ab.py`，以同一份 synthetic large-pressure glass／aluminum S8R deck 進行六組配對真實 CCX 求解。A 組要求 `*NODE PRINT,NSET=NALL; U,RF`；B 組僅移除 `NALL RF` 輸出要求，保留 `U`。其餘網格、荷載、材料、拘束、`NLGEOM` 和 `EDGE RF` 完全一致。獨立比對兩組原始 deck 的唯一差異、最後增量的 NALL U 和 EDGE RF，並保留完整 CI 日誌。合成負向測試驗證 deck 不相等及標記缺失時拒絕。

**目的**：驗證先前「NALL RF 可能改變 EDGE RF」的推測是否可由可重複的真正求解器 A/B 實驗否定；單次同檔交叉核對不等於跨設定實驗。即使 A/B 完全一致，仍只能 admission `OUTPUT_SELECTION_INVARIANCE_ONLY`，不能以其推論完整支承反力或 `GLOBAL_BALANCE_PASS`。完整大變形平衡仍 `EVIDENCE GATED`。

## 第十八階段：C3D20 展開節點力與 S8R 殼節點 RF 投影驗證（候選）

研究日期：2026-10-10。沿已校驗的 CalculiX 2.21 原始碼 `results.c`、`resultsforc.c`、`printout.f`、`printoutnode.f`、`frd.c` 與 `map3dto1d2d.f` 查證，`RF` 是 internal nodal force 的投影，而不是只含拘束自由度的支承反力。針對一般 quadratic S8R 殼元素，`map3dto1d2d.f` 使用 `node8` 分層節點對照：角點取三個厚度方向節點，邊中點取兩個厚度方向節點；力模式（`iforce=1`）各展開節點只計入一次，而非再依同一原殼節點相鄰元素 incidence 做平均。

本階段新增 `check_rf_3d_projection.py`：以真正的 `*NODE FILE,OUTPUT=3D` `U,RF` 產出的 FRD `FORC` 資料和 C3D20 connectivity，依原始碼對照重建 3D→S8R nodal-force projection（力模式只計入一次、不除以 incidence），和 `*NODE PRINT,NSET=NALL` 的 `RF` 逐原始節點比對，含資料完整性與共用節點唯一歸屬守門。以 `test_rf_3d_projection.py` 驗證合成正向與缺漏、重複、不合幾何排列等負向案例。

**驗證門**：FRD 必須明確包含最後 time=1.0 的完整 expanded `FORC`；若 `OUTPUT=3D` 使 `RF` 缺漏或 solver 不支援，拒絕並維持未認證。即使映射數值相符，這是與 CCX 原始碼、相同求解器內部力資料的交叉驗證，不是獨立 global reaction balance。不得因 `NALL RF` 全域和接近零便聲稱 follower pressure 已與支承反力平衡；維持 `GLOBAL_BALANCE_NOT_ADMITTED` 與 `EVIDENCE GATED`。

### 第十八階段候選失敗與根因修正（2026-10-10）

第一版 PR #42 exact-head `bbe1d0b542bb5dcfa9ed8cfa4efd84c4d64117d6` 的 Repo CI `38049657499` SUCCESS、CalculiX CI `38049657595` **FAIL**。失敗點為真正 CCX 3D FRD `FORC` 映回 `NALL RF` 的最大節點分量相對差 0.37689231，並非測試的非線性收斂失敗；五項 synthetic unit tests 均 PASS。下載該 run 的 `calculix-nlgeom-probe` artifact（ID `11669230685`）後，以 glass 4 網格真實 FRD／DAT 重現。

**根因**：原候選誤把 `map3dto1d2d.f` 的場量平均套用至 `iforce=1` 力路徑；CalculiX 在力路徑以 `inum(node2d)=-1` 標記，避免 shared expanded node 重複累計，最後力值**不除以**相鄰元素 incidence。誤除使 shared node 的 RF 約變成原值 1/2 或 1/4。修正後，以相同真實 glass 4 原始 artifact 重新對帳，三維節點力加總接近零，映射後節點力與原 `.dat` 的差距主要為文字輸出捨入精度。本修正須通過新的 exact-head CI 才能正式 admission；不修改求解器或放寬 0.0002 的 serialization tolerance。持續 `GLOBAL_BALANCE_NOT_ADMITTED`。

## 第十九階段：受限合成板件的三向平移力平衡重建（候選，2026-10-10）

**前提／來源**：以 CalculiX 2.21-1 原始碼 `e_c3d_rhs.f` 壓力 P1 路徑、`map3dto1d2d.f` (`iforce=1`)、`resultsforc.c`／`printoutnode.f`，以及 Stage 18 實際 CCX `.frd`/`.dat` 成功算例為證據。針對 repo generator 的合成 S8R 板件，原始印出的 `NALL RF` 是**內部節點力**，不能直接當作支承反力。此候選腳本只重建可觀測的 Cartesian translational residual：用真實 CCX expanded C3D20 節點最終座標，獨立計算 follower `P1` 的等效展開節點外力，再沿已驗證 node8 對照映回 S8R 原節點。於已知明確約束的平移自由度，採 `R_constrained = internal_RF − reconstructed_P1_pressure`；於其餘平移自由度要求 `internal_RF − reconstructed_P1_pressure ≈ 0`。不是 CCX 原生獨立輸出的支承反力。

- **模型 scope**：僅 `generate.py` 產生的 `glass`（四邊 U3 簡支，2 個定位點補 U1／U2）與 `aluminum`（邊界 U1–U6 固定）的六組高荷載（q=0.6 N/mm²；4/8/16 網格）、線彈性 isotropic S8R、`NLGEOM`。只審核 1/2/3 **平移分量**；不代表 U4–U6 旋轉、彎矩、shell director、MPC/constraint multiplier、接觸或其他負載機制之平衡。
- `check_reconstructed_pressure_balance.py` 要求恰當的材料與零位移 `*BOUNDARY` 契約，不接受不明約束組合；強制完整真實 FRD 20-node 座標／U、真實 `NALL RF`，並先通過 Stage 18 FRD→`.dat` 內力投影交叉檢核。重建 P1 nodal load 不允許與全部外力合力不符。
- 真實 Stage 18 artifact `11669230685` 的本機初步證據（**不同於正式 exact-head CI**）：6/6 合成模型的三向合力 + 重建支承合力，相對歐氏範數殘差皆小於 1.52×10⁻⁷；未約束平移自由度最大差除以壓力總合力皆小於 1.2×10⁻⁸。偏差包括 DAT／FRD 可見文字輸出精度，容差暫採 `GLOBAL_REL_TOL=5e-7`、`FREE_REL_TOL=1e-7`，均須由 CI 實跑驗證而非僅依此宣稱 admission。
- 六項定向單元測試含解析平面 P1 分配、known-simple support layout、missing FRD node、非法約束、自由度及約束反力刻意擾動、不一致或非有限力值等 fail-closed paths。**必須同時通過 PR exact-head Repo CI 與實際 CalculiX CI，再能 admission 此限定驗證**。
- 此外，仍不等同能從 CalculiX 直接獨立量得拘束反力，更非一般殼板 global six-component force/moment balance 或玻璃／鋁板承載力、ASTM E1300／ADM 規範檢核。保持 **`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`、`EVIDENCE GATED`**。


## 第二十階段：展開節點幾何力矩資訊保真診斷（candidate，2026-10-11）

**Stage scope**：只觀察已驗證合成 S8R 模型的 CalculiX 2.21 `OUTPUT=3D` FRD expanded-node 資料，在同一個 Cartesian 原點（0,0,0 mm）計算壓力等效節點力與展開節點內力的 `Σ(r×F)`。先要求 Stage 19 的平移重建與 Stage 18 的投影對照全部通過。這是 **geometric-moment observation**，不是完整六自由度平衡，亦不是獨立支承反力／反力矩測量。

- 新增 `check_expanded_moment_diagnostic.py` 與 `test_expanded_moment_diagnostic.py`，利用 Stage 13/18/19 現有 parser／P1 積分，對實際 FRD 全部展開節點之最終座標、內力與重建壓力節點力計算 `ΣF` 及 `Σ(r×F)`；不以中面原節點替代作用位置。
- 五項 synthetic tests 中，兩個厚度方向展開節點具相反切向力的純力偶，合力為 0、力矩不為 0，證明原殼節點三向力投影會遺失力矩資訊；另涵蓋解析力矩、座標原點變化、資料缺漏及非法／非有限值。這些 synthetic tests 不等於實際 CCX admission。
- `unpartitioned_geometric_residual_Nmm` 是 **未分類內力與外力幾何力矩之差**，不能視為支承反力矩、MPC multiplier 或全域平衡殘差。即使它接近零，也不能給出 full six-component PASS。輸出固定標示 `six_component_balance=NOT_ADMITTED`，並將 rotational reactions、rotational MPC multipliers、independent support reactions 標示 `UNOBSERVED`。
- 這一版未提供 `U4/U5/U6`、`RM`、`MPC` 的可靠可觀測契約，且未重新完成 CalculiX 2.21 exact-source 的 constraint-related routines 對照。完整三維力矩、director、offset、constraint-couple 與 MPC 力重新分配仍屬 evidence gap；不得把 `Σ(r×F)` 本身當成完整 `ΣM=0`。
- **Admission gate**：須有 Stage 20 PR exact-head Repository CI 與真實 CalculiX CI、merged main CI 及 canonical read-back，才可認證上述受限診斷在真實合成案例上可重現。最終 engineering capacity／六維 global balance 仍為 `GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`、`EVIDENCE GATED`，不得聲稱 ASTM E1300／ADM 容量。



## 第二十一階段：平移支承幾何力矩及未觀測力偶需求（候選，2026-10-11）

- **限定 scope**：只使用 Stage 19/20 六組合成 S8R／NLGEOM 板件已驗證的原始節點平移限制和真實展開 FRD／DAT。先執行 Stage 20/19 gates；無法通過不得產生力矩診斷。
- Stage 20 的 expanded P1 力矩與 Stage 19 重建平移支承力分別取自真正受壓面及原始 S8R 節點變形位置；兩者必須採共同 Cartesian 原點。計算 `required_unobserved_couple_if_equilibrium = −(M_P1 + M_reconstructed_translation_support)`，**只是維持靜態平衡所需要的條件式殘餘力偶，不是獨立輸出、實測或驗證之旋轉支承反力矩**。
- 新增 `check_required_couple.py` 與 `test_required_couple.py`（六項 synthetic tests），涵蓋平移力矩、剩餘力偶需求、原點變化、平移平衡先驗守門、缺失節點／錯誤自由度與非有限值。Real CCX 只能確認已支援合成 fixture 的計算可重現，不能認證 MPC/rotation。
- CalculiX 2.21-1 的 `gen3dboun.f`／`gen3dmpc.f`／`gen3dforc.f` 源碼逐行對帳及旋轉反力輸出契約尚缺證據；不得以 upstream moving branch 或異版本使用手冊代替 exact-version 原始碼。對 rotational reactions、MPC couple 和 independent support reaction 仍輸出 `UNOBSERVED`。
- Admission 需 PR exact-head Repository CI／真實 CalculiX CI、main CI 與 canonical read-back。即使數值合力矩很小，`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`、`EVIDENCE GATED` 仍然成立，且不涉及玻璃／鋁板正式容量設計。


## 第二十二階段：CalculiX 2.21 殼旋轉 SPC／MPC 原始碼路徑取證（2026-10-11）

**原始碼身分與權利邊界**：使用維護者提供的 Debian source package `calculix-ccx 2.21-1`，與 `.dsc` SHA-256 重新對帳：`calculix-ccx_2.21.orig.tar.bz2` 為 `51d229aee320cf685216d360f7c04f9a57af0148fbe840483a964c86c315da82`（1,794,485 bytes），Debian `calculix-ccx_2.21-1.debian.tar.xz` 為 `6c2a934b66491c9e916cbf6328167d417f7e985b380e200facf92c3e953d255f`（20,872 bytes）。檢查四個 Debian patches 的修改路徑：未改動下述 `gen3dboun.f`、`gen3dmpc.f`、`gen3dforc.f`、`resultsforc.c`、`printout.f` 或 `printoutnode.f`。此身分只證明**版本相符之封包原始碼**；未驗證 `.dsc` PGP signature，亦未重建比對 Ubuntu 安裝 binary SHA，不能冒充 source-to-binary reproducibility。僅記錄位置和最小語意摘要，不複製 GPL-2.0 原始碼至本 Repo。

### 來源對帳／適用範圍

| exact 2.21 source | 觀察路徑／行號 | 此次能支持的 claim |
| --- | --- | --- |
| `src/gen3dboun.f` | 63–72；76–128 | 擴展殼／梁 SPC 前會處理 shell 旋轉值；已存在 knot 的旋轉 DOF `idir > 3` 可導到 `rig(node)` 對應旋轉節點之 1–3 平移型 SPC，不能直接視為原始 S8R 節點的獨立旋轉 reaction |
| `src/gen3dboun.f` | 568–584；617–643 | 一般非非線性動力情形的原始旋轉 SPC 進入 mean-rotation MPC 路徑；對殼法向 drilling 軸的旋轉（`abs(dot) > 0.999`）可被忽略，因此 `EDGE,1,6` 文字不能自動解讀成六個可量測反力分量 |
| `src/gen3dboun.f` | 657–742 | 殼內平面轉軸的旋轉值以 `MEANROTBS` mean-rotation MPC 及新增 SPC angle term 轉換；需原始 MPC 係數與相應約束力，不能直接從 `NALL RF` 取得完整轉矩 |
| `src/gen3dboun.f` | 144–212 | 非線性動力條件下存在另外的 knot generation 分支；不可套用靜態驗證的 mean-rotation 結論到所有分析模式 |
| `src/gen3dmpc.f` | 41–67、116–215 | 既有 MPC 所引用殼旋轉自由度／依賴展開節點的轉換具有不同路徑；在某些 knot 情況轉成 `rig(node)` 的 1–3 DOF，不代表能從 FRD `FORC` 反推出完整 multiplier |
| `src/gen3dforc.f` | 131–149；571–705 | 指定原始殼節點轉矩時，也可能轉向 knot／mean rotation MPC；此與 `*DLOAD,P` 不同，本 Repo 尚無對應受控載荷實測 |
| `src/resultsforc.c` | 34–59；75–134 | `fmpc` 與 dependent/independent term 做 MPC 內力再分配，且對 `ndir>3` 有跳過路徑；投影後 `RF` 並非所有約束 multiplier 的獨立列印值 |
| `src/printout.f`／`src/printoutnode.f` | 85–93、132–137／95–111 | 原殼 `RF` 經 `map3dto1d2d(iforce=1)`，輸出標頭仍為三分量 `forces (fx,fy,fz)`，不提供可直接認證的 `RM4–RM6` 反力矩觀測欄 |

以上是**原始碼語意研究**；不表示任意受限 shell model 皆可獨立產生全域力矩平衡，亦不證明 `fmpc`、所有 boundary reaction 或 director offset 的物理歸屬已可從目前 DAT／FRD 讀出。

### 下一個 bounded empirical gate

同一平面、等向性、合成 `S8R`、`NLGEOM`、`*DLOAD,P` 的鋁板 fixture，以原始 `EDGE,1,6,0.` 與只移除法向旋轉 `EDGE,1,5,0.` 作配對 **真實 CCX A/B 求解**。其他 deck 字元須完全相同，比較最終原節點 `NALL U`、`NALL RF` 與 expanded-node FRD 觀測，任何模型／輸出缺漏 fail-closed。若 A/B 相同，只能認證本限定 fixture 中 U6 的 output-selection／constraint invariance，**不能**宣稱所有殼的 drilling rotation 一律不起作用、所有 MPC 已釐清或六分量平衡 PASS。無法執行則保留此 empirical gap。

**工程狀態不變**：`EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`；不做 E1300／ADM 正式容量計算。

## 第二十三階段：合成鋁板 U6 旋轉 SPC A/B 求解（候選，2026-10-11）
以相同線彈性、平面 S8R 合成鋁板 NLGEOM、P1 pressure 以及 4／8／16 網格，只改變 EDGE 原始節點拘束 DOF 範圍 1–6 改為 1–5。其他參數及輸出須相同。

- 真實 CCX paired 求解後，使用 check_rotation_spc_ab.py 檢查完整 NALL U、NALL RF、expanded FRD U 以及元素拓撲，回報最大位移和內力差異，observed_exact_text_invariance 只代表文字精度下完全一致，不等於一般工程不變性。
- test_rotation_spc_ab.py 驗證唯一 deck 差異與缺失、重複拘束 fail-closed。計算缺漏或 FRD／DAT 不完整即拒絕。
- Stage 22 exact-source 靜態 mean-rotation／drilling path 為研究背景；結果不提供獨立 rotational reaction、MPC multiplier 或 general six-component global balance。
- 完成須 PR exact-head Repo CI＋真正 CalculiX CI、main CI 與 canonical read-back。無論 A/B 差異如何，整體 EVIDENCE GATED、GENERAL_GLOBAL_BALANCE_NOT_ADMITTED。

## 第二十四階段：三維展開節點力矩與殼節點投影遺失力偶（候選，2026-10-11）

- 利用 Stage 18 已驗證的 node8 C3D20→S8R 力投影歸屬，將每個展開節點位置寫為 original S8R current position 加上 expanded-relative arm，分解 Σ(x_expanded×F) 為 Σ(x_shell×F_projected)＋Σ((x_expanded−x_shell)×F_expanded)。這是同一組內力／外力的幾何恆等式，不是獨立旋轉 reaction。
- 對 Stage 20 真實 CCX expanded FRD internal FORCE 與 Stage 19 獨立積分的 P1 nodal load 分開執行 moment partition；要求節點完整、單一原始殼節點歸屬、Stage 18/19 先驗 gate 及 algebraic force/moment partition closure。
- 新增 check_expanded_moment_partition.py 和 test_expanded_moment_partition.py；合成測試含隱藏的純力偶、arm + local couple 重組、缺少 shell／expanded position、非有限力值。真實 A/B 需由 exact-head CalculiX CI 完成。
- 此處的 relative geometric couple 不能冒充 CCX 自主輸出的 U4–U6 旋轉反力或 constraint MPC multiplier，不能將恆等式 PASS 提升為六分量全域平衡。狀態保持 GENERAL_GLOBAL_BALANCE_NOT_ADMITTED、EVIDENCE GATED。


## 第二十五階段：隔離重編譯之 MPC instrumentation（候選，2026-10-11）

- **使用者授權**：可在隔離研究環境對已驗證版本 CalculiX 2.21 原始碼最小插樁及重編譯，並與未修改原始碼構建之 CCX 比對。維持 GPL-2.0 授權邊界，不將 GPL solver 原始碼或 executable 複製／納入本 MIT/CC BY 知識庫。
- **受控輸入**：Debian upstream `calculix-ccx_2.21.orig.tar.bz2` SHA-256 `51d229aee320cf685216d360f7c04f9a57af0148fbe840483a964c86c315da82`；`src/resultsforc.c` SHA-256 `d1de9498ac715a7f08da0b7beba3c92c7c2f1030c85c37122d2708f2f480cad0`。只有 exact hash 與唯一插樁錨點皆成立才可建立 instrumented 變體。
- **測量責任**：於 `resultsforc.c` 已完成數值更新後，以 opt-in `CCX_MPC_AUDIT_FILE` 輸出每次 `calcul_fn==1` 下 MPC 個數、`MEANROT` 類型數量、`abs(fmpc)` 最大值；不改 force redistribution 邏輯。不輸出所有 MPC mapping、原始殼節點對應或約束作用位置，亦不能由此求得旋轉支承反力矩。
- **驗證**：兩組 solver 從相同原始碼與 build flags 開始，只讓 instrumentation differ；相同合成 aluminum S8R P1 高荷載 deck 比對 `NALL U/RF`、expanded FRD U/RF 與拓撲，要求文字精度下逐項相同並保留有限 trace；任何 source hash、追蹤資料、mesh／output 缺漏、位移或 force mismatch 一律 fail closed。
- **執行邊界**：CI runner 下載 source 時先校驗 SHA-256，隔離編譯原版／插樁版，使用官方依賴；不得發佈或上傳修改 GPL solver binary。CI 若因依賴、compiler、來源下載或 instrumentation 自身失敗，仍以實際原因記錄，絕不把失敗視為工程缺陷或放寬數值檢核。
- **Admission 不擴張**：這是 source-internal MPC redistribution observability，並非獨立 `U4/U5/U6` reaction couples、constraint multiplier completeness、任意 shell global six-component moment balance 或 ASTM E1300／ADM strength check。維持 `GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`、`EVIDENCE GATED`。

## 第二十六階段：MEANROT 係數／節點 term 有界可觀測診斷（candidate，2026-10-11）

Stage 25 已驗證原版與 opt-in 插樁版於合成鋁板 4／8 網格具相同文字精度輸出。此候選僅在相同、SHA 固定之 2.21 原始碼的隔離再編譯中加入第二個 opt-in `CCX_MPC_TERMS_FILE`；不改動核心計算。

- 記錄 `resultsforc.c` 的每次呼叫 ID、`MEANROT` 的 MPC ID、term 序號、solver 內部 node ID、DOF、係數及 `fmpc`。對 term chain 過長、資料缺漏、非有限值、不一致呼叫順序 fail-closed。
- 保留 Stage 25 pristine／instrumented 的相同 deck 及 U/RF/FRD 數值對照，追加第二個 opt-in 版與 pristine 比對。只有真正執行 CI 才能宣稱 exact-head real solver validation。
- 內部 node ID 與 FRD ID 的數值吻合不是物理身分證明；不可僅憑兩者 ID 相同就將 term 力矩歸到 shell director、rotational reaction、MPC multiplier 或支承反力。新的 `term_node_ids_in_expanded_FRD` 僅是 coverage diagnostic。
- 只把研究用診斷腳本和受限證據說明保存於公開 KB；不公開 GPL 原始碼或 binary。完整六維力矩平衡仍 `GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`、`EVIDENCE GATED`。


## 第二十七階段：MEANROT term 節點身分與旋轉輸出限制（來源研究，2026-10-11）

**Source identity**：沿用已核對 SHA-256 的 CalculiX 2.21 上游原始碼，逐行檢視 `src/gen3dboun.f`、`src/resultsforc.c`。此段為來源路徑對帳與後續測試約束，不是新的真實 solver runtime outcome。

- `gen3dboun.f:568–583`：在指定殼旋轉 SPC、且非對應非線性動力分支時，先進入 mean-rotation MPC 建構。對殼法向 drilling 旋轉，`633–643` 以方向內積判斷是否忽略。
- `gen3dboun.f:687–727`：`MEANROTBS` 建立過程呼叫 `usermpc`，以 `knor(indexk+j)` 取得殼展開節點、以 `nodeact=nk+1` 傳入旋轉值項，最後以 `nodeact=0` 傳入非齊次項。此處表明 **MPC term 的角色不全等於可於 FRD 取得目前變形座標的實體 C3D20 節點**；但 `nk+1`、`nodeact=0` 的輸入是過程參數，**不能**僅靠此推論 Stage 26 所有 unmatched term 的確切角色。
- `resultsforc.c:34–59, 75–134`：利用 `ipompc/nodempc/coefmpc/fmpc` 重分配節點力，並對 `MEANROT` 具有排除非結構 term 的特殊分支。Stage 26 的任一 term 不能被直接解讀成已套用於物理殼支承的獨立力。
- Stage 26 的 exact-head 真實隔離 CCX CI `38114272472`：鋁板 4／8 網格的最後一次呼叫各有 64／128 個 MEANROT MPC、256／512 個 term；其中 192／384 個 term node ID 不在現有 FRD 節點集合。此處的集合差異僅為數值 ID coverage，不證明節點身分，更不是力矩平衡誤差。
- **下一道 admission gate**：要追查各 `usermpc` term 的確切 role，須有 exact 2.21 source-verified term role mapping（包含特殊 node 0、旋轉值及 inhomogeneous terms）和實際儲存座標的獨立 trace；不得把 node ID coincidence 當作 position、也不得為求得 `r×F` 替未知 internal nodes 合成座標。應先完成 source-role discriminator 與反例測試，再考慮 instrumented moment reconstruction。
- 保持 `EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`；沒有獨立旋轉支承反力／MPC 力偶認證，也沒有正式工程容量計算。


## 第二十八階段：`usermpc.f` MEANROT 角色級隔離診斷（候選，2026-10-11）

- **原始碼錨點**：官方來源封存檔 SHA-256 `51d229aee320cf685216d360f7c04f9a57af0148fbe840483a964c86c315da82`；`src/usermpc.f` SHA-256 `97d49518ea8306d0ba9b88c0861c4bfb45487d45836f765d01b9d624548e2fe5`。只在 source hash 和結構錨點符合時，由 CI 隔離複本插樁；不提交第三方 GPL source 或 binary。
- **最小資料契約**：在 `usermpc` 完成 MEANROT 建構且已確立 dependent DOF 後，opt-in `CCX_MPC_ROLES_FILE` 記錄 MPC ID、每個 term 的 node/DOF、角色：regular candidate、axis/angle helper、inhomogeneous helper、以及 `noderef/idirref`。嚴格與 Stage 26 `resultsforc` 最後一次呼叫的 `nodempc` 順序及 node/DOF 對帳；資料缺失、重複、順序變化或缺少 helper 皆 fail closed。
- **工程責任邊界**：這是 **source-internal term role identity**；其中 regular candidate 並非自動得到已驗證的 FRD 三維位置，angle/inhomogeneous helper 也不等同實體受力點。只有通過 exact-head source build、原版與插樁版同 deck 的 NALL/FRD 結果一致、完整 trace mapping 與負向測試，才可宣稱受限角色對帳可重現。不得把 coefficient×fmpc 直接視為獨立支承反力矩。
- Stage 28 與後續仍維持 `EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`，不包含玻璃／鋁板正式工程承載力計算。

### 第二十八階段：第一輪 root cause（受限診斷修正）

CI `38118121617` 的 real `usermpc` trace 顯示原始鋁板 4 網格可有 `ROLE_END,7,8,261,261,1,1`，同一個 internal node `261` 的 DOF 1 是 angle/axis helper、DOF 2 是非齊次 helper。原插樁僅比對 node ID，後一判斷覆蓋前一判斷，導致 `HELPER_ROLE_MULTIPLICITY` 被正確拒絕。現改以 (node ID, DOF) 辨識，並新增同節點不同 DOF 的回歸測試。此修正不放寬物理契約，無論 CI 成功與否均不宣稱獨立旋轉支承力矩。


### 第二十八階段：第二輪 exact-source reconciliation（時間點差異）

Exact-head CI 在完成 node/DOF 角色修正後，已通過原版／插樁版求解數值對照及 Stage 26 term trace，但 `TERM_NODE_DOF_IDENTITY_MISMATCH` 明確指出 **`usermpc` 建立時的 MPC chain 不能被視為最後 `resultsforc` trace 的同一快照**。已觀察建立記錄含 8 個 term 的 MPC；Stage 26 最後一次求解器 trace 的鋁板 4 網格則是 64 MPC、256 term（平均每 MPC 4 term）。兩者不具可直接推論的 term 序列恆等性。

本階段正式改為 **creation-role observation + cross-snapshot difference diagnostic**；保留所有記錄格式、完整性、helper multiplicity、node/DOF 與非有限值等 fail-closed 檢查，但跨快照僅回報 numeric MPC ID overlap 與 exact term sequence coincident count；固定輸出 `creation_to_final_mapping=NOT_ESTABLISHED`。數值 coincident 不代表 term lineage、旋轉 reactions 或物理座標已認證。

後續如要追蹤轉換，需另行對 `gen3dmpc`、`cascade`、`decascade` 及 nonlinear MPC updates 加入必要的版本相符來源／身分對帳，不得以 tolerance、索引相同或憑空插入節點位置補足。


## 第二十九階段：MEANROT MPC 建構／轉換／力輸出責任路徑（來源研究，2026-10-11）

本次使用已驗證 `calculix-ccx_2.21.orig.tar.bz2` SHA-256 `51d229aee320cf685216d360f7c04f9a57af0148fbe840483a964c86c315da82` 的**同一份 exact 2.21 原始碼**，而非 upstream moving branch：

| 責任 owner | SHA-256 與最低充分來源證據 | 可成立的限定結論 |
| --- | --- | --- |
| `src/usermpc.f` | `97d49518ea8306d0ba9b88c0861c4bfb45487d45836f765d01b9d624548e2fe5`；93–126、290–302、483–500 | 建立 mean-rotation auxiliary angle/inhomogeneous terms、計算係數並選定 dependent term；建立時 term identity 不是永久穩定輸出契約 |
| `src/gen3dmpc.f` | `78367fa0950302861e2916d28b3c5ad88fb2b84f8da45f779be4a709ba3255c2`；42–109 | 對原始殼旋轉相關 MPC 進行展開／knot 路徑轉換；此處不是已驗證的最終力反應輸出 |
| `src/cascade.c` | `430911d6f9f91078c0efb826ba103656a504e46ec0d3ce74356b91b4333336c4`；34–57、97–135 | source 明確宣告 decascade／dependent DOF 處理及 user/nonlinear MPC 分類；它是值得進一步測量的中間態 owner，但單靠 source 不能斷定全部 8→4 term 縮減由它造成 |
| `src/results.c` | `d4adfb2b68fdd83d5dc46b9306a712d8dc05aacd326deb2f91cc3d94b22e6d7b`；401–414 | 呼叫 `resultsforc` 時存在 ordinary MPC arrays 和 mortar-transform arrays 的分支；Stage 28 合成非 mortar fixture 未驗證任意 contact/mortar 分支 |
| `src/resultsforc.c` | `d1de9498ac715a7f08da0b7beba3c92c7c2f1030c85c37122d2708f2f480cad0`；34–59、75–134 | 此處的 `nodempc/coefmpc/fmpc` 是進入內力重分配當下的 arrays，不可默認等同 `usermpc` 建立當下的原始 term chain |

### 階段性數值證據與下一道守門

Stage 28 的 PR #52 真實隔離 CCX exact-head run `38118486882` 觀測：鋁板 4 網格在建立快照中有 64 個 MEANROT、384 個 regular terms、64 個 angle terms、64 個 inhomogeneous terms；8 網格則分別為 128／768／128／128。建立與最後一次 `resultsforc` 的 numeric MPC ID 集合可重合，但兩組網格的完整 term-sequence match 都為 **0**；這是**跨階段身分未閉合的證據**，不是物理平衡失敗。

下一個真正必要的研究為記錄 `cascade` 入口／出口及 nonlinear MPC update 的 bounded term identity digest／term count，核對誰改變 `nodempc` 及 `coefmpc`，但不得在沒有來源級連續性之前，用 MPA ID overlap 假定同一 term lineage。此 dossier 只建立候選 owner path；尚未授權任意求解器內部力矩重建，也未取得獨立旋轉拘束反力矩。

**工程狀態維持** `EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`；不做玻璃／鋁板 capacity acceptance。


## 第三十階段：`cascade.c` 入口／出口 MEANROT chain 診斷（candidate，2026-10-11）

延續 Stage 28–29 已確立的 source-role 與 transformed-term snapshots 差異，使用完全相同之 CalculiX 2.21 upstream SHA `51d229aee320cf685216d360f7c04f9a57af0148fbe840483a964c86c315da82`，並對 `cascade.c` exact SHA `430911d6f9f91078c0efb826ba103656a504e46ec0d3ce74356b91b4333336c4` 進行 **隔離、opt-in、instrumentation only** 的診斷版重編譯。

- 在 `cascade` entry／exit 以 `CCX_CASCADE_AUDIT_FILE` 記錄 ordered call ID、MEANROT constraint count、總 term count、最大 term chain 長度；只讀取 entry／exit 的 `ipompc/nodempc/labmpc`，不改 core solver 的 MPC 約束、係數或方程。
- 記錄檔 parser 嚴格要求 call pair 完整、序號有序、範圍受限、至少真實觀測一次 MEANROT。輸出兩端 aggregate count 是否改變；**aggregate change 不足以推定所有 8→4 term 的個別因果／term lineage**，結果固定 `specific_8_to_4_causality=NOT_ESTABLISHED`。
- 沿用 Stage 25–28 的隔離未修改版／診斷版求解比較，要求相同合成鋁板 4／8 網格的 `NALL U/RF`、expanded FRD U/RF 維持現有 text-numeric 比對契約；任何資料缺漏、差異、非有限值或 source SHA 不符 fail closed。
- 不把任何 GPL source／binary 提交到 KB。只有 PR exact-head 真實 CalculiX CI、Repository CI、合併後 main CI 與 canonical read-back 成立，才能稱此限定 cascade 診斷可重現；不代表獨立轉動拘束反力、一般六分量平衡或設計承載力 admission。保持 `EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。


## 第三十一階段：`cascade` 單一 MPC chain 前後變化（候選，2026-10-11）

Stage 30 真實隔離 CCX CI `38118925389` 已觀測鋁板 4／8 網格皆為 25 次 cascade 呼叫，24 次 aggregate MEANROT term 數在入口與出口不同，沒有 MEANROT MPC 個數的變化。Stage 31 針對**每次呼叫每個 numeric MPC ID**新增 bounded `CASCADE_DETAIL_V1` observation，記錄 entry/exit 的 term chain 長度，並要求每筆均與 Stage 30 aggregate count／total／maximum 精確對帳。

- 仍從 verified upstream SHA-256 `51d229aee320cf685216d360f7c04f9a57af0148fbe840483a964c86c315da82` 重新建立隔離編譯；只擴充 GitHub CI working directory 中的 `cascade.c` 診斷 patch，絕不將 GPL source/binary 寫入公開 KB。
- 新增的資料檢查會拒絕重複 numeric ID、缺失 entry/exit、非法 chain 長度及與 aggregate 不一致的資料。輸出明確統計 8→4 的**單次 cascade caller-local numeric MPC ID transition** 數量，不能由此推定 `usermpc` creation 至最終 `resultsforc` 的完整 across-call / cross-stage identity。
- 同一合成鋁板 4／8 網格維持未修改 CCX 與診斷版之 NALL U/RF、expanded FRD U/RF strict text-numeric 一致性。即使觀測到 8→4，仍為 source-internal transformation observation，非 rotational support reaction 或 six-component balance。
- Admission 門：PR exact-head 三組 CI、main CI、remote changed-file read-back。整體維持 `EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。


## 第三十二階段：Stage 28–31 真實證據 reconciliation 與後續 admission boundary（2026-10-11）

本階段只收斂當前已通過 exact-head／main CI 的**受限合成板件研究成果**，不執行新的 solver modification 或宣稱正式工程採用。

| Stage | PR／exact-head CI | 合併後 main SHA | 受限結論 |
| --- | --- | --- | --- |
| 28 | #52；隔離 CCX `38118486882`、Repository／FEA CI SUCCESS | `c71d8967bae61c6d5eb752c7d59a782f61fbf195` | 建立快照鋁板 n=4 為 64 MEANROT、384 regular＋64 angle＋64 inhomogeneous terms；n=8 為 128、768＋128＋128。轉換後的完整 term 序列 match 為 0：`creation_to_final_mapping=NOT_ESTABLISHED` |
| 29 | #53；Repo CI `38118720549` SUCCESS | `fd7991a838ba0431479bd4a4d2de67e8ea8367fc` | 精確來源責任路徑為 `usermpc` → `gen3dmpc`／`cascade`／其他處理 → `resultsforc`；仍未完整辨識每條 term lineage |
| 30 | #54；隔離 CCX `38118925389`、Repository／FEA CI SUCCESS | `41808f2092337540f55b1ec055a9e65e0c57cb84` | 兩個 synthetic 鋁板網格均為 25 次 cascade call，24 次的 MEANROT aggregate term 數量改變，MPC count 不變 |
| 31 | #55；隔離 CCX `38119261430`、Repository／FEA CI SUCCESS | `7e4901ff28d5591cb85f4b2b0fc2b9bcbcda5be2` | n=4 累計 1536 次、n=8 累計 3072 次 **per-call, per-numeric-MPC-ID** 8→4 term-count transitions；不是獨立 MPC 個數，也不代表跨 stage identity |
 
Stage 31 main CI `38119404136` SUCCESS；以上合併 commit 與執行紀錄皆按已驗證 remote evidence 記錄。原版與最小插樁版於相同合成板件的 NALL U/RF 及 expanded FRD U/RF 維持現有 text-numeric 精度下完全一致，不能擴張為一般 shell engineering acceptance。

**目前能證明的最高範圍**：對這些固定合成模型，MEANROT helper roles 與 cascade entry/exit 的 MPC chain 縮減，可在 exact-source 隔離 GPL 診斷版實際觀測。尚無獨立旋轉拘束反力矩、完整 nonlinear MPC term identity lineage、含 node 力偶的實際六分量 global equilibrium acceptance。下一個可驗證工程問題需重新建立 per-term source identity 穿越 MPC transformation 的契約，並在所有原始／展開／輔助節點的真實作用位置取得獨立數據；目前不宜直接新增工程容量或 six-component PASS gate。

**維持** `EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。此 dossier 為唯一研究證據 owner；外部 GPL 2.21 原始碼及 binary 不納入 public repository。


## 第三十三階段：固定合成板件之受限 execution adapter（候選，2026-10-11）

- **目標**：不把 Stage 1–32 的 MPC 研究誤視為通用工程求解器完成。新增可一次呼叫之 `run_synthetic_panel.py`，只接受 Repo canonical `generate.py` 產生的 glass／aluminum、n=4／8／16、large-load 固定合成 S8R P1 NLGEOM 算例；禁止未知 deck、任意 `*INCLUDE`、非預期材料與專案輸入。
- **執行關卡**：預設 opt-out；只有 `--execute`、可信外部 CCX executable、既有且空白的操作員控制資料夾成立才產生 fixture／執行，無 sandbox。回傳僅為 `SYNTHETIC_BENCHMARK_EVIDENCE_PASS` 或拒絕，不是正式 engineering PASS。
- **數值證據**：要求求解器 process zero exit、完整 .sta 最後步驟 time=1、.dat／.frd、Stage 19 三向平移力平衡、Stage 24 力矩幾何分解均通過；缺少資料、非有限值、超過固定輸出大小、超時、數值不一致都拒絕。CI 應跑 mock／fail-closed test 及真實獨立 `glass n=4` smoke（不偷用原本已執行的結果）。
- **工程邊界**：這不是任意幾何模型 execution adapter；不提供獨立旋轉反力矩、六分量 global equilibrium、材料非線性、接觸／屈曲／缺陷或 ASTM E1300／ADM capacity。保持 `EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。


## 第三十五階段：受限 execution adapter 輸入／求解器／輸出身分鏈（候選，2026-10-11）

Stage 33 六組真實合成 CCX adapter smoke 在 PR #57 成功、合併後 main CI 亦成功。此階段限定原六組合成模型，補上 **SHA-256 provenance**，不新增任意 input deck 入口或任何 engineering approval。

- 在 solver 執行前檢查非空、bounded deck 與可信操作員提供的本機外部 CCX executable，取得 SHA-256；執行後先確認 deck 及 executable 內容 SHA 未改變，再接續既有 output completeness、final `*.sta`、Stage 19／24 審核。
- 只有 bounded numeric checks 全部成立時才在 `artifact_provenance` 輸出 deck、solver、DAT、FRD、STA 之 SHA-256。輸出檔 identity 為此一 run 觀測到的 file bytes，不等同跨 runtime 或 compiler 版本的通用數值等價，也不保證 solver executable 沒有執行外部副作用；操作員仍須信任本機工具。
- 新增遺失／超大檔案 SHA 拒絕及運行期間 solver bytes 改變等負向測試。不得將測試建立之 fake solver 當真正 runtime evidence；本階段完成門仍為 PR exact-head 真實 CCX 6-case smoke、Repo CI、合併後 main CI 與 canonical read-back。
- 維持 `EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。輸入／求解器雜湊是追溯而非旋轉反力矩、工程失效準則、ASTM E1300 或 ADM 容量的 admission。


## 第三十六階段：跨獨立工作目錄的合成求解重播契約（候選，2026-10-11）

延續 Stage 33–35 固定六組 synthetic S8R NLGEOM P1 adapter，以及已驗證之 deck／solver／DAT／FRD／STA SHA-256 evidence，本階段只新增「同一受限模型在不同**空白工作目錄**執行兩次」的可觀測重播對照。

- 單次 CI 執行固定六組 glass／aluminum × n=4／8／16，保留每組獨立 JSON result於 runner ephemeral 目錄，而非寫回 execution workspace；對 glass n=4、aluminum n=4 再以**新空白工作目錄**重新執行實際 CCX，要求同一 deck SHA、同一 solver binary SHA、相同模型語意、受限三向平移與幾何力矩數值結果完全一致。
- 重播比較工具 `check_synthetic_replay.py` 必須拒絕非 `SYNTHETIC_BENCHMARK_EVIDENCE_PASS`、缺少 artifact provenance、不合法 SHA、非有限 JSON、擴張 engineering admission、不同 solver/deck 及數值 mismatch。DAT／FRD／STA **byte SHA 不要求相同**（可包含與作業環境相關文字），不能拿哈希不相同作為物理結果不同的證明。
- 這是同一 CI runner／solver 版本上「跨兩個工作目錄的 deterministic repeatability」；不宣稱跨作業系統、compiler、CPU、硬體或一般模型求解一致，也不提供獨立旋轉反力／完整 MPC lineage。
- 完成需 PR exact-head 六組真實 CCX、兩組獨立 replay、Repository CI、合併後 main CI 與 remote read-back；保持 `EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。


## 第三十七階段：可輸入鋁板參數之受限非線性研究模型（候選，2026-10-11）

使用者已選擇鋁板為下一個模型；此階段從 Stage 36 固定 synthetic adapter 衍生出 **explicit research-input only** 的 S8R 矩形四邊固定板介面，**不是**正式鋁板工程設計器。

- 新的 `aluminum_research_input.py` 僅接受固定鍵名的 JSON，單位 `N-mm-MPa`，矩形寬／高、厚度、由呼叫者提供之彈性模數、Poisson ratio、均布正向 P1 pressure、4／8／16 mesh、`four_edges_clamped` 支承，以及非空 material provenance label；拒絕額外欄位、重複欄位、非有限值、超出 bounded numerical research envelope 的輸入。
- 不將 JSON 直接傳給 CCX；只透過既有 `generate.py` 產生受限模型。新入口 `run_aluminum_research.py` 預設不執行；只在 caller 明確 opt-in、空白 working directory、可信外部 CCX 下呼叫原有 process wrapper。須取得 final-step `.sta`、NALL U/RF、expanded FRD、Stage 19 bounded translations 與 Stage 24 geometric partition，並記錄 deck／solver／DAT／FRD／STA SHA-256。
- 限定參數範圍是 **testing envelope，不是建築法規、ADM 或物理合理性認證**。即使 `ALUMINUM_PARAMETRIC_RESEARCH_EVIDENCE_PASS`，也僅表示該算例通過受限 numerical checks。沒有材料牌號／temper／焊接熱影響、失效準則、屈曲、連接或獨立旋轉拘束反力矩。
- 最低驗證為 JSON 負向測試、與既有固定參數一致的 real CCX smoke、PR exact-head CI、main CI 與 canonical remote read-back。**不開放任意外部 deck 或宣稱 ADM member capacity**。

工程狀態維持 `EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。


## 第三十八階段：不同鋁板參數之真實求解驗證（候選，2026-10-11）

Stage 37 已完成與舊合成固定案例相同之參數下的真實 CCX smoke。此階段新增 **120×80×2.5 mm、E=70000 MPa、Poisson ratio=0.32、P1 pressure=0.3 N/mm²、8 分割、四邊固定** 的明確合成反例，要求新的 `run_aluminum_research.py` 真實執行 `ALUMINUM_PARAMETRIC_RESEARCH_EVIDENCE_PASS`。另外從產出的 deck 獨立解析原始節點外接矩形、元素數目與壓力，與 JSON 確認一致；此前的 100×100×2 mm 單組對照保留。

這仍是 bounded elastic S8R numerical method research，非正式鋁板尺寸設計、非 ADM 強度容量，也不保證任意 parameter combinations 的求解或物理驗收。必須實際 CI PASS 才能將本階段標為受限通過。工程狀態維持 `EVIDENCE GATED` 與 `GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。


## 第四十階段：鋁板小撓度獨立 Ritz 近似與三層網格研究（候選，2026-10-11）

兩組完全合成低荷載矩形鋁板：100×100×3 mm、E=69000 MPa、ν=0.33、p=0.0001 N/mm²；120×80×2.5 mm、E=70000 MPa、ν=0.32、p=0.0002 N/mm²。兩組均為四邊固定、線彈性、S8R NLGEOM P1，分別採 4／8／16 網格、六次 opt-in 真實 CalculiX 2.21 求解。

獨立研究比較使用 Kirchhoff 小撓度板之**一項 Rayleigh–Ritz 近似**：w=W(1−ξ²)²(1−η²)²，ξ=2x/a、η=2y/b；由 D=Et³/[12(1−ν²)]、彎曲能量與外力位能，利用解析多項式積分取得 W。此為近似方法而非精確解析真值。比對需輸入、deck 幾何、材料、網格、面壓、來源 SHA 與真實執行一致，16 網格與 Ritz 差異不大於 20%，並具 |w16−w8| < |w8−w4| 的改善及 max|w| < 0.05t。20% 與 5% 僅為 bounded research-screening threshold，並非工程允許誤差、精確網格收斂或 ADM 設計依據。

只有 PR exact-head 真實 CCX 六案例、Repository CI、合併後 main CI、remote read-back 均成功才能稱此研究階段通過。維持 `EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`，不建立正式鋁板 strength/capacity、轉動反力或任意支承 admission。


## 第四十一階段：鋁板求解結果受限研究摘要（候選，2026-10-11）

在既有 `ALUMINUM_PARAMETRIC_RESEARCH_EVIDENCE_PASS` 之後，新增 `research_observations`，僅整理 original S8R NALL 節點最後增量的三向平移位移（mm）、中心節點位移、節點最大合位移、節點最大面外位移及節點 ID。最大值僅限**原始殼節點**，不是殼元素連續場或 expanded solid 的全域極值。資料來源為既有 CCX DAT final NALL U；不另外虛構應力或應變。另沿用 Stage 19 通過之 follower-pressure/internals 推導的三向平移支承合力（N）及 residual，明示屬**重建**而非獨立測量；輸出與已有稽核結果對帳。

對輸入、deck 幾何／網格／材料／面壓及 NALL 節點 coverage 做 fail-closed 比對。`stress`、`strain`、`rotational_support_reaction` 固定為 `NOT_OBSERVED`；`aluminum_design_manual_capacity=NOT_COMPUTED`、`engineering_acceptance=NOT_ADMITTED`。既有 SHA-256 provenance 和 opt-in runtime 邊界不變。完成需 PR exact-head Repo CI、實際 CalculiX CI、merge 後 main CI 與 canonical read-back；本摘要沒有提升通用六分量平衡或工程 capacity admission。


## 第四十二階段：鋁板 expanded-node 應力與應變觀測（候選，2026-10-11）

僅在受限 `run_aluminum_research.py` 參數模型增加 CalculiX `*EL FILE,OUTPUT=3D` 的 `S,E`；固定合成 benchmark deck 不變。新增 FRD `STRESS` 與 `TOSTRAIN` 六分量解析，要求 final time 1.0、明確六分量標頭／次序、無缺漏／重複／非有限值、與既有 C3D20 expanded 節點座標及位移完全一致的節點覆蓋。於 Stage 41 `research_observations` 下附加各 tensor 最大絕對分量、對應擴展節點 ID、來源與單位。

**數值意義**：這是 CalculiX 3D 展開元素產生的節點外插／平均觀測值，不是未經平均的 Gauss point 值、殼中面表面極值或任何屈服／失效準則。未提供獨立應力／應變數值 oracle，故 `independent_numerical_oracle=NOT_ESTABLISHED`，`integration_point_extreme=NOT_OBSERVED`，不計算 von Mises 合格性或 ADM capacity。必須 PR exact-head Repository 與真實 CCX CI PASS、merge 後 main CI、canonical read-back 才可聲稱本受限觀測 adapter 完成。保持 `EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。


## 第四十三階段：鋁板低壓下張量之獨立壓力縮放檢核（候選，2026-10-11）

僅針對同一組 100×100×3 mm、E=69000 MPa、ν=0.33、n=16、四邊固定 S8R 模型，分別以 0.0001／0.0002 N/mm² 面壓執行**兩次真實、獨立** CCX。基於小撓度等向線彈性近似，固定模型對均布壓力之 U、S、E 場一階成比例，是不同於 parser 自身的物理縮放檢核；在所有已解析原始殼節點 U 及 expanded-node 六分量 S／E 上逐分量比較，不只比峰值。確認相同模型 geometry/topology、參數輸入及 DAT／FRD／deck SHA provenance，非有限／缺節點／缺張量／場振幅太小均 fail closed。研究門檻設 4% 最大分量相對於該場最大幅值的 scaled residual，並要求面外位移低於板厚 5%；這些容差**只是合成數值研究的 screening**，不是材料允許誤差、一般精度保證或設計規範。

壓力成比例屬數值一致性檢查，不等於逐點真實應力／應變解析值、積分點峰值或獨立本構應力真值已建立；工程狀態保持 `EVIDENCE GATED`／`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。完成需 PR exact-head Repo／real CCX CI 與合併後 main CI／read-back。


## 第四十四階段：低荷載法向應力／應變本構交叉驗證（候選，2026-10-11）

延續 Stage 43 受限的同一 100×100×3 mm、E=69000 MPa、ν=0.33、16 網格低荷載 synthetic 資料，採用獨立線彈性等向材料 compliance 關係 εᵢ=(σᵢ−ν(σⱼ+σₖ))/E，在 CCX 真實 FRD expanded-node 的**全部法向三分量**檢查，並以 E×應變殘差（MPa）相對於最大觀測法向應力作 bounded max-error screening。研究門檻暫設 3%；缺資料、非有限值、節點覆蓋不相等、訊號太小都 fail closed。此檢查僅可驗證材料本構關係與 solver 輸出彼此相容，不代表幾何應力場絕對數值正確；shear convention 尚未獨立解決，故**不檢查剪應力/剪應變**。

Stage 43 已通過 PR #68 真實 independent pressure scaling 與 main CI；Stage 44 必須另取得 PR exact-head 真實 CCX、Repository CI、合併後 main CI 與 canonical read-back。僅限定線彈性低荷載 synthetic；保持 `EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`，不主張任何工程強度 admission。

## 第四十六階段：3003-H14／3004-H12／3004-O 帷幕鋁板研究材料來源（2026-10-11）

優先研究 alloy–temper 為 **3003-H14、3004-H12 與 3004-O**。此為研究選題優先順序，**不是**宣稱全體台灣或全球帷幕牆的使用率，也不等於專案產品保證。舊 5754-H42／5005A-H14 案例僅作比較。

### 供應商公開機械性質（研究線索；非設計強度）

| 合金／temper | 公開板厚範圍 | Rm（MPa） | Rp0.2（MPa） | 來源 |
| --- | --- | --- | --- | --- |
| 3003-H14 | 1.21 mm 以上至 6.30 mm | 140–180 | 最低 115 | BlueScope Distribution，3003 sheet 資料 |
| 3004-H12 | 大於 0.20 mm 至 6.00 mm | 190–240 | 最低 155 | Southwest Aluminum，3004 sheet 資料 |
| 3004-O（供應商與 H111 合併列示） | 大於 0.20 mm 至 12.50 mm（表中另列較厚範圍） | 155–200 | 最低 60 | Southwest Aluminum 與 tk accelis（原 thyssenkrupp Materials Processing Europe）的 EN AW-3004 供應商資料 |

- [BlueScope Distribution — Aluminium 3003 Data Sheet](https://www.bluescopedistribution.com.au/products/aluminium/aluminium-3003-data-sheet/)：3003-H14 之板厚、Rm、0.2% yield、成形與表面處理資訊。
- [Southwest Aluminum — 3004 Aluminum Sheet](https://www.southwest-aluminum.com/aluminum-plate/3004-aluminum-sheet.html)：3004-H12 之板厚、Rm、0.2% yield、厚度分區延伸率；該供應商提及幕牆板應用。
- [tk accelis Processing Europe — EN AW-3004 / Al Mn1Mg1](https://www.thyssenkrupp-materials-processing-europe.com/en/aluminum/alloy-group-3000-or-en-aw-3003-or-en-aw-3004-or-en-aw-3005a-or-en-aw-3103-a-or-en-aw-3105a/en-aw-3004-or-al-mn1mg1)：公開供應商表將 O 與 H111 同列；除 Rm／Rp0.2 外，列示依板厚而變的伸長率與建議彎曲半徑。**不得將兩種實際 temper 或加工狀態無條件視為完全相同。**
- [ASTM 官方 B209/B209M-21a](https://store.astm.org/b0209_b0209m-21a.html)：**標準範圍與版本路由**，不是可自由複製的標準全文或免費材料／設計公式。

這些表格的供應商、地域及來源層級不同，未獨立確認相同法規／標準、試驗方向、材料批次或製造與加工後狀態；不可逕以最低 Rp0.2 比較判定**任一實際鋁板的設計強度或耐久性**。必須核對供應商產品規格、mill certificate、板厚、冷作成形後 temper、軋延方向與適用設計依據。**供應商的 Rp0.2 不是 ADM allowable strength、局部挫屈、扣件或板件極限承載力。**

3004-O 為 annealed／退火狀態，通常供較大成形變形用途；相對於 3004-H12，兩者的屈服強度、延性及成形後材料狀態必須分開確認，不能把冷作／退火前後性能視為不變；此處僅根據已列的供應商產品資訊，不建立塑性曲線或加工折減。

### 台灣在地供應來源：中鋼鋁業（2026-10-11 查核）

帷幕牆工程實務反映，台灣常由**中鋼鋁業股份有限公司（C.S. Aluminium Corporation）**供應 3003-H14、3004-H12、3004-O；此為使用者提供的 `FIELD_OBSERVATION`，**不是**可驗證之產業市占率排行，也不據此推定三種質別皆為目前標準公開接單品。

| 研究目標質別 | 中鋁公開一手來源之證據 | 產品／用途適用界線 |
| --- | --- | --- |
| 3003-H14 | 官方「鋁捲、鋁片／帷幕牆」專頁：厚度 1.5–3.5 mm、寬 800–1550 mm、長 1000–6100 mm；抗拉 135–175 MPa、降伏最低 120 MPa、延伸率最低 5% | 廠商對**該頁帷幕牆產品**之公開規格；未指向任何特定批次、出廠證明或設計容許強度 |
| 3004-H12 | 中鋁官方公開報導已提及低碳帷幕牆用 3004H12 的推廣方向；但本次查核範圍內的**公開網頁尚未取得其完整、依厚度分級的保證機械性質表** | `PUBLIC PRODUCT MENTION CONFIRMED / PRODUCT-GRADE PROPERTY TABLE NOT FOUND IN CHECKED PUBLIC SCOPE`；不可將 O、一般 3004 或其他供應商的數值自動套入 H12，正式採購與設計仍需產品規格書／批次 MTC |
| 3004-O | 中鋁 2025-02-20 官方公告 **CAC 3004-O (RC60)** 低碳鋁材供外牆／帷幕牆使用，該公告產品實測敘述：抗拉 177 MPa、降伏 149 MPa、延伸率 19%；另在一般 3004 鋁片接單 O 質別表有列示 | 數值限 `CAC 3004-O (RC60)` 的官方公告，**不可擴張為所有 3004-O／O-H111／任何厚度或批次之通用材料值**；公告的「降伏強度」未因此自動被賦予任何特定塑性曲線定義 |

可直接核對的**製造商原始連結**（不重製官網表格全文）：

- [中鋼鋁業｜鋁捲、鋁片／帷幕牆產品規格](https://www.csalu.com.tw/Product1-03-5.html)：3003-H14 厚度／尺寸與抗拉、降伏、延伸率。
- [中鋼鋁業｜可接單規格與質別](https://www.csalu.com.tw/Product5.html)：3003／3004 alloy 與部分質別的公開產品路由；不得由一般 alloy 路由補猜 H12 的厚度分級保證值。
- [中鋼鋁業｜2023-12-07 年度公開報導：低碳 3004H12 帷幕材料](https://www.csalu.com.tw/NEWS_CONTENT.aspx?docsid=9CEA42944CEAF050)：僅支持中鋁公開提及 3004H12 推廣方向；**不提供**可直接轉成 FEA 材料卡的完整厚度分級性質或塑性曲線。
- [中鋼鋁業｜2025-02-20 低碳 CAC 3004-O (RC60) 發表新聞稿](https://www.csalu.com.tw/NEWS_CONTENT.aspx?docsid=61C8957482BE2B4C)：公告特定產品性能與帷幕應用，非單軸全應變曲線或設計手冊。

**來源優先路由更新**：台灣帷幕用料的優先查核證據改由中鋁當前產品型錄／正式規格書／該批次出廠材質證明建立；先前 BlueScope、Southwest Aluminum、tk accelis 只保留為**跨廠商／不同市場的研究比較**，不得覆寫實際中鋁供料產品性能。尤其中鋁 3004-O RC60 公告降伏值與其他供應商一般 3004-O 最低值不同，屬**不同產品與證據語境**，不能無適用條件直接斷言「某資料錯誤」、也不能用兩個公告數值內插、外插生成 `*PLASTIC` 本構曲線。

**公開資料與非公開資料分流**：廠商公開新聞稿所提產品存在／推廣方向、一般牌號規格、特定質別的產品保證值、單次試驗觀測、製程變更後試驗，以及現行標準條款，必須各自保留 evidence type 與適用條件。來源為客戶版、專有或授權未確認的技術資料，除非取得可公開引用的正式版本與權利確認，**不得寫入公開 KB 的私有檔名、測試頁面、實測數字或檔案本體**。其工程意義可留在獨立私人研究工作檔；不得以多個簡報版次膨脹成多次獨立驗證。公共材料卡仍禁止由降伏／抗拉／伸長率三項推導完整 `*PLASTIC` hardening，容量維持 `NOT_ADMITTED`。

本補充僅更新 reference provenance，未建立全台主要供應商市占率統計、合約供貨身分、實測 engineering material card 或正式 capacity admission。下一步若取得中鋁該產品**材料證明、厚度／供貨狀態、拉伸試驗完整應力–應變資料與授權條件**，才另開受限材料本構驗證。

現有參數化 FEA 的 E／ν／厚度／壓力與材料來源均維持**明確輸入**。合金牌號不可自行推出 E、ν、塑性曲線、降伏或 capacity。Stage 42–44 FRD 的 S／E 張量是 expanded-node 外插／平均觀測，Hooke／壓力比例一致性不代表真實材料強度驗證，故本階段**不改動 solver、計算器或輸入契約**。

下一個 admission trigger：製造商或可靠產品的原始性能與批次資料、合法可使用的標準設計條款、材料／板件失效模型、獨立數值或實驗驗證。欠缺時維持 `MATERIAL_CAPACITY_NOT_ADMITTED`、`EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。

## 第四十七階段：三種鋁板材料非線性證據適用性與資料需求（研究，2026-10-11）

此階段延續 Stage 46 的 **3003-H14、3004-H12、3004-O** 材料優先序，研究哪些公開來源能支持日後建立 *實測* 非線性材料模型。**不是啟用 CalculiX `*PLASTIC`、設計強度或新 FEA admission。** 只使用公開原始論文著錄及摘要／供應商已有公開型錄；不轉錄受版權保護全文、圖像或曲線數據。

### 匹配性／獨立 evidence family

| 目標質別 | 此次實際核對的 evidence | 已能支持 | 尚不能支持 |
| --- | --- | --- | --- |
| 3003-H14 | Zampaloni 等（2003），*Experimental and numerical study of stamp hydroforming of sheet metals*，International Journal of Mechanical Sciences，DOI 10.1016/j.ijmecsci.2003.11.006（原始出版社頁） | 確有相同 alloy–temper 的液壓成形實驗與各向同性／各向異性模型比較 | 將液壓成形的接觸／支承、加工狀態或其參數直接挪用為本 KB 四邊固定均布壓力板、批次指定材料或普遍失效準則 |
| 3004-H12 | Stage 46 Southwest Aluminum 3004 sheet 公開供應商強度／板厚表 | alloy–temper 名稱與供應商所列抗拉／Rp0.2 類別之研究線索 | 完整單軸 true-stress–equivalent-plastic-strain hardening table、各向異性或加工後可靠屬性；**在本次有限查證來源內未找到直接相同質別的可用原始完整曲線** |
| 3004-O | Katsuta 等（1985），*Forming limit curves of 3003 and 3004 alloy sheets*，DOI 10.2464/jilm.35.696；Kaneko 等（1985），*Effects of tempering on the formability of 3003 and 3004 aluminum sheets*，DOI 10.2464/jilm.35.12（均為原始學術期刊）；Stage 46 tk accelis O/H111 型錄 | 確有 3004-O 的實驗成形極限／成形性研究與退火質別供應商資訊 | 將 forming limit curve（FLC/FLD）誤作材料 hardening curve；將 O/H111 合併型錄視為**完全同一**加工狀態；直接推定彎折後、任意厚度或任何構件的失效容量 |

**兩篇 1985 年論文是不同研究問題的同刊來源，不能因材料牌號相同便視為兩份已交叉驗證的相同 stress–strain 數值。** 1985 年 FLC 研究另外涵蓋 3003-O、3003-H24、3004-H24，**H24 不得替換 H12**。Zampaloni 等研究的加工設備、支承與接觸條件也不同於目前的 synthetic S8R clamped P1 板件。

原始頁面（保留永久 DOI，不下載／複製受限論文全文）：

- [Zampaloni et al. 2003，原始出版社](https://doi.org/10.1016/j.ijmecsci.2003.11.006)。
- [Katsuta et al. 1985，J-STAGE](https://doi.org/10.2464/jilm.35.696)。
- [Kaneko et al. 1985，J-STAGE](https://doi.org/10.2464/jilm.35.12)。
- [tk accelis 3004 供應商頁面](https://www.thyssenkrupp-materials-processing-europe.com/en/aluminum/alloy-group-3000-or-en-aw-3003-or-en-aw-3004-or-en-aw-3005a-or-en-aw-3103-a-or-en-aw-3105a/en-aw-3004-or-al-mn1mg1)。

### 後續材料本構 admission gate

真正增加 `*PLASTIC` 前，需逐一確認：① 具來源授權的材料試驗資料，匹配 alloy、temper、板厚、供應商／batch 與製造後狀態；② 拉伸方向（0°／45°／90°）及是否需處理 rolling anisotropy；③ 溫度、應變率與原始工程應力–應變曲線；④ 由實測資料嚴格判定均勻延伸區與頸縮前的轉換範圍，不能由屈服／抗拉兩點猜整條曲線；⑤ 若選用 CCX 等向硬化，需有相容、單調且具物理量定義的 von Mises true stress–equivalent plastic strain 表及首屈服零塑性應變，並先用獨立單元素本構實驗／numerical reference 核對；⑥ 成形後狀態、板件與支承／連接／局部挫屈、完整 engineering design basis 再分別 admission。

目前可讀到的 CalculiX 2.18 `*PLASTIC` 文件描述輸入格式，但它**只能作舊版方法路由**；真正針對 CalculiX 2.21 實作必須從已核對版本的 source/manual 與真實 CCX regression 再驗證。不能把任何 peer-reviewed FLC、供應商最小 Rp0.2、單獨材料 E／ν，或跨質別 hardening coefficients，當成可直接產生真實 deck 的材料模型。

**目前結果：** 已找到相關學術材料研究線索，但三種目標 alloy–temper 都維持 `MATERIAL_PLASTICITY_NOT_ADMITTED` 與 `MATERIAL_CAPACITY_NOT_ADMITTED`；已存在的線彈性 S8R synthetic 模型及其 Stage 40–44 數值檢查不受本文件變更影響。整體仍為 `EVIDENCE GATED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。

## 第四十九至五十階段：合成塑性本構及部分卸載路徑之真實 CI 驗證（2026-10-12）

**Stage 49（PR #80）**：新增一個明確合成、單元素 C3D8、位移控制單軸的雙線性等向硬化算例，`*ELASTIC`（研究值 E=70000 MPa、ν=0.30）與 `*PLASTIC`（合成初屈服 100 MPa、硬化斜率 H=1000 MPa）由求解器獨立執行低於及高於屈服的兩種位移。檢查獨立單軸 oracle 的 σ 與等效塑性應變、FRD stress/PE 欄位、節點覆蓋及 STA 收斂。官方 CalculiX 2.21 真實輸出中 `*EL FILE PEEQ` 對應 FRD `-4 PE`／`-5 PE` 描述；先前 PR 測試曾因誤期待 PEEQ 欄位名稱或換行 assertion 而失敗，修復後 exact-head CI 與 merged-main Repository CI 成功。完成合併 commit `aa21fd2605e5db689684ba9d4f4e53ae2f4276e8`。

**Stage 50（PR #81）**：以相同合成材料與幾何額外建立兩個連續 CCX `*STEP`，先載入塑性峰值（軸向 ε=0.004），再部分卸載到 ε=0.003；解析 FRD 最終 step time 1 與 2。獨立 oracle 依 `σ_unload=σ_peak−E×(ε_peak−ε_unload)` 與 `PEEQ_unload=PEEQ_peak` 核對實際求解，並檢查載入步末已形成正確塑性起始狀態；本地單元測試 8/8 PASS，PR exact-head Repository CI／real CCX CI 與合併後 main CI 均成功。合併 commit `780c6cf5402393a041daf2ec39dcffdc66337966`。

**研究範圍嚴格限制**：這些 E、ν、σ_y、H、位移與單元素尺寸均是合成測試，不是 3003-H14／3004-H12／3004-O 的製造商資料、合格材料卡、軋延各向異性或真實構件支承；FRD 為節點外插／平均觀測，不是獨立積分點量測。Stage 49–50 僅說明 CCX 本構演算法在選定 *單元素＋指定載入路徑* 下與獨立基準吻合，仍維持 `MATERIAL_PLASTICITY_NOT_ADMITTED`、`MATERIAL_CAPACITY_NOT_ADMITTED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。

後續若要提升真實材料與構件 admission，必須有中鋁適用產品、厚度、加工後狀態及合法可使用的完整拉伸本構曲線，並依新支承、幾何、塑性演化及失效模型分別驗證；不能用本次合成雙線性參數替代產品實測資料。

## 第五十二階段：私人中鋁硬化表結構預檢及已驗證邊界（2026-10-12）

**Stage 52／PR #83**（合併 commit `0000e450a1fe573532c99a524fc537ff12463899`）新增 `tests/fea_benchmark/envelope_panels/validate_private_hardening.py`，供操作者在公開 Repository 之外，以明確 opt-in 的本機私有 JSON 對 `3003-H14`、`3004-H12`、`3004-O` 的 true von Mises stress–equivalent plastic strain **點列結構**執行唯讀預檢；相關介面與限制由 `scripts/engineering_calc/README.md` 說明。程式檢查固定欄位、製造商宣告、單位、材料／供貨狀態、有限值、塑性應變順序與應力非遞減；僅回傳結構狀態、點數與 `NOT_ADMITTED` 界線，不輸出私人試驗值、產品代號或產生 `*PLASTIC` 求解輸入。

**完成證據**：PR exact-head `51968f552a3b9c4253916b96ae22f6d879e2dbfe` 的 Repository CI `38197370523` 與 CalculiX workflow `38197370568` 均 SUCCESS；merged-main `0000e450a1fe573532c99a524fc537ff12463899` 的 Repository CI `38197549052` SUCCESS；已以該 SHA 的 GitHub canonical source read-back 核對 validator、合成測試與 README 範圍。此 evidence **只支持 Stage 52 的結構 validator／既有 synthetic CI scope**，不代表已輸入真實中鋁完整硬化曲線，亦非本批次試驗、真實鋁板塑性路徑或板件容量之驗證。

先前整理的私有廠商規格／試驗摘要並不等同完整的 `points=[[true_stress_mpa, equivalent_plastic_strain], …]` 資料；取得真正符合 alloy、temper、產品板厚、拉伸方向、批次、製造／加工狀態及來源權利的完整原始曲線後，仍須獨立檢查單軸轉換與 CCX 2.21 本構行為，才可另行考慮下階段 admission。現階段維持 `MATERIAL_PLASTICITY_NOT_ADMITTED`、`MATERIAL_CAPACITY_NOT_ADMITTED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED` 與 `EVIDENCE GATED`。

## 第五十四階段：獨立三項式 Ritz 彎曲場篩選（2026-10-12）

**Stage 54／PR #86**（merge SHA `39e81065f3971b02c34632deedc66faae21685f1`）對現有 synthetic 低荷載、四邊固定矩形、線彈性 S8R NLGEOM P1 鋁板新增獨立三項式 Kirchhoff–Rayleigh–Ritz 多項式近似：以解析多項式積分及 3×3 線性方程取得中心撓度和中心上下表面彎曲 SXX／SYY，與真實 CCX 2.21 expanded C3D20 FRD 的外插／平均應力和原始 S8R 中心位移比較。並核對中心上下表面觀測覆蓋、非彎曲（membrane）殘量及數值有限性。使用的 synthetic 低荷載 square case 不代表中鋁 3003-H14／3004-H12／3004-O 真實材料性質。

**真實驗證 evidence**：初次 PR head `9854ae348b014d8efe303ab4447dfba076ce6279` 的 Repository CI SUCCESS，但 CCX workflow `38208642361` FAIL，原因是新增單元測試在 membrane 反例中錯誤巢狀使用兩層 `assertRaisesRegex`，內層吞掉預期例外，使外層錯誤判定沒有例外；沒有改動物理模型或容差。修正後 exact PR head `5ada81f7c9e1558ad0c1f5a168a9abfe5a223da4` 的 Repository CI `38208877299` 與真實 CalculiX CI `38208877300` 均 SUCCESS，合併後 main Repository CI `38209073600` SUCCESS；GitHub canonical merged-main source／test／workflow read-back 已確認。

**限制與不可外推**：三項式 Ritz 與 CCX 的 expanded-node stress 均有各自方法誤差；目前篩選門檻撓度 12%、彎曲應力 30%、非彎曲殘量 18% 只是這組 synthetic fixture 的 bounded research thresholds，不是通用精度聲明、精確應力解、法規允許誤差或 ADM 容量值。沒有觀測 Gauss-point 極值、真實折板／加勁肋／支承／扣件／局部挫屈或獨立旋轉反力矩；持續維持 `EVIDENCE GATED`、`MATERIAL_CAPACITY_NOT_ADMITTED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。下一步如要提高獨立性，需獨立解析或試驗基準、不同板形與 mesh variation／shell formulation 的適用性評估，不能用本次單組 PASS 宣稱可直接設計鋁板。

## 第五十五階段：兩種板形與三層網格之中心彎曲應力研究（2026-10-12）

**Stage 55／PR #88**（merged-main SHA `2c38211b79062e9407019181327f36ddc404edb4`）沿用 Stage 40 已存在的六組真實 CalculiX 2.21 合成線彈性、四邊固定 S8R NLGEOM P1 算例：100×100×3 mm 與 120×80×2.5 mm，各 4／8／16 網格。 `check_aluminum_ritz_mesh_stress.py` 核對輸入／報告、deck／DAT／FRD SHA-256、expanded C3D20 觀測覆蓋及兩方向中心上下表面應力差，並檢查各板形各方向 4→8 與 8→16 應力變化是否縮小；**只在 n=16 適用 Stage 54 三項式 Kirchhoff–Ritz 中心應力及撓度既有 screening**，粗網格只擷取觀測，不偽稱已達細網格門檻。

初次 PR head `fd7c0e72052140e246c2c7bd31137d6b086c6a73` 的 Repository CI `38211473578` SUCCESS、真實 CCX CI `38211473476` FAIL：直接將 n=16 的 `RITZ_CENTER_DEFLECTION_DISAGREEMENT` 門檻套用到粗網格，屬測試適用性錯誤而非已證實 solver 異常。修正後 PR head `dc42a9999c485b97ef99c37d1f3fd508faaa0a93` 的 Repository CI `38211746401` 與真實 CCX CI `38211746387` 均 SUCCESS；merged-main Repository CI `38211906983` SUCCESS。保留原 Stage 54 n=16 tolerance，不降低驗證門檻。

**限制**：本研究只確認指定合成案例之中心外插／平均應力觀測與網格差異縮小，不建立精確收斂階數或高網格極限，亦非全場／積分點峰值及真實材料、產品構造或 ADM 容量驗證。維持 `EVIDENCE GATED`、`MATERIAL_CAPACITY_NOT_ADMITTED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`；真實折板、加勁肋、支承／接觸、缺陷與屈曲另需 evidence/admission。

## 第五十六階段：理想簡支鋁板支承對照（2026-10-12）

**Stage 56／PR #90**（merged-main SHA `aaf79bb4323299658f54cb0aaa034dd635b5de92`）建立僅供合成研究用的 100×100×2 mm 等向線彈性鋁板 S8R NLGEOM P1，E=69000 MPa、ν=0.33、p=0.0001 N/mm²，n=4／8／16。理想簡支為全周限制法向平移、兩個角點最小面內 pin／slider 約束，其餘旋轉自由；此處沒有實際扣件、框架接觸或旋轉支承勁度。以獨立 Kirchhoff–Navier 雙奇數正弦級數求中心撓度，61 階參考約 0.00078694836 mm，41／61 截斷差異在本算例低於 1e-6 相對值；同時使用既有同尺寸四邊固定 CCX synthetic case 對照。真實 CCX 簡支中心撓度依序為 n=4：0.0008086117 mm、n=8：0.0008001258 mm、n=16：0.0007999044 mm；四邊固定為 0.0001819677、0.0002296706、0.0002382199 mm。簡支值由上方逐步下降接近解析值，細網格相對差約 1.646%，並觀測相鄰網格差縮小。本研究僅證明指定合成模型的支承差異與撓度趨勢。

**CI provenance**：初版因 fixture 邊界字串的跳脫換行而修正；其後 real CCX 首輪因預設錯誤的網格單調增加假設而拒絕；診斷 run `38213269744` 明確輸出三網格中心撓度後，按真實觀測改為單調下降並維持既有 12% 細網格 Navier 比對門檻。另一次 CI 將兩種不同負向測試提前拒絕的原因分開，未降低門檻。最終 exact-head `060ee7c07067913256ef9757e02677c9318f186f` 的 Repository CI `38213568136`、真實 CalculiX CI `38213568135` 均 SUCCESS，merged-main Repository CI `38213746691` SUCCESS，合併來源 read-back 已成立。

**未 admission**：`MATERIAL_CAPACITY_NOT_ADMITTED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`，真實鋁板四邊支承的扣件、接觸、折邊、加勁肋、局部挫屈、實際邊界勁度及 ADM 強度設計均未建立。Stage 56 不改動原 `run_aluminum_research.py` 可接受的支承種類，不新增一般 user-deck 執行路徑。所有研究篩選門檻均非設計規範容許誤差。

## 第五十七階段：合成 U 型折邊薄壁懸臂殼模型（2026-10-12）

**Stage 57／PR #92**（merge SHA `3a2d83e04d12e48e7119038b0328ccf6140552dd`）依使用者明確授權，新增固定幾何合成 U 型折邊薄壁懸臂梁式殼模型：長 300 mm、U 主面寬 40 mm、兩側直角折邊各 20 mm、t=1.5 mm，synthetic E=69000 MPa、ν=0.33；S8R 二次殼以 8／16 長度網格、24 個截面元素，共用連續折角節點。根部固定六自由度、自由端沿 U 截面以二次一致邊線節點力分配總面外 1 N；不開放外來 user-deck 或真實產品條件。

**獨立近似**：薄壁中面截面積分給出中性軸 z=5 mm、Iy=5000 mm⁴，Euler–Bernoulli 懸臂梁自由端 `FL³/(3EI)=0.0260869565 mm`，根部彎矩需求 300 N·mm。真實 CalculiX 合成殼的功共軛端線加權平均位移：8 網格 `0.02655514979 mm`，16 網格 `0.026570833125 mm`；16 網格相對理論差 `1.85486%`，兩層差除以梁參考值約 `0.06012%`。兩組根部 Z 向合力分別 `1.000000156 N`、`1.000000599 N`，符合指定合力研究界線；不等於獨立六分量平衡。

**驗證**：早期候選發現折邊座標索引、根部與自由端節點數及截面元素計數不一致，先修正後重新觸發 exact-head CI；最終 head `fa88d69d354758e065da67ad56907245708e3083` 的 Repository CI `38228085522`、真實 CalculiX CI `38228085537` 均 SUCCESS，merged-main Repository CI `38228840117` SUCCESS，canonical source 已在合併 SHA read-back。保留失敗歷程作修正 provenance，不把先前候選 PASS 當作最後 head 的執行證據。

**適用性與拒絕外推**：本階段僅以指定 U 型懸臂受限案例驗證幾何、荷載配分、端部位移及根部平移反力。梁理論僅近似殼響應，模型沒有折彎圓角、成形硬化／殘餘應力、真實加勁肋或離散扣件、風壓載入、接觸／局部挫屈／初始缺陷、獨立旋轉反力矩、完整六分量全域平衡或 ADM 工程容量。所有 acceptance 維持 `EVIDENCE GATED`、`MATERIAL_CAPACITY_NOT_ADMITTED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`；研究門檻不能當正式設計允許誤差。下一步若研究實際加勁／折板受風壓情形，須先取得符合物理條件的獨立載荷與場值基準，另行 admission。

## 第五十八階段：U 型折邊主板均布面壓（2026-10-12）

**Stage 58／PR #94**（merge SHA `ed397f0b091eca2dfef9ed500e5feb25ac4553bc`）依使用者當次授權，沿用 Stage 57 合成 U 型折邊懸臂 S8R 殼（長 300 mm、主面 40 mm、兩側折邊 20 mm、厚度 1.5 mm、E=69000 MPa、ν=0.33），僅對主面 WEB set 加 `*DLOAD,P,0.0001 N/mm²`，兩側折邊不直接加壓，根部六自由度固定；8／16 長向網格真實 CCX 求解並保留 deck／DAT／STA／FRD SHA-256 provenance。

**獨立理論基準與實測**：薄壁截面 `Iy=5000 mm⁴`，依 Euler–Bernoulli 均布線載懸臂近似，主面投影壓力總合力 `1.2 N`、根部彎矩需求 `180 N·mm`，理論端部撓度 `q B L⁴/(8 E Iy)=0.0117391304348 mm`。真實 CalculiX 8／16 網格主面自由端 Simpson 權重位移分別 `0.0119553254167 mm`／`0.0119599727083 mm`，細網格相對梁近似差 `1.88125%`，兩網格變化／理論量值 `0.039588%`。原始 ROOT RFz：`-1.175000514 N`、`-1.187500322 N`，只是受載邊界的原始節點輸出方向／量級診斷，**不可等同於扣除施加荷載後的純支承反力**。

**CI**：PR exact-head `358af71f7413de3af6b3dac1ebf9d763776e76bb` 的 Repository CI `38232753445` 與真實 CalculiX CI `38232753461` 均 SUCCESS，包含新增案例驗證標記 `U_FOLD_WEB_PRESSURE_BEAM_SCREENING_PASS`；合併後 exact-main Repository CI `38233094823` SUCCESS，合併後 canonical source 與工作狀態已 read-back。研究門檻（相對梁理論 25%、8／16 差 15%）僅屬受限 synthetic screening，**不是實際工程容許誤差**。

**邊界**：這是 U 型折邊**懸臂梁式殼**的主面均布面壓，不是四邊支承整片折邊鋁板的風壓容量。未 admission 完整 follower pressure 全域反力、獨立旋轉反力矩、局部板殼應力峰值、折角圓弧、成形後材料、接觸／扣件、加勁肋／局部挫屈或 ADM 設計容量。維持 `EVIDENCE GATED`、`MATERIAL_CAPACITY_NOT_ADMITTED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。

## 第五十九階段：合成中心連續加勁肋之 S8R 板件（2026-10-12）

**Stage 59／PR #96**（merge SHA `caec3e16447cc34f03112b244f8d7890ee077460`）依使用者明確授權，在合成 100×100×2 mm 四邊固定矩形鋁板中線增加 S8R 共用節點之理想連續直立加勁肋，高度 0／4／8 mm，厚度 2 mm；E=69000 MPa、ν=0.33、主面 `WEB,P,0.0001 N/mm²`，只在 WEB 上加壓，肋不直接加壓。8／16 網格共六組真實 CalculiX 研究算例，輸入與 STA／DAT／FRD SHA-256 隨 CI 證據輸出，公開版本完全 synthetic。

**獨立近似與實測**：四邊固定薄板 Kirchhoff 一項 Ritz 基準中心撓度 `0.0002574911071 mm`；採相同簡化位移形狀之板彎曲能＋中心梁彎曲能，依 `I_rib=T h³/3` 得加肋研究近似，作定性勁度順序判讀，**不是完整板肋相容／翹曲應力場精確解**。真實 CCX 中心撓度：8 網格 h=0／4／8 mm 為 `0.0002296706／0.0001741728／0.0001035602 mm`；16 網格分別為 `0.0002382199／0.0001840568／0.0001079533 mm`。兩種網格均觀測肋高增加、中心撓度下降；未加肋 16 網格與單項 Ritz 參考差約 7.48%，各肋高 8／16 網格差小於受限 15% 檢查門檻。**本研究沒有建立真正獨立的加肋板精確場值 oracle，也不提供一般 mesh convergence order。**

**驗證來源**：PR exact-head `dc1cb0952810be8bc7dcd020fdae3219f80609c0` 之 Repository CI `38252655579` 與真實 CalculiX CI `38252655598` 均 SUCCESS，包含 `CENTER_RIB_LOAD_TRANSFER_SCREEN_PASS`；merge-main 版本為 `caec3e16447cc34f03112b244f8d7890ee077460`。Merged-main workflow 與 canonical remote read-back 應另以完成狀態查核，不以 PR CI 取代。

**Engineering admission 邊界**：板／肋共用中面殼節點是理想剛性連續連接，不代表現場焊接、螺絲、膠或接觸；未 admission 實際折彎／成形材料、初始缺陷、局部挫屈、全場積分點應力極值、獨立旋轉支承反力／反力矩、完整六分量平衡、真實鋁板強度或 ADM 構件容量。狀態持續 `EVIDENCE GATED`、`MATERIAL_CAPACITY_NOT_ADMITTED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。

## 第六十階段：中心加勁肋端部理想約束的荷載路徑（2026-10-12）

**Stage 60／PR #98**（merge SHA `011099fef194dddb0b252b0abd907ecff7a9c0b0`）在 Stage 59 的合成 100×100×2 mm、E=69000 MPa、ν=0.33、WEB 壓力 P=0.0001 N/mm²、四邊固定、中心連續高 8 mm S8R 加勁肋上，增加兩端 16 個肋上部節點之**額外全固定**，與肋端不另約束對照（n=8／16，共四個 CalculiX 2.21 synthetic case）。兩案同一幾何、荷載、材料、殼網格；差異限定於 RIB_END 理想額外運動約束。板與肋共節點仍非現場焊接、螺絲、膠或其他實際連接。

**獨立概念與數值**：在同一外力下，線彈性受限位移空間增加同質約束，荷載功共軛柔度不應上升；本研究用整張 WEB 的 S8R 二次形狀函數面積積分（corner -1/12、midside +1/3）獲取 z 向平均位移代理，因 NLGEOM follower pressure 故此定理只作合成**小變形近似篩選**，不是任意非線性證明。8 網格肋端自由／額外固定平均位移 `3.8218132e-05／2.5298594073e-05 mm`；16 網格 `4.0286069131e-05／2.6367923970e-05 mm`，16 網格 fixed/free 比值 `0.65451717`，下降約 `34.55%`。兩支承的兩網格差異分別約 5.13%／4.06%，低於本次 synthetic 的研究性 15% 門檻。肋端固定方案有非零原始 RIB_END RFz 訊號（8 網格 signed -0.17852374 N、sum absolute 0.60848434 N），只證明額外理想約束參與 solver response，**不可升格為實際扣件力或獨立完整反力**。

**CI／provenance**：PR exact-head `d8143aa5ff50370c0a6e736199c6cc4b1722cf43` 的 Repository CI `38259477743` 與真實 CalculiX CI `38259477694` 均 SUCCESS，新增測試標記 `END_TRANSFER_KINEMATIC_CONSTRAINT_SCREEN_PASS`。合併後 current main `011099fef194dddb0b252b0abd907ecff7a9c0b0`；merged-main CI 應按獨立 GitHub 結果確認，不能以 PR CI 代替。

**未 admission**：真實肋端轉接角碼、扣件接觸／間隙／滑移／轉動勁度、局部板肋應力極值、有效連接設計、完整六分量平衡／旋轉反力矩、初始缺陷、局部挫屈、任何實際鋁材或 ADM 容量。持續 `EVIDENCE GATED`、`MATERIAL_CAPACITY_NOT_ADMITTED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。

## 第六十一階段：加勁肋端部 Z 向有限剛度彈簧（2026-10-12）

**Stage 61／PR #100**（技術 merge SHA `50c83eb5335e2919e9578bd65047e456347ecbde`）延續 Stage 60 已完成的中心連續高 8 mm S8R 肋板，合成四邊固定 100×100×2 mm、E=69000 MPa、ν=0.33、WEB 均布 P=0.0001 N/mm²，保留同一次 real CCX workflow 中 n=8／16 肋端自由模型的 exact deck／DAT／STA／FRD evidence。於同樣 16 個高於板面之肋端節點追加接地 `SPRING1` Z 向自由度 3 的**有限線性彈簧**，每節點 synthetic stiffness `1000`、`10000 N/mm`，另執行四組 CCX；沒有增加六自由度完全固定或任何真實扣件屬性。

**數值觀測與物理界線**：受限 S8R WEB 形狀函數整面 U3 積分之名義載重功共軛平均位移代理，n=8 自由／1000／10000 N/mm 為 `3.8218132e-05／3.8143975542e-05／3.7845806625e-05 mm`；n=16 分別 `4.0286069131e-05／4.0220265749e-05／3.9968016563e-05 mm`。n=16 高剛度比自由柔度代理 `0.99210515`，降幅約 `0.7895%`，不同於 Stage 60 肋端額外六自由度全固定所得 `0.65451717` 比值。16 節點簧力僅可由指定剛度乘求解節點位移 (k u) **衍生估算**，不得稱為獨立 CCX 彈簧元件應力／支承反力量測；線彈性正半定附加勁度的荷載功單調性在此 NLGEOM follower pressure 中僅作小變形研究性篩選，非一般非線性定理。

**驗證來源**：PR exact-head `8aa1fb2425c0363128aa79a654709c2536d97cc4` Repository CI `38262403563` 與真實 CalculiX CI `38262403666` 均 SUCCESS，新增標記 `RIB_END_SPRING_STIFFNESS_TREND_PASS`，兩網格變化研究閾值 15% 受限通過。技術 merged-main SHA 為 `50c83eb5335e2919e9578bd65047e456347ecbde`；合併後 Repository CI 與 canonical read-back 須另行確認，不可把 exact-head PR CI 視同已驗證 main。

**Engineering admission 仍拒絕**：合成剛度並非扣件試驗數據；未建立實際角碼、螺絲、錨定、摩擦／滑移／接觸、彈簧方向耦合、旋轉柔度、全場積分點應力、局部屈曲、初始缺陷、獨立旋轉反力矩、六分量全域平衡、材料塑性或 ADM 設計容量。狀態維持 `EVIDENCE GATED`、`MATERIAL_CAPACITY_NOT_ADMITTED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。

## 第六十二階段：加勁肋端部平移彈簧方向對照（2026-10-12）

**Stage 62／PR #102**（技術 merge SHA `3cd00fe9b10d2b78fd0a793973dfaa0e65721638`）沿用 Stage 60–61 synthetic 100×100×2 mm、E=69000 MPa、ν=0.33、中心肋高 8 mm、WEB P=0.0001 N/mm² 四邊固定 S8R 板。僅比較 16 個肋端上部節點之 `SPRING1` 全域 X(1)、Y(2)、Z(3) 平移方向，每個節點勁度均 `10,000 N/mm`；新增 X／Y 的 n=8／16 四組真實 CalculiX，Z 與無額外彈簧基準從**同一 CI workflow** 的 Stage 61／60 嚴格輸出回讀。此處沒有任何旋轉 DOF 彈簧或現場扣件資訊。

**實際 CCX 觀測**：以同一 WEB S8R 形狀函數積分 z 向位移作名義固定方向外載功共軛平均位移代理，n=16 無彈簧 `4.028606913125e-05 mm`、X 彈簧 `3.13260750203125e-05 mm`、Y 彈簧 `4.028606913125e-05 mm`、Z 彈簧 `3.99680165625e-05 mm`；X 減少約 `22.24%`，Y 在此對稱合成工況與無額外彈簧相同，Z 減少約 `0.79%`。n=8 也觀察到相同方向趨勢。各方向 8／16 網格相對差均約 4.6–5.3%，符合受限 15% 研究篩選，但沒有完整 mesh convergence order 或獨立殼場精確解。

**證據**：PR exact-head `a3ecc8287c3b33f09650fe852b25faac900b507d` 的 Repository CI `38271242796` 與真實 CalculiX CI `38271243144` 均 SUCCESS，真實執行標記 `RIB_DIRECTION_TRANSLATION_SCREEN_PASS`。合併後的 main CI 應獨立核對。所有 `k u` 彈簧力均為衍生估算而非獨立 CCX 接點反力；NLGEOM follower pressure 下的荷載功減少僅用於此極小位移理想化案例之趨勢 screening，不是一般非線性定理。

**拒絕工程外推**：方向敏感度不等於實際角碼、螺絲、膠、支承連接方向效能；Y 向在本算例結果不變並非一般構造性質。未 admission DOF4–6 轉動勁度、局部翹曲或應力極值、完整六分量平衡、初始缺陷、屈曲、材料塑性及 ADM 容量。狀態保持 `EVIDENCE GATED`、`MATERIAL_CAPACITY_NOT_ADMITTED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。

## 第六十三階段：隔離剛性槓桿之平移彈簧轉動柔度（2026-10-13）

**Stage 63／PR #104**：研究範圍是理想剛性槓桿與接地 `SPRING1` 平移 DOF3；利用彈簧配置位置與 `u_z(x)=w+x·s` 的小轉角假設，建立獨立 2×2 幾何剛度矩陣並以真實 CalculiX 2.21 解比對。**沒有使用或驗證 `SPRING2` DOF4–6 的純轉動彈簧**，也未把 Stage 62 X 向彈簧減撓效果直接宣稱為純轉動支承。

- 純力偶合成例：在 `x=±50 mm` 各接 `200 N/mm` DOF3 彈簧，以 `±1 N` 產生 100 N·mm 名義力偶。解析旋轉斜率 `0.0001 rad`，求解端部 U3 為 `−0.005／+0.005 mm`，中心 U3 為零；由 `k×u` **衍生**簧力合計 0 N、加權力矩 100 N·mm，受限解析與求解一致。
- 偏心荷載分配合成例：三個主要接地平移支承（`x=−50／0／+50 mm`，`k=100／200／300 N/mm`）加兩個 `x=±10 mm`、`k=500 N/mm` 輔助支承，於 `x=+10 mm` 施加 1 N。求解中心 U3 約 `0.0006024096 mm`、位移斜率約 `3.6144578×10⁻⁶ rad`；簧力 `k×u` 合計約 1 N、`x×k×u` 合計約 10 N·mm。額外兩個彈簧**同時增加平移剛度與幾何轉動耦合**，並非獨立純轉動彈簧。
- 有限 EI Euler–Bernoulli 值在 Stage 63 僅為**獨立理論參考，沒有相對應的真實 CCX 有限剛度梁驗證**；此缺口由下一階段另行處理。

**證據身分**：PR head `a066b5f85edcd7ceb8c82690580db94b96a88693`；[Repository CI `38277415445`](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/38277415445) 與 [real CCX CI `38277415991`](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/38277415991) 均 SUCCESS，新增五項 Python 測試通過；[PR #104](https://github.com/masini1491/building-envelope-engineering-kb/pull/104) 合併 SHA `151738eef3bb78136521db031a880ca407b06393`，相同 SHA 的 merged-main [Repository CI `38343837490`](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/38343837490) SUCCESS。CI 中 `.inp/.dat/.sta/.frd` 與求解檢查器的證據僅屬 isolated synthetic 模型。

**尚未認可**：S8R 真實連接、局部殼旋轉、獨立量得的彈簧反力／反力矩、完整六分量平衡、材料／扣件強度、真正工程設計容量。`EVIDENCE GATED`、`MATERIAL_CAPACITY_NOT_ADMITTED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`。

## 第六十四階段：有限 EI 梁之彈性根部轉動對照（2026-10-13）

**Stage 64／PR #105**：將 Stage 63 的剛體極限與有限梁彎曲分離。使用完全合成的 `B31` 懸臂梁（`L=100 mm`、`E=69000 MPa`、`ν=0.33`、方形 `10×10 mm`，端部 1 N）對照根部全固定與具有等效轉動柔度的方案；各採 `n=4／8` 網格。Euler–Bernoulli 小撓度解析基準為純梁彎曲 `0.00579710145 mm`、根部彈性轉動額外撓度 `0.010000000 mm`、總撓度 `0.01579710145 mm`，等效轉動剛度 `10⁶ N·mm/rad`。

**失敗與修復必須共同保留**：初版 PR head `19a2c980eef23d34b3d2c1f926c6a59c056cdf0a` 的 real CCX [CI `38326051275`](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/38326051275) **FAIL**，診斷為所嘗試的 rigid-body coupling 沒有形成主 `B31` 根部轉角到側向平移彈簧的有效傳力鏈，彈性端出現無界量級位移。**不是**放寬容差即可接受的結果。修正版以和主梁共節點的兩根高剛度**但仍有限 EI**之輔助 `B31` 梁將根部轉動傳給接地 DOF3 彈簧，並新增無界位移與彈簧未參與的拒絕條件；此方法不能宣稱為理想 rigid MPC、真實角碼或可用的原生旋轉 DOF 彈簧。

| 梁端向下位移（mm） | Euler–Bernoulli 近似 | CCX n=4 | CCX n=8 |
| --- | ---: | ---: | ---: |
| 根部固定 | 0.00579710145 | 0.005729936 | 0.005808374 |
| 根部彈性轉動總位移 | 0.01579710145 | 0.015576700 | 0.015719570 |
| 額外根部轉動位移 | 0.01000000000 | 0.009846764 | 0.009911196 |

以細網格為例，固定端撓度相對理論差約 0.19%，轉動增量差約 0.89%；兩側由 `k×u` 衍生的力矩幅值約 100 N·mm。這是合成 B31／輔助梁模型的有限精度對照，**不是**殼加勁肋局部應力或實體連接的轉動剛度驗證。

**證據身分**：修正版獨立候選曾以 head `021d18b9c4e04d0d996383fd7747a6efbd78a219` 經真實 CCX 成功驗證，之後為整合 Stage 63 workflow，PR #105 最終 exact head `f0d55c23ea4be58095adf3a18aee31f574688d3d` 再跑 [Repository CI `38343903329`](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/38343903329) 與 [real CCX CI `38343903311`](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/38343903311)，皆 SUCCESS；[PR #105](https://github.com/masini1491/building-envelope-engineering-kb/pull/105) merge SHA `e8052103934cf38f71adde9903d0f35a4eae2195`，merged-main [Repository CI `38344143862`](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/38344143862) SUCCESS。**未 admission**完整六分量反力矩、真實 S8R 連接、材料容量或 ADM。

## 第六十五階段：合成 S8R 加勁肋端部彈簧高度視窗（2026-10-13）

**Stage 65／PR #106**：沿用 Stage 59–62 的 `100×100×2 mm`、中心連續高 8 mm S8R 加勁肋、E=69000 MPa、ν=0.33、四邊固定及僅 WEB `P=0.0001 N/mm²` 合成模型。與同一次 CI 重新驗證的肋端自由／全高度 X 平移彈簧基準相比，低位 `z=1–4 mm` 與高位 `z=5–8 mm` 各只在兩端共 8 個節點接 `SPRING1` DOF1，`k=10000 N/mm` 每節點，分別在 n=8／16 兩種網格求解。

| WEB 功共軛平均 U3（mm） | n=8 | n=16 |
| --- | ---: | ---: |
| 肋端自由 | 3.8218132e-05 | 4.028606913125e-05 |
| 低位彈簧 | 3.601197786458334e-05 | 3.78892456875e-05 |
| 高位彈簧 | 3.036418803125e-05 | 3.1839676225520835e-05 |
| 全高度彈簧 | 2.9887918708333333e-05 | 3.13260750203125e-05 |

在這個特定對稱模型及 16 網格中，低位、高位、全高度相對自由端的位移代理依序降低約 5.95%、20.97%、22.24%。兩種網格各條件的變化約 4.6%–5.1%，只滿足**研究性**雙網格 screen。獨立的**假設剛截面** `u_x(z)=u_0+zθ` 幾何矩陣：兩視窗皆 `K00=80000 N/mm`、凝縮轉動項 `K11−K01²/K00=100000 N·mm/rad`；但低位 `K01=200000 N`、`K11=600000 N·mm`，高位 `K01=520000 N`、`K11=3480000 N·mm`。**凝縮值相同不代表 S8R 局部殼場或轉動剛度相同**；此矩陣也不是獨立的殼場 oracle。

**證據身分**：PR #106 head `62b3685dc078d39d2bb11b8413b9dff492bb3f3c`；[Repository CI `38352604291`](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/38352604291)、[real CCX CI `38352604287`](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/38352604287) 均 SUCCESS，Stage 65 四項專項單元測試通過；[merge SHA `a04711c04aff9d9f16f2a43d3d2fa141b0485cee`](https://github.com/masini1491/building-envelope-engineering-kb/pull/106) 與 merged-main [Repository CI `38409511220`](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/38409511220) 已驗證。全域正負簧力互抵不能判斷每端沒有局部傳力；非真實扣件或純旋轉彈簧容量。

## 第六十六階段：肋端逐高度位移及局部彈簧群衍生內力（2026-10-13）

**Stage 66／PR #107**：重用**同次 CCX 求解** Stage 65 的四組 n=8／16 × 低位／高位數據；不新增 deck。`check_rib_local_groups.py` 逐端讀取全部 16 個肋端節點的 `(U_x,U_y,U_z)`，以選定 8 個有效 DOF1 彈簧的既定 `k` 逐顆形成 `k U_x`、`z k U_x`、`½ k U_x²`，分別彙整左／右端之帶號量與絕對量，核對高度完整性、兩端反對稱與彈簧儲能恆等關係。

| n=16，單端衍生值 | 低位 1–4 mm | 高位 5–8 mm |
| --- | ---: | ---: |
| `abs(sum(k U_x))` | 0.15926866 N | 0.24771551 N |
| `abs(sum(z k U_x))` | 0.49812865 N·mm | 1.6436892 N·mm |
| 最大單顆 `abs(k U_x)` | 0.07215462 N | 0.07210295 N |
| 兩端合計 `sum(½ k U_x²)` | 8.3583460e-7 N·mm | 1.55693199e-6 N·mm |

兩端 `sum(k U_x)` 與 `sum(z k U_x)` 帶符號總和在此**對稱載重模型**為零，然而單端絕對量與儲能不為零，**全域帶號相消不可推論局部連接無受力**。上表是求解位移乘**人為指定合成剛度**之衍生診斷；沒有獨立從 CalculiX 取得扣件反力／反力矩，`z k U_x` 亦未取得完整結構力矩驗證。

**證據身分**：PR #107 head `a68978d77d772766bbae137db26a605370754323`；[Repository CI `38423669157`](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/38423669157) 與 [real CCX CI `38423669241`](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/38423669241) SUCCESS，新增四項單元測試通過，檢查器輸出 `STAGE66_LOCAL_SPRING_GROUP_POSTPROCESS_PASS; NO_INDEPENDENT_SUPPORT_REACTION`；[PR #107 merge SHA `157674fab45692e7a816f29ca50a82844d83b5fe`](https://github.com/masini1491/building-envelope-engineering-kb/pull/107)，merged-main [Repository CI `38424867812`](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/38424867812) SUCCESS。

## 第六十七階段：彈簧群衍生力峰值、高度分布及雙網格比較（2026-10-14）

**Stage 67／PR #108**：在同一組 Stage 65／66 real CCX 受限數據上進一步驗證各端最大單顆 `abs(k U_x)`、正規化各高度力幅值比例、`sum(abs(k U_x))`、`sum(z abs(k U_x))` 與力幅值加權高度 `z̄`。在 n=8／16 間比較各分量、各高度量級與最大值所在高度；僅採**兩網格差異 screen**，不建立一般網格收斂階數，不將帶絕對值的高度加權指標寫成真實支承反力矩。

| 單端研究量 | 低位 n=16 | 高位 n=16 |
| --- | ---: | ---: |
| 最大單顆 `abs(k U_x)` | 0.07215462 N，z=4 mm | 0.07210295 N，z=8 mm |
| 四顆力幅值總和 | 0.15926866 N | 0.24771551 N |
| 力幅值加權高度 `z̄` | 3.12759993 mm | 6.63539074 mm |
| 最高單顆力占本端總幅值 | 約 45.30% | 約 29.11% |
| 最大單顆力 n=8／16 相對差 | 約 5.13% | 約 4.27% |

低位四顆按 `z=1／2／3／4 mm` 的力幅值占比約 `7.20／18.15／29.35／45.30%`；高位 `z=5／6／7／8 mm` 約 `20.66／24.25／25.98／29.11%`。**此相同合成模型的高位配置，使每端力幅值總和與力臂指標提高，但最大單顆幅值並未明顯提高**；此敘述不是一般構造安全結論。

**失敗與修復 provenance**：PR 初版 head `dd4726f3cb40076bd7d2b20f8c950f1410dbead2` 的 Repository CI `38425721900` SUCCESS，但 [real CCX CI `38425721923`](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/38425721923) **FAIL**：新增負面測試原欲驗證重複高度，所造輸入卻先違反既有 `z×k U_x` 算術恆等檢查。只修正測試資料，使其確實測試重複高度拒絕分支；不放寬 solver 或 engineering 容差。修正版 exact head `b2f24e52d34211fc0022a9a33a83af20fe31b33f` 的 [Repository CI `38425933726`](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/38425933726) 與 [real CCX CI `38425933807`](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/38425933807) 均 SUCCESS，六項單元測試全過、標記 `STAGE67_LOCAL_FORCE_HEIGHT_MESH_SCREEN_PASS; NO_INDEPENDENT_REACTION_OR_CAPACITY`。 [PR #108](https://github.com/masini1491/building-envelope-engineering-kb/pull/108) merge SHA `5a09072cd2635a2fb88d3651ab6ebe1f33c4ea19`，merged-main [Repository CI `38426821001`](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/38426821001) SUCCESS。

### Stage 63–67 共通不可外推與下一道研究關卡

上述五階段只證明各指定**合成**模型與指定輸入/輸出 checker 的受限相容。`SPRING1` 只具有指定全域**平移** DOF 的合成線性剛度；力臂所生等效轉動效應、B31 輔助梁傳力、S8R 彈簧高度配置**互相不能當成相同物理連接**。任何 `k×U`、`z×k×U`、正規化力幅值、`Σ|kU|` 或儲能診斷均衍生自相同求解位移，不是額外獨立量測的實體扣件支承反力、反力矩或局部峰值應力。

**後續研究候選（尚未 admission，非自動執行）**：先限定一個具有獨立 oracle 的 solver 反力／element-force 觀測測試：① 從 CalculiX 2.21 官方欄位與實際輸出核對原始 SPRING1 元件力、節點 RF、MPC 消去／約束來源及其符號／座標約定；② 明確區分「由既定 kU 重算」、「由求解器元素輸出」與「經外部解析或試驗獨立驗證」三個證據層級；③ 在隔離小模型及負面檢查先成立後，才判斷 S8R 的局部場值／六分量支承需求是否可 admission。獨立的真正轉動反力矩、整片殼積分點極值、局部支承／扣件非線性與實際規範容量均需另獲可靠模型、來源與獨立驗證，不因追加本段文字即取得工程能力。

所有後續設計相關結論繼續維持 `EVIDENCE GATED`、`MATERIAL_CAPACITY_NOT_ADMITTED`、`GENERAL_GLOBAL_BALANCE_NOT_ADMITTED`；**不能**把本次部件研究數值作為 ASTM／ADM 或實際帷幕牆設計容量。
