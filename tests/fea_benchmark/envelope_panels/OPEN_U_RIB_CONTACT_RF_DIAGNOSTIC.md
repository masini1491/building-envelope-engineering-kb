# 開口 U 肋底面接觸｜RF、CFN 與 MPC 觀測限制

## 背景及證據

PR #131 的合成鋁板／U 型肋 S8R 面接觸，CalculiX 2.21 已能以 `*CONTACT PRINT,SLAVE=RIB_BASE_UNDERSIDE,MASTER=PLATE_TOP` 輸出 `CF/CFN/CNUM`，但 `*NODE PRINT RF` 三組原始觀測在接觸工況仍不能重建全域平衡。原始 artifact：CalculiX run `38855616149`、artifact `12027213102`。第一輪真正求解的接觸工況，n=8、n=16 壓合 `RF3` 殘差分別約 −44.4375 N、−17.8664 N；無接觸工況則近零。**絕對不可改用更寬容差宣稱 PASS**。

重新讀取資料後，n=8／16 壓合的 slave CFz 分別約 +14.4088／+14.1058 N；接觸面積分別為 34.02925／59.4862 mm²。分離工況的接觸面積與力也不為零且對網格敏感。**這不是合格單向接觸與設計傳力證據。**

## 驗證邊界

CalculiX 的 `RF` 官方輸出契約指出 MPC 相關作用力不被直接計算。S8R shell 內部展開與 contact 需要額外的 MPC／作用力語意查證，因此三個 `RF3` 區塊相加 **不是經證實的完整全域平衡 oracle**；但這也不表示模型已平衡。`CF/CFN` 是接觸面觀測量，屬內力，不能直接加到所有外部 RF 以湊出平衡。參考：<https://feacluster.com/CalculiX/ccx_2.18/doc/ccx/node305.html> 及 <https://github.com/Dhondtguido/CalculiX/issues/97>（issue 只作調查線索，非本案 bug 確證）。

`check_u_rib_contact_observations.py` 只取同一次求解的 final-time 節點 RF3 區塊及 `*CONTACT PRINT` slave 表面統計；明確標示 `UNPROVEN`／`NOT_ESTABLISHED`／`NOT_ADMITTED`，不是新的 contact physics PASS，亦不會停止或放寬既有 `check_u_rib_base_contact.py` 的 fail-closed 驗證。


## 已宣告但無實際接觸之控制組（2026-10-16）

PR #131 head `ab256396a996b190f9600d4d685cdca34588026e`、CalculiX CI run `38886863783`、artifact `12040810140`：把獨立 U 肋沿 Z 向移動 +20 mm，保留接觸配對，n=8／16 均完成求解。原始 `.dat` 的最終 `*CONTACT PRINT` 六項表面總力皆為 0 N、接觸面積為 0 mm²，但未定義的表面中心／法線、正負號法向力及剪力輸出為 `NaN`；此情況不應與有效有限數值等同，也不應直接視為資料完整損壞。

兩組三個原始 RF3 分區數值均與同次 `unlinked` 對照逐項相同，n=8／16 的原始 RF3 合計分別約 +1.56e-6／−1.118e-6 N。因此本控制組支持「已宣告配對但無接觸」不會自行造成已觀測的巨幅 RF3 殘差，但**未**證明活動接觸工況的 MPC 反力來源或全域平衡。

`check_u_rib_contact_observations.py` 對此 **唯一明確結構**（總力／總力矩皆為有限零、接觸面積為有限零、法向與剪力均為文字 `NaN`）將記錄 `INACTIVE_ZERO_AREA_UNDEFINED_NORMAL_AND_SHEAR`，以 JSON `null` 保存兩個未定義值；任何面積非零、總力非零、錯誤或非有限數值仍 fail-closed。此為輸出格式觀測，不是物理 admission，也不更動原有 RF3 平衡驗收門。


