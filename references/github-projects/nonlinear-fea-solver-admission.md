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
