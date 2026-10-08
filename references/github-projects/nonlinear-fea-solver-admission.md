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