## 已知外力的獨立殼反力診斷（已取得 exact-head CCX 2.21 結果）

以未接觸 `unlinked` S8R 板／U 肋為母本，在 U 肋底部中央附近兩個未拘束植釘候選節點各施加 ±0.5 N，形成正、反向 ±1 N **已知外力**；n=8／16 共四組。仍保留鋁板的獨立 +0.02 mm 人工位移控制。比較 `RIB_END_RF` 的原始反力和已知輸入力 `R+F`，同時記錄板邊／中心 RF3、STA 完成時間、原始輸入與輸出 SHA-256。此診斷不含接觸、植釘彈簧或材料容量，不使用推導殼 MPC 力修補輸出，也不改原 PR 的 contact FAIL gate。

### 真實求解結果與驗證範圍

- Exact head：`74b4b0a908b5983003931a67d2e2c382a973198b`；CalculiX CI run `38930367631`；artifact `12058024468`（ZIP SHA-256：`cc74b9463cb323c76fb65a4a3cb43b778a0c81ff14a87e54a395f4e7f0084426`）。
- n=8，施加 +1／−1 N，U 肋兩端原始 RF3 分別為 −0.9999972／+0.9999986 N；殘差 +2.8e-6／−1.4e-6 N。
- n=16，施加 +1／−1 N，U 肋兩端原始 RF3 分別為 −1.00000034／+1.00000024 N；殘差 −3.4e-7／+2.4e-7 N。
- 四組 `.dat`、`.sta`、`.frd` 經 artifact 內原始檔 SHA-256 逐項核對均一致。第一次 artifact 只有輸入檔 `.inp` 的 JSON SHA-256，沒有保存原始 `.inp` 本身；後續 CI 補上輸入檔路徑，以便 artifact 接收端獨立重算其雜湊。
- 依既有合成平衡絕對誤差基準 0.0002 N，加入 **只適用無接觸、已知 ±1 N 外力** 的 deterministic fail-closed 檢查；這不是一般 S8R、接觸或任意 MPC 反力的 admission。
- 此負向控制支持「已知非接觸外力可由本合成 U 肋兩端 RF3 平衡」，但不能推出活動接觸時的偽節點力、MPC 反力或受力等價；原本 `OPEN_U_CONTACT_RF_GLOBAL_Z_IMBALANCE` 仍保持 FAIL。

**下一門**：建立獨立可驗證的 MPC 約束傳力重建／完整反力觀測，或可核對的其他數值 oracle 後，才允許研究 contact／網格收斂及合成植釘共同作用。

## 主從面互換隔離觀測（已完成 real CalculiX 2.21；負面結果）

本次不改合成幾何、網格、材料、理想支承、接觸 penalty 或 ±0.02 mm 人工位移；僅交換接觸 pair 及 CONTACT PRINT 的 slave/master。PR #131 exact head `1c4f881331713e0977d467bba5280f82608a6918`；CalculiX run `38937038025`，artifact `12061078620`（ZIP SHA-256 `20870ab18de84d517b43d24ffbba0c23a4d39161dca44e58ea1aa0b6188e83e6`）。四組 `.inp/.dat/.sta/.frd` 對應 JSON 的 16 組 SHA-256 全部核對一致；原始配對觀測也來自同次 CI。

| 網格／方向 | 原配對 raw RF3 合計 (N) | 反轉配對 raw RF3 合計 (N) | 原配對 slave CFz (N) | 反轉配對 slave CFz (N) | 原配對接觸面積 (mm²) | 反轉配對接觸面積 (mm²) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| n=8 toward | −44.4374645 | −44.4653812 | +14.40875 | −14.39054 | 34.02925 | 28.48912 |
| n=16 toward | −17.8664376 | −17.8710571 | +14.10576 | −14.10800 | 59.48620 | 133.62470 |
| n=8 away | +0.6399254 | +0.1492582 | +0.6890661 | −0.8108804 | 782.45100 | 393.18820 |
| n=16 away | −0.0192892 | −0.0002979 | +0.03750857 | −0.02053856 | 76.85426 | 1682.72000 |

**範圍限定的結論：**

- 壓合工況原始 RF3 殘差在反轉後仍是 n=8 約 −44.47 N、n=16 約 −17.87 N，沒有形成全域反力平衡 oracle。反轉 slave 側後，CFz 符號改變不能被當成兩側獨立實測平衡證據。
- 接觸面積及分離時非零接觸力對 slave/master 非常敏感；n=16 away 反轉面積約為原配對的 21.9 倍。這是受限演算法／離散數值敏感度，不能由 `CFN` 與幾何名目重疊面積直接推出真實帷幕接觸容量。
- n=8／16 的已知 ±1 N 無接觸節點力對照通過，但只限該負向控制；既不能外推至帶 contact springs 的內部節點力，也不能證明缺失的反力全由 MPC 引起。
- CalculiX 文件將 `RF` 定義為節點外力（含約束反力及 CLOAD/DLOAD），並明示不計算由 MPC 產生的作用力；`CONTACT PRINT` 的 `CF/CFN` 僅代表指定 slave 接觸面力。官方文獻定義見 [*NODE FILE](https://feacluster.com/CalculiX/ccx_2.18/doc/ccx/node305.html)、[*CONTACT PRINT](https://feacluster.com/CalculiX/ccx_2.18/doc/ccx/node237.html)。這是 2.18 公開文件的語意參考，2.21 本算例行為需以實測及 2.21 原始碼核對，不能推定完全相同。
- [CalculiX upstream issue #97](https://github.com/Dhondtguido/CalculiX/issues/97) 已回報殼與接觸同時存在時外力觀測異常；2026 年 [RR 輸出討論](https://calculix.discourse.group/t/output-reaction-forces-only/3809?page=3) 也指出 expanded shell 的 FRD 力輸出存在未解議題。均只是獨立問題線索，尚未能認定是 PR #131 的同一根因，更不能套用非正式修補作正式反力。
- **停在證據門**：`CONTACT_NOT_ADMITTED`、`MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED`、`ENGINEERING_ACCEPTANCE_NOT_ADMITTED`；原有 `check_u_rib_base_contact.py` RF3 FAIL 不改，PR 不合併。若要突破，優先建立可追溯的接觸力 ownership、獨立切面力或實體單元對照，而非改容差／任意補算 CFN。


## 2.21 原始碼追蹤與端部反力分區（2026-10-17）

### 來源與完整性

本節使用已提供的 Debian `calculix-ccx_2.21.orig.tar.bz2`，依 `calculix-ccx_2.21-1.dsc.txt` 的 SHA-256 核對原始封存檔與 Debian 補丁，不使用不明版本的 GitHub `master` 替代 2.21；未獨立執行 OpenPGP 簽章驗證。

- 原始 tarball SHA-256：`51d229aee320cf685216d360f7c04f9a57af0148fbe840483a964c86c315da82`；Debian 補丁 tarball SHA-256：`6c2a934b66491c9e916cbf6328167d417f7e985b380e200facf92c3e953d255f`。
- 原始 `ccx_2.21/src/resultsforc.c` SHA-256：`d1de9498ac715a7f08da0b7beba3c92c7c2f1030c85c37122d2708f2f480cad0`；`printoutcontact.f` SHA-256：`2c4d1da25da0ba5f3157a7d591bf262c388fc652dae05b4de0da2c4a36954c01`。
- `printoutnode.f` SHA-256：`c0bbe37ece5ae10faf2ba93113767361fb3dd4f1225e5c2f082cdfad85889141`；`gen3dforc.f` SHA-256：`513af06251a29e4d64a719d05f7789714bfb5ee95670829ab8ccb7f88ea6fa4d`。
- 對應本案結果：PR #131 head `e60277e9ed30d097e38303bfb1030952a939a208`、CalculiX run `38982263432`、artifact `12081678042`，ZIP SHA-256：`86b9ae2a790d4b89d2b3f356d979c6dc964e43902d290ab2868df138936b3c4e`。

### 原始碼可直接支持的觀測意義

1. `printoutcontact.f` 第 70–91、175–211 行：以選定 slave 面的接觸元素／積分點累加 `springarea(1,igauss)`，計算接觸應力乘以該面積權重所形成的 `CF` 與力矩。程式輸出的 `area` 是這些接觸權重的總和，**不是獨立幾何接觸面積測量或植釘受力面積**。
2. `printoutcontact.f` 第 245–280 行：接觸面積為 0 時，平均位置／平均法向仍以 `area` 當除數；這能解釋本算例無作用接觸時的 `NaN` 輸出結構，但不能因此放寬其他非有限結果的拒絕條件。
3. `resultsforc.c` 第 34–59、75–118 行：為內力／系統向量計算，暫時移除 MPC 對節點內力向量的貢獻，並依係數恢復至 `fn`。這些作業是求解器內部力與 MPC bookkeeping；`printoutnode.f` 第 94–110 行列印 `fn` 的 `RF` 欄位，並不能僅從這些語句推論已取得完整 MPC 約束反力，亦不能當作任意 `fmpc` 補償力獲得物理 admission。
4. `gen3dforc.f` 第 22–29、715 行起處理殼／梁節點集中載重及 expanded-node 對應，顯示這類單元的輸出 ownership 需分開確認；本次尚未以獨立物理或反力重建 oracle 證實缺口來源。

### 原始 RF3 的 U 肋截面位置分區

使用上述 exact-head artifact 的原配對 `toward` `.dat` 最終時間 `RIB_END_RF`，並使用同一網格互換配對 `.inp` 中**未修改的節點幾何**，按各節點 Z 座標分區。n=8／16 均各包含左右端合計 18 節點；以下單位 N：

| Z 位置 | n=8 | n=16 |
| --- | ---: | ---: |
| 底部中面 3.0 mm | −54.2592060 | −26.5812218 |
| 側壁中面 26.5 mm | +49.6732200 | +25.1760130 |
| 側壁頂部 50.0 mm | −54.2602300 | −30.5669940 |
| **直接加總** | **−58.8462160** | **−31.9722028** |

分區加總與同次診斷 JSON 的 `RIB_END_RF.sum_rf3_n` 相同；這是依原始座標與已列印反力進行的重分組，**不是獨立外力平衡或 MPC 重建**。正負交錯及網格差異說明 raw RF3 不能代表單一接觸傳力或中央單排植釘承載需求，也不能把任一區的數值任意抵銷為已驗證反力。

### 工程判斷與後續研究界線

上述原始碼資訊解釋 `CF`／輸出面積的計算路徑，以及零接觸面積的 `NaN`，但仍**不能判定**壓合時 n=8 約 −44.4375 N、n=16 約 −17.8664 N 的 raw 全域反力缺口究竟來自 MPC、接觸元素外力、殼展開後的映射或多項交互因素。下一步需要能明確分辨作用側與傳力的獨立切面力、可信實體單元對照或版本核對的最小診斷；在此以前維持 `CONTACT_NOT_ADMITTED`／`MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED`／`ENGINEERING_ACCEPTANCE_NOT_ADMITTED`，不更改現有 `OPEN_U_CONTACT_RF_GLOBAL_Z_IMBALANCE` fail-closed 門，也不合併 PR #131。


## 無殼展開 C3D8 對照（已取得實際求解，僅反力數值觀測）

為隔離原本開口 U 肋 S8R 殼展開及內部 MPC 的影響，新增獨立節點的 C3D8 實體鋁板與 U 型肋 synthetic 對照（網格 n=8／16、toward／away／unlinked）。板件為 1200×300×3 mm，實體 U 肋截面外寬 50 mm、肋底 3 mm、兩側壁 3 mm、實體高度 50 mm，板上表面與肋底面重合於 Z=1.5 mm；無植釘、無摩擦、人工 E=69000 MPa、ν=0.33、penalty=100000。僅做觀察，不宣稱幾何、網格與 S8R 完全等價。

本地已針對源碼測試元素數、節點不共用、接觸面、實體總體積及六組 deck scope；**2 項 deterministic tests PASS**。本地沒有 ccx 與必備 SPOOLES 環境，因此 **實際求解 NOT_RUN**。Workflow 加入六組隔離執行，原物理驗收 `check_u_rib_base_contact.py` 維持 fail-closed，並將輸入／DAT／STA／FRD 一併保留至 CI artifact。只在 exact-head real CCX 結果出現後，才決定是否需獨立反力解析檢查；若求解失敗不得將「C3D8 也無法平衡」視為已成立。


### 真實 C3D8 求解與獨立三集合 RF3 複算（已取得）

Exact-head `5c4a4ae847719fa49a936ed92b83b31b7f647efd`；CI `39010749089`，artifact `12092962247`；下載 ZIP SHA-256 `1d41f9ece682d52cfd9bf3e0b8e5acd78020b70d7526e2293c061b588c811e1c` 與 GitHub artifact digest 一致。六組 `.inp/.dat/.sta/.frd` 已保存；使用最終時間 1.0 的三個節點 RF3 集合，由原始 `.dat` 及實際 `.inp` NSET 分別重算：

| 網格／工況 | PLATE_EDGE_RF (N) | RIB_END_RF (N) | CENTER_RF (N) | 三集合合計 (N) |
| --- | ---: | ---: | ---: | ---: |
| n=8 toward | −422.6182400 | −28.8000490 | +451.4181000 | −0.000189000 |
| n=8 away | +424.0204828 | −0.9179164 | −423.1026000 | −0.000033625 |
| n=8 unlinked | −423.1023108 | 0 | +423.1023000 | −0.000010800 |
| n=16 toward | −116.3491909 | −20.1105400 | +136.4597300 | −0.000000932 |
| n=16 away | +121.2229734 | −4.7051689 | −116.5178100 | −0.000005520 |
| n=16 unlinked | −116.5104179 | 0 | +116.5104200 | +0.000002148 |

受限觀測結論：六組實體模型的 raw RF3 合計都小於 0.0002 N（該界線只用於表述此合成數值觀測，不是新工程允收門）。原配對 `toward` 的奴面 CFz 為 n=8 +28.79987 N、n=16 +20.11054 N，與各自 U 肋端 RF3 的負號相符到列印精度；**同一求解器兩組輸出的一致性不是獨立物理解析 oracle**。

重要反例：`away` 位移只是中心點向相反方向移動，未證明全部板肋界面皆張開；n=8／16 仍分別有約 +0.9179165／+4.705169 N 的 CFz。這兩組不能被標成 separation PASS，也不能把此數值當實物拉力、摩擦或植釘反力。

C3D8 模型的接觸面積、C3D8 實體截面局部剛度與 S8R 殼截面之間不具嚴格同一離散等價性，因此只能得到 **solid raw RF3 balance observed / shell raw RF3 unbalanced** 的差異證據，不能排除幾何／網格／接觸離散共同因素，更不能據此確證 MPC 單一根因。

既有 `check_u_rib_base_contact.py` 的 `OPEN_U_CONTACT_RF_GLOBAL_Z_IMBALANCE_-44.4374645` 仍原樣 FAIL，PR 未具合併資格。下一個實質工作是建立受控的殼展開傳力或真正完全張開的獨立幾何控制，再驗證 active-contact 的作用側與支承力學 ownership。仍維持 `CONTACT_NOT_ADMITTED / MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED / ENGINEERING_ACCEPTANCE_NOT_ADMITTED`。
