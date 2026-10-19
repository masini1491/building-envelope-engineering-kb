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

## 實體 C3D8 完全分離控制與殼體 S8R 全原始節點排查（2026-10-17；受限實測）

### 實體 C3D8 明確初始間隙：無作用接觸的兩個觀測通道

在上述 C3D8 板／肋合成模型，將**整組實體 U 肋**上移人工 0.1 mm，仍保持鋁板中心 −0.02 mm 的位移控制與原本的接觸 pair；不添加植釘、摩擦、實際接觸剛度或新的邊界條件。

- 第一個同次求解觀測通道：`CONTACT PRINT` 的接觸面積與 CF 均為零，n=8／16 全域 raw RF3 殘差分別為 +0.0000108／−0.000002148 N。
- 第二個不使用 `CONTACT PRINT` 計算間隙的通道：依 exact-deck `.inp` 原始座標和 `.frd` 最終位移重建**全板最高 Z 與全肋最低 Z 的嚴格垂直包絡間隙**，n=8 為 0.0999552 mm、n=16 為 0.0999462 mm，皆正值；此控制組兩實體的變形後 Z 包絡完全分離。
- Exact PR head `c525e5e332d66998f55a52c70f2325cbe7fd11ed`；真實 CalculiX 2.21 CI `39026212648`、artifact `12098472424`，ZIP SHA-256 `ce951d0d6217f1a1d565a38da6d0a4ab721491a9cab44adce61503e8238b9c2a`；檢查器與其 5 項負向測試已於該 run 通過。完整 CI 結果仍因既有 S8R 接觸 RF3 門而 FAILURE。
- 以上僅支持本控制的 `INACTIVE_CONTACT_OBSERVED_FOR_CLEARANCE_CONTROL`；不能將原始 `away` 視為完全分離，也不能提升 C3D8 到 S8R、植釘、接觸容量或一般工程 admission。

### 全部 S8R 原始殼節點 RF3：失衡無法由漏列自由原始節點解釋

在原 `toward` S8R 工況僅增加 `ALL_ORIGINAL_RF` 的 `*NODE PRINT`，不改接觸幾何、材性、拘束、荷載、網格或原先 fail-closed 驗收。比較全部**原始 `.inp` 節點**與原來 `PLATE_EDGE_RF`、`RIB_END_RF`、`CENTER_RF` 三集合，並檢查節點全集、集合互斥、各集合 RF 值一致及同次求解 provenance。

| 原始 S8R 節點觀測 | n=8 | n=16 |
| --- | ---: | ---: |
| 全部原始節點數 | 346 | 666 |
| 三個已列印節點集合聯集 | 83 | 115 |
| 其餘原始節點數 | 263 | 551 |
| 其餘原始節點 RF3 合計 (N) | +2.3712253×10⁻¹⁰ | −5.3182375×10⁻¹¹ |
| 其餘節點最大單點 `abs(RF3)` (N) | 3.662528×10⁻¹⁰ | 3.024885×10⁻¹⁰ |
| 三集合 RF3 合計 (N) | −44.43746453 | −17.86643756 |
| **全部原始節點 RF3 合計 (N)** | **−44.4374645298** | **−17.8664375601** |
| 同次 slave CFz (N) | +14.40875 | +14.10576 |

- Exact PR head：`ca787748148080cfbf162a7b0fce49e5236e7ada`；CalculiX 2.21 CI run `39027520751`；artifact `12099405754`，ZIP SHA-256 `2491a1dadd84ff2fa7ad1df9b7cf82846e3b520c4b42f170374fcd8d28140aa9`。JSON 指向的 n=8／16 各 `.inp/.dat/.sta/.frd`，共 8 檔 SHA-256 已再次獨立重算比對 **8/8 一致**，節點 partition 與總力複算一致。新三項 deterministic tests 在 real CI 內 PASS，Repository CI `39027520702` SUCCESS。
- **界限內結論**：原先壓合工況 raw RF3 失衡，並非遺漏加總其他**原始殼節點**的 RF3 所致。印出的自由原始節點 RF3 近零，不能靠將原始節點列印範圍擴大來恢復平衡。
- **不能推論**：原始節點集合不等於殼厚度展開後的全部內部節點，也不等於整個接觸／MPC system 的完整廣義力。CalculiX 的 `RF` 輸出含其定義內的節點外力，不可視作單獨的支承反力 oracle；不可以將 `CFz` 直接加到 raw RF3 人為補足。本次仍**不能證實**缺口唯一由 MPC、接觸元素或輸出映射造成。
- 原 S8R 檢查器仍報 `OPEN_U_CONTACT_RF_GLOBAL_Z_IMBALANCE_-44.4374645`，CalculiX CI 因此 FAILURE 且 PR #131 **OPEN／UNMERGED**。`CONTACT_NOT_ADMITTED`、`MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED`、`ENGINEERING_ACCEPTANCE_NOT_ADMITTED` 全部維持。

**下一個值得做的最小工作**：使用已版本核對的 CalculiX 2.21 原始碼，以源碼 ownership tracing 界定 `resultsforc`／殼展開／contact spring 在內部節點之作用力保存、分攤與輸出邊界；若需要診斷插樁，僅在隔離研究環境針對相同 2.21 編譯與未修改版本作可重播比較，先形成獨立作用側／平衡 oracle，不能藉修改門檻或推出新的實際設計容量跳過驗證。

## 已驗證的 MPC 權重力分配反例（CalculiX 2.21 原始碼隔離執行）

在未改寫的 CalculiX 2.21 `resultsforc.c` 上，以獨立 C harness 提供人工 `nactdof`、`ipompc`、`nodempc`、`coefmpc` 與 `fn`，實際編譯並執行 `resultsforc()`；本研究不需要也不執行完整的 ccx 求解器。原始 Debian tarball `calculix-ccx_2.21.orig.tar.bz2` 的 SHA-256 為 `51d229aee320cf685216d360f7c04f9a57af0148fbe840483a964c86c315da82`，其中 `resultsforc.c` 與 `CalculiX.h` 也逐檔驗證 SHA-256；僅在執行時使用外部原版原始碼，**不把 GPL 原始碼複製進 KB Repository**。

- 既有四種兩節點情境：MPC 使用／不使用、系統內力向量輸出開關、非零獨立節點力，查驗 `fmpc`、回填的 `fn` 與 reduced active-DOF `f` 不可混淆。
- 新增三組非單位係數情境：`(1,-2,0)`、`(1,-0.6,-0.4)` 與 `(2,-1,-1)`，驗證 dependent／independent DOF 權重、廣義約束乘數、系統內力與 `fn` 的恢復。
- 新增兩組**彼此不相交**的 MPC 聯合測試，獨立檢查兩個乘數、兩個 active-DOF 系統內力，並拒絕原始 `fn` 未恢復的狀態；不包含 chained-dependent MPC、`MEANROT`／`RIGID` 等特殊拓撲及實體接觸。
- **診斷反例**：某個合成線性 MPC 的係數 `(1,-2)` 與原始 `fn=(+10,-20)` N，使原始兩節點 `fn` 直接相加為 −10 N，但該 MPC 消去後的 reduced active-DOF `f=0` N。兩種合計的對象不同；此反例只能說明非平移等效 MPC 下，原始 Z 向力直接相加未必是可直接採用的完整平衡 oracle。**不代表真實模型可以把 −44.4374645／−17.8664376 N 差額判成已平衡**。
- 本地 exact-source 執行：八組 synthetic harness scenarios **8/8 PASS**；原有五項 archive／失效輸入契約測試 **5/5 PASS**；工具輸出維持 `CCX221_MPC_FORCE_BOOKKEEPING_ISOLATED_PASS_NOT_ENGINEERING_ORACLE`。使用 `python ccx221_resultsforc_mpc_audit.py /path/to/calculix-ccx_2.21.orig.tar.bz2` 重播；結果必須包含 `full_calculix_build=NOT_EXECUTED` 與 `actual_s8r_contact_mpc_balance=NOT_ESTABLISHED`。
- **下一個缺口**仍然是：從實際 S8R 接觸求解器精確地取得 expanded-node／contact-spring internal forces、MPC 自由度與有效外荷載，建立可獨立重建的作用側和完整平衡。單獨 `resultsforc()` 的人工輸入測試不是 S8R 物理驗收；`OPEN_U_CONTACT_RF_GLOBAL_Z_IMBALANCE` 保持原樣，PR #131 不合併，`ENGINEERING_ACCEPTANCE_NOT_ADMITTED` 不變。

## 殼體反力檔案輸出映射 A/B 實測（2026-10-17；僅輸出差異）

在相同 S8R `toward` 合成模型，A 為只要求 `*NODE FILE U`，B 唯一改動為 `*NODE FILE U,RF`，原來 `*NODE PRINT`、網格、邊界、接觸及位移載重皆不變。Exact PR head `7621993642f836c6509d783495675676633bd290`；CalculiX 2.21 CI `39033608972`，artifact `12101362777`，ZIP SHA-256 `2653c8e8d9eb41cc5a8135dde0f5a92649c4d23fd959f9f1ba729cd55bc104a1`；Repository CI `39033609015` SUCCESS。兩組 `.dat`／`.sta` 各自 A/B **位元組完全相同**，僅 `.frd` 因加入 FORCE 輸出而不同。原 `.dat` 三集合與全部原始節點 RF3 的結果未變。

| 同一時間 1.0 之輸出觀測 | n=8 | n=16 |
| --- | ---: | ---: |
| 原始殼節點 raw RF3 合計（A、B 完全相同；N） | −44.4374645298 | −17.8664375601 |
| B 的最終 `.frd` `FORC` 記錄數 | 904 | 1736 |
| B 的 `.frd` 記錄節點 ID 最小 | 347 | 667 |
| B 的最終 `.frd` 記錄 F3 合計（N） | −44.4375782997 | −17.8675579870 |
| B `.frd` F3 減 B `.dat` raw RF3（N） | 約 −0.00011377 | 約 −0.00112043 |

檢查界線：上表 `.frd` 數值是由 `FORC` 最後一個時間區塊中列印的**節點記錄**求和，並不涵蓋全部展開節點或求解器的獨立 generalized force；不能以「F3 接近 raw RF3」宣稱完整 MPC／接觸反力已平衡。特別是 `.frd` 的 ID 高於原始 `.inp` 節點範圍，該區塊不能與原始節點集合一一對應，兩個總和不能當同一物理量精確相減後解讀。

原始碼 2.21 `printout.f` 的 RF 設定會使用 `map3dto1d2d(...,iforce=1)`；`map3dto1d2d.f` 對力分支採展開節點力加總，而不是對位移的厚度平均。此源碼路徑不足以憑空宣稱 S8R 所有內部節點、MPC 與接觸負載已恢復完整平衡。

**結論**：僅改 RF 檔案輸出不會修復或掩蓋既有的 `OPEN_U_CONTACT_RF_GLOBAL_Z_IMBALANCE`。本受限研究仍為 `MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED`／`ENGINEERING_ACCEPTANCE_NOT_ADMITTED`，PR #131 維持 OPEN。下一步應追查原版 2.21 真正的元素內力與約束自由度，而非新增相同的 RF 輸出選項實驗。

## 殼體反力檔（FRD）幾何／位移／反力同集合覆核與接觸力歸屬路徑（2026-10-18；仍未通過物理門）

### 精確提交（Exact-head）CI 與原始證據完整性

PR #131 的 test-only 修正 head `da21e005dde4f9098405c7408019a46b15d8d387`，Repository CI `39054940761` SUCCESS；實際 CalculiX 2.21 CI `39054940762` FAILURE。CI 原始 log 中，`test_probe_s8r_rf_output_projection.py` **3/3 PASS**，已排除前一個 head 的固定欄寬 NaN 負向測試失敗；後續真正停止在既有 `check_u_rib_base_contact.py` 的 `OPEN_U_CONTACT_RF_GLOBAL_Z_IMBALANCE_-44.4374645`。不修改、跳過或提高該物理門檻。

同次 CalculiX artifact `12109655758` 的 ZIP SHA-256，經獨立下載、位元組重算，為 `beea8fb590dbf647565517a240f63f3f51d947e2549c6f0458a7a89ce3468fa8`，與 GitHub digest 一致。對 artifact 中 n=8／16 各 A/B 的 `.inp/.dat/.sta/.frd` **16/16 份 SHA-256**，逐一與 `u_s8r_rf_projection_observations.json` 原紀錄比對一致；A/B 各自 `.dat` 與 `.sta` 均位元組相同。A/B `.inp` 比對確認只在 `*NODE FILE,OUTPUT=3D` 增加 `RF`；`.sta` 的最後時間都是 1.0。本獨立重算以 ZIP 原始 bytes 為輸入，不等於第二次獨立求解。

### 輸出幾何節點集合（FRD）的獨立交叉檢查

對同一 ZIP 的 B 組 `.frd`，不以既有 `probe_s8r_rf_output_projection.py` 的 JSON 宣稱代替實際讀取：分別解析 `2C` 幾何節點記錄、最後時間 1.0 的 `DISP` 與 `FORC` 節點 ID，核對筆數、無重複及**三者 ID 集合逐一相等**。

| 本次實際 FRD（B／toward） | n=8 | n=16 |
| --- | ---: | ---: |
| 原始 `.inp` 殼節點數 | 346 | 666 |
| `2C` 幾何節點數 | 904 | 1736 |
| 最後 `DISP` 節點數 | 904 | 1736 |
| 最後 `FORC` 節點數 | 904 | 1736 |
| 三種 FRD 節點 ID 集合 | 完全相等 | 完全相等 |
| FRD 節點 ID 範圍 | 347–1758 | 667–3390 |
| 該範圍內未出現在 FRD 的 ID 數 | 508 | 988 |
| 最後 `FORC` F3 列印值合計（N） | −44.4375782997 | −17.8675579870 |
| 原始全部殼節點 `.dat` RF3 合計（N） | −44.4374645298 | −17.8664375601 |

**只可得出的結論**：本次 `FORC` 並未漏列**同一 FRD 已輸出的 `2C` 幾何節點**；原始 `.inp` 殼節點不是同一組觀測 ID。FRD 範圍內的空號不能自行解讀為確實存在、應計反力的內部自由度；`2C` 集合完整也不能證明已列出求解器全部 generated nodes、contact-spring force、MPC generalized forces 或 external load ownership。**此表不是完整求解器平衡 oracle。**

### 版本核對的 CalculiX 2.21 力向量路徑

以 Debian 2.21 原始封存檔 `calculix-ccx_2.21.orig.tar.bz2` 的 SHA-256 `51d229aee320cf685216d360f7c04f9a57af0148fbe840483a964c86c315da82`，在 Repository 外隔離解壓、直接追查：

- `gen3delem.f` 269–281、369–372 行：S8R 的 2D→3D 展開使用 `gen3dfrom2d`，元素改為 `C3D20RL`。展開過程包含 additional MPC，不能視作原始殼節點直接等於有效方程自由度。
- `resultsmech.f` 389–455 行：接觸 spring 分支經 `springforc_n2f`／`springforc_f2f` 求得元素節點力 `fnl`，隨後逐節點累加進 `fn`。在 `springforc_f2f.f` 424–437 行，可見 master 與 slave 分別以負／正形狀函數權重配置局部接觸力。這是**程式碼路徑**，尚未取得本案真實運算的兩側完整數值和。
- `results.c` 241–258、401–414 行：先聚合各 thread 的 `fn`，再由 `resultsforc` 依實際 `nactdof`／MPC 拆分 active system force 與回填 `fn`。`resultsforc.c` 34–118 行的 `f`、`fmpc`、`fn` 不應混為單一可直接相加的反力。
- `printout.f` 84–92 行及 `map3dto1d2d.f` 538–572、650–657 行：RF 輸出經 `iforce=1` 的 expanded→2D force sum 與 node marker 去重。它是映射輸出，不等同 independent active-DOF 平衡驗算。

以上僅能識別潛在的觀測邊界：**局部接觸雙側力 → 全部 expanded-node `fn` → MPC 分離／有效 `f` → RF 映射／列印**。尚未證實本案實際選用的 contact branch、每個接觸積分點正負作用側、各 MPC 條款或有效外荷載的完整數值歸屬；不得把源碼上的正負權重直接宣稱為求解結果已平衡。原版 GPL 原始碼未加入公開 KB。

**下一個可檢驗工作**：如需追究真實 S8R 失衡根因，在隔離、同版本求解環境建立最小 read-only 診斷插樁，分別輸出 `springforc_* ` 的 master／slave 局部 F3 加總、`resultsmech` 聚合後 expanded `fn`、`resultsforc` 處理前後的 `fn/f/fmpc` 與對應 `nactdof/ipompc/nodempc/coefmpc` term identity；使用同版未修改 solver、相同 `.inp`、`.dat`、`.sta` 及 independent external-force ledger 對照。**尚未實際插樁／執行此測試，獨立有效自由度平衡仍未建立**。

狀態維持 `CONTACT_NOT_ADMITTED`／`MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED`／`ENGINEERING_ACCEPTANCE_NOT_ADMITTED`；PR #131 保持 OPEN／UNMERGED，不修改物理驗收門檻，不將合成研究外推實際鋁植釘設計容量。

### 隔離診斷插樁重播準備（未進行完整求解）

最小診斷工具：`tests/fea_benchmark/envelope_panels/ccx221_s8r_force_instrument.py`。使用者授權限於隔離研究；工具僅在 Repository **外部**、已驗證 SHA-256 `51d229aee320cf685216d360f7c04f9a57af0148fbe840483a964c86c315da82` 的原始 CalculiX 2.21 解壓目錄修改 `src/results.c` 與 `src/resultsmech.f`。**不得**把修改後 GPL 原始碼提交至公開 KB、不得將此版本視作正式求解器。

本次以未安裝 SPOOLES 的本地 GCC／gfortran，分別將插樁後兩檔編譯成物件檔，確認 `-DARCH=Linux -DSPOOLES -DARPACK -DMATRIXSTORAGE` 的 C 與 `-fallow-argument-mismatch` 的 Fortran 來源可編譯；**完整 ccx link 與真實模型求解皆 NOT_RUN**。前述插樁對 `fn`、`f`、`fmpc`、MPC terms及接觸元素 `fnl` 的檔案輸出，是供下一輪研究的 instrumentation candidate；沒有獨立同版原版／插樁版 `.dat/.sta` 檢查前不得進行物理詮釋。輸出會因非預設環境變數 `KB_CCX_LEDGER` 而啟用，接觸 spring 分支與 MPC terms 的覆蓋仍待實際求解證明。

重播前必須於**空白隔離工作目錄**驗證原始碼封存檔 SHA-256、確認診斷 patch 只改上述兩檔，對原版及插樁版使用相同 toolchain／輸入 `.inp`、單 CPU，先要求 `.dat/.sta` 原始資料一致並確認 trace 確有記錄，才分析接觸兩側／有效自由度。不要以 trace 存在、物件檔 PASS 或 raw FRD 的 FORC 合計推導完整 solver 反力平衡；既有 `OPEN_U_CONTACT_RF_GLOBAL_Z_IMBALANCE` 門維持 FAIL，PR #131 不合併。

## 隔離 A/B 求解首次完整通過與 MPC 力回填重播（2026-10-18；不代表工程平衡）

- PR #131 exact head `18b2c4221817243f561829d69774f3b9a24b3920`；隔離 workflow [run 39135858640](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/39135858640) **SUCCESS**；artifact `12140280193`，ZIP SHA-256 `905b92a2642085e87d3bd685f5b4151d4703585c4d718ac147e423e4a33ce872`，與 GitHub digest 一致。研究版本為同版 CalculiX 2.21-1 原版與只修改隔離 `results.c`／`resultsmech.f` 的插樁版。
- 真正完成原版及插樁版編譯、n=8 `toward` 求解；原版／插樁版的 `.inp/.dat/.sta` **逐位元組相同**（不是只比較數字）。`.inp` SHA-256 `e0360eed38d6708075200c499a870e38e79f120eaa88ff7427c497e7f0cef2cf`；`.dat` SHA-256 `51355577b2eea72bf19656a00ec73f292008804296b31128c261334ffc5d8043`；`.sta` SHA-256 `4b3c0f468070b0e0ad29d13e2ce30a49dfb72ae73432de88b391db1813cc9a95`。此 A/B 證明插樁未改變上述**輸出 bytes**，不是獨立工程平衡 oracle。
- `kb_force_ledger.tsv` SHA-256 `2dc6087367abe7f47d1ae62d03c1a212f1325ba2aff0d004e64b95095324b70e`；`kb_contact_ledger.tsv` SHA-256 `4cf6b8a4853e92afec823afb107c6522ebc399106db045bcbc8c3df11ba21b1a`。10 增量、每增量依序 `KB_EVENT P`／`Q`，最終時間 1.0，展開節點數 `1914`、MPC 數 `1238`。
- 最終增量（#10），接觸 spring 由元素 97、98、99 各輸出 16 筆 `fnl`；各自前 8／後 8 節點的 F3 合計分別為 `(+4.695122924, -4.695122924)`、`(+1.637494896, -1.637494896)`、`(+8.076132190, -8.076132190)` N，三個元素合計 `−1.33×10⁻¹⁵ N`，支持當前 trace 範圍內的雙側接觸作用反作用配對，**不代表接觸力大小已通過獨立絕對 oracle**。
- 最終 `resultsforc()` 前全部 expanded `fn` 的 F3 合計 `−2.9804104×10⁻¹² N`，後為 `−44.4374737211 N`；舊 `.dat` raw RF3 約 `−44.4374645 N`。這兩種觀測量不同，差值不可擅自用 CF／CFN 補抵，也不能把前者的零合計當成 reduced-system 平衡。
- 以同次 ledger 中記錄的 MPC `coefmpc`／`fmpc`／`nodempc` 資料、依固定 2.21 `resultsforc.c` 一般線性 MPC 消去與回填順序，在本地唯讀重播 10 個增量：Z 向 `fn` 逐值符合 `Q` trace；最大差異在原 trace 記錄精度下為 `0`。此重播只驗證**已記錄的 MPC 力回填／所有 Z 向節點力一致性**，沒有驗證求解方程的 active-DOF force balance，也不能證明缺口全是輸出映射造成。部分 X/Y MPC 回填具有特殊標記／不在上述有限範圍內，不推廣為三方向完整重建。
- **尚缺** `KB_ACTIVE` 有效自由度 `f` 的實測紀錄（此次 trace 中 0 筆）及獨立的位移／拘束／外荷載 ledger；也沒有完成 n=16 原版／插樁版求解。因此 `MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED` 與原本 `OPEN_U_CONTACT_RF_GLOBAL_Z_IMBALANCE` 的 FAIL-CLOSED 仍不變。

**後續最小步驟**：在隔離 A/B 插樁實際 `calcul_f` 為 1 的運算邊界擷取 reduced active-DOF `f`，並記錄其對應的外力與邊界／MPC ownership；先以 n=8 取得真正 active-DOF residual，再擴張 n=16。不修改物理驗收容差，不將本結果當成實際植釘／帷幕系統的設計認可，PR #131 保持 OPEN／UNMERGED。

## 雙網格內力與約束方程逐項覆核（2026-10-19）

隔離同版原版／插樁版 A/B：[run 39174714987](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/39174714987) **SUCCESS**，exact PR head `a5fe08526fd86f19d765b0e93e2a0ae98712d7b6`；artifact `12153418267`、ZIP SHA-256 `ed7584a2a1256b7f59b9f45e302d9927ff6284d41ddf00a9eda9295e2f7e751f`，獨立下載重算與 GitHub digest 一致。此 run 保留 n=8 及 n=16 的 A/B 同版求解，兩網格各自 `.inp/.dat/.sta` **三檔位元組完全一致**，不是跨網格比較，也不是由舊 CI 推估。

| 來自本次 ZIP 的真實求解／trace | n=8 | n=16 |
| --- | ---: | ---: |
| `.inp` SHA-256 | `e0360eed38d6708075200c499a870e38e79f120eaa88ff7427c497e7f0cef2cf` | `90becf2d6530482a88991f7e038ee63162f52ec41e9943ddfb16be612c7ee6cf` |
| `.dat` SHA-256 | `51355577b2eea72bf19656a00ec73f292008804296b31128c261334ffc5d8043` | `0afd51cf40a63be7bd837b684fcd7bbe9c6fc93d530922cd62bc8b67a1efd35d` |
| `.sta` SHA-256 | `4b3c0f468070b0e0ad29d13e2ce30a49dfb72ae73432de88b391db1813cc9a95` | `3aaf52ec7219ac3effac194b302b835c711c5389f3bb081ee39d52e84fd49f1a` |
| 展開節點 `nk` | 1914 | 3610 |
| MPC 條數 | 1238 | 2070 |
| 最終有效方程數 | 1904 | 3936 |
| 最終 reduced-system 迭代觀測數 | 6 | 5 |
| 最終最大絕對 `b`（求解器方程力單位） | 0.000363184958 | 0.00000110015236 |
| 最終 `fext` 非零有效方程筆數 | 0 | 0 |
| 第 10 增量、MPC 前 `fn` F3 合計（N） | −2.9804×10⁻¹² | −9.7395×10⁻¹³ |
| 同一增量、MPC 後 `fn` F3 合計（N） | −44.4374737211 | −17.8664384417 |
| 最終接觸 spring 元素數 | 3 | 7 |
| 接觸每元素雙側 X／Y／Z 淨力最大絕對值（N） | 1.78×10⁻¹⁵ | 8.88×10⁻¹⁶ |

雙網格 `*.inp` 皆有一組 `*CONTACT PAIR` 與 displacement boundary，沒有 `*CLOAD` 或 `*DLOAD`。`nonlingeo.c` 的 reduced `fext` 全零與此一致；**但指定非零位移的反力不包含在「自由有效方程外力全零」這個敘述內**，不可據此宣稱全部 support reactions = 0。

獨立 Python 唯讀解析原始 ZIP：檢查 10 個 `P/Q` pair 覆蓋、每組 MPC term 順序與數量、逐項有限性、每元素 16 筆接觸力、每增量 X/Y/Z 兩側合力、每個 reduced 方程 ID 不重複及 `b=fext-f` 一致；對 **n=8／16 各 10 個增量**，以原版 2.21 `resultsforc.c` 的一般 MPC 消去與回填順序重播 Z 向節點力，與實測 `Q` trace 最大絕對差異均為 **0（按原始紀錄雙精度）**。這是 solver trace／MPC 轉換之**同源數據一致性與源碼回放**，**不是額外獨立求解**。本地驗證器及 10 項含 NaN、缺筆、重複方程、修改 digest、接觸節點覆蓋的負向測試已執行 PASS；此輪所述本地檢查不自動代表 CI 已包含該驗證器。

目前可確認：力輸出差異與 MPC 回填的演算法路徑一致；接觸 spring 的雙側對向力互抵；本工況有效方程上的 `fext` 為零且最終 `b` 非零但小。**尚未取得**逐個原始支承／指定位移 DOF 對應的獨立反力帳、全域 MPC constraint dual force 映射，以及未受約束實體力平衡的外部 oracle。因此即使減少錯誤觀測的疑慮，也不可把 `OPEN_U_CONTACT_RF_GLOBAL_Z_IMBALANCE` 門直接改成 PASS；不得藉 `CF/CFN` 補零或宣稱可用於實際植釘容量。

下一步只針對 **SPC／prescribed displacement owner + exact MPC dual vector → 原始及 expanded node 的一致反力映射** 設計新的觀測切面。先核對 `nodeboun/ndirboun/xbounact` 及 mortar branch 對應，建立獨立外部力 ledger，再計算支持／指定位置的反力；所有物理 admission 仍維持 `CONTACT_NOT_ADMITTED`、`MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED`、`ENGINEERING_ACCEPTANCE_NOT_ADMITTED`，PR #131 繼續 OPEN／UNMERGED。

## 約束力歸屬：MPC 消去／回填依類型驗證（2026-10-19，非物理平衡 oracle）

同版 CalculiX 2.21 PR head `a65357fed2af6c3a5d9537033b4494358b63f42e` 的 [Actions #39180408726](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/39180408726) 為 **SUCCESS**，artifact ID `12155483309`，ZIP SHA-256 `c2a1f10fda57803b7e6241ba842e31ea41bef84b2fe9936c9dfec950be7d5491`。再次驗證 n=8／n=16 原版與插樁版 `.inp/.dat/.sta` 位元組一致，且 SPC 旋轉方向 4～6 已正確歸為 `KB_SPC_ROT_UNMAPPED`（n=8：246 筆；n=16：342 筆），不再作 invalid translational index。

由這份固定 artifact 的最後 `P/Q` 力向量和 `KB_MPC/KB_TERM`，照原版 `resultsforc.c` 的先消去、後回填順序逐筆唯讀重播；**總 Z 向變動依 MPC 類別拆解**：

| 演算法類型 | n=8 全域 `fn3` 變動 (N) | n=16 全域 `fn3` 變動 (N) |
| --- | ---: | ---: |
| `KNOT1` | 約 0 | 約 0 |
| 無標籤 MPC（ledger 的空白 `labmpc`） | −4.65100614066 | +1.13019292126 |
| `MEANROTBS` | −39.78646758043 | −18.99663136300 |
| 三類合計 | **−44.43747372109** | **−17.86643844174** |
| 原始 `.dat` `ALL_ORIGINAL_RF` F3 合計 | −44.43746452976 | −17.86643756005 |
| 原始列印值與重播總和差（絕對值） | 9.19×10⁻⁶ | 8.82×10⁻⁷ |

這是**來源同源的程式演算法回放／輸出觀測帳**：最後一步以前 `fn3` 全域內力合計接近零，後續 `MEANROTBS` 與無標籤約束回填解釋列印 RF3 的非零合計；不代表真實支承反力應加減上述數值，也不代表 force/moment 六分量已閉合。n=8／n=16 殼轉動 SPC 仍 **UNMAPPED**，不得以其 `KB_SPC` 平移 F3 合計作為完整原始殼支承反力。

新增唯讀重播入口 `tests/fea_benchmark/envelope_panels/check_ccx221_mpc_restore.py` 與合成 cascade／負向測試 `test_check_ccx221_mpc_restore.py`。本地已針對固定 ZIP 雙網格逐增量重播：10/10 各網格最後力結果一致，與原始 `.dat` 比對及合成負向測試 PASS；**只確認診斷一致性**，不更動物理驗收門。需要外部原始殼 SPC 與擴展實體 MPC 的功共軛／力矩對應之**獨立**數值 oracle，不能把同源重播誤寫為 independent support reaction validation。

維持 `OPEN_U_CONTACT_RF_GLOBAL_Z_IMBALANCE` FAIL-CLOSED、`CONTACT_NOT_ADMITTED`／`MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED`／`ENGINEERING_ACCEPTANCE_NOT_ADMITTED`，PR #131 繼續 OPEN／UNMERGED。

## 中心指定 Z 位移能量差分觀測（2026-10-19／限定中心反力，不含六分量驗收）

隔離研究 [GitHub Actions #39185949264](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/39185949264) **SUCCESS**，原版 source-pinned CalculiX 2.21（未插樁）分別對 n=8 與 n=16 的 5 組中心位移 `0.0198/0.0199/0.0200/0.0201/0.0202 mm` 真實求解，保留各 `.inp/.dat/.sta`。Artifact ID `12157943452`，ZIP SHA-256 `65a347dc30237fb9dc732815d70e5ba31b6de071567344581c23af0fde94681e` 已獨立下載校核一致；n=8 原始輸入 `e0360eed38d6708075200c499a870e38e79f120eaa88ff7427c497e7f0cef2cf`；n=16 `90becf2d6530482a88991f7e038ee63162f52ec41e9943ddfb16be612c7ee6cf`。測試只修改 center Z 位移及 `*EL PRINT ELSE`（分別 PLATE、RIB）與 `*CONTACT PRINT CELS` 的診斷輸出；幾何、接觸模型、材料、板邊與肋端固定條件不改。

`ELSE` 輸出之 PLATE＋RIB 內能與 `CELS` 接觸彈簧能量逐案例另列。當前直接採此三個列印合計作**候選觀測能量**，並比較能量中心差分 `[E(0.0200+h)-E(0.0200-h)]/(2h)`；並未宣告三項是普遍適用的無重複計入完整總勢能定義，亦非外部獨立物理求解器。

| 實測量 | n=8 | n=16 |
| --- | ---: | ---: |
| `h=0.0001 mm` 候選能量斜率 (N) | 20.5863000 | 19.95807045 |
| `h=0.0002 mm` 候選能量斜率 (N) | 20.5864250 | 19.95784546 |
| 基準 `u=0.0200 mm` 的 `.dat CENTER_RF` RF3 (N) | 20.58953 | 19.96088 |
| h=0.0001 斜率與中心 RF3 絕對差 (N) | 0.00323 | 0.00281 |
| h=0.0001 相對差 (%) | 0.01569 | 0.01408 |
| 基準 PLATE `ELSE` (N·mm) | 0.06425522 | 0.06105031 |
| 基準 RIB `ELSE` (N·mm) | 0.1416027 | 0.1385293 |
| 基準接觸 `CELS` (N·mm) | 0 | 2.045318×10⁻⁷ |

兩種 h 導出的中心功共軛斜率穩定，與原始 CENTER_RF 的約 20 N 反力相符。**僅此中心 Z 方向的比較得到可重播的交叉證據**，未測支承組逐項變分、力矩或任意 six-component balance。特別注意：n=8 `CELS=0` 但存在非零 contact force；不能因 `CELS=0` 假定 contact work 已全部被正確輸出，也不能直接以此能量差分取代工程接觸驗收。每次擾動是否保持同一接觸分支、接觸負功／雙重計數及完整能量 ownership 尚須獨立確認。

因此原先 `OPEN_U_CONTACT_RF_GLOBAL_Z_IMBALANCE` 仍 **FAIL-CLOSED**；`CONTACT_NOT_ADMITTED`、`MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED`、`ENGINEERING_ACCEPTANCE_NOT_ADMITTED` 均不改。下一步應測板邊／肋端群組功共軛擾動與獨立約束力矩／幾何虛功，包含接觸 active-set 變化和負向對照；此 run **不能**宣稱上述後續項目已完成。

## 支承群 Z 微擾與接觸分支不對稱（2026-10-19／限研究自由體力帳）

同版原版 CalculiX 2.21、18 個 source-pinned n=8/n=16 求解，[run 39188319636](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/39188319636) **SUCCESS**；artifact ID `12158619455`、ZIP SHA-256 `b3cddccfda6d05bd472298ff5e8410d2bff3815592edb01c212bad16b6268796`，獨立下載重算一致；manifest SHA-256 `f9d52a1b0f0063527e7596d3766a2a2da08ad2424d63837692dabe8c318a028b`。固定中心 Z=0.0200 mm，板邊、肋端原各固定；分別對板邊或肋端的**整組 Z 方向**添加 ±0.0001／±0.0002 mm 指定位移。各輸入僅更動受控指定位移與 `ELSE/CELS` 觀測，保留 1.0 最終增量與不同模型 SHA。

| 基準最後一步觀測，N | n=8 | n=16 |
| --- | ---: | ---: |
| `CENTER_RF` raw F3 | +20.589530 | +19.960880 |
| `PLATE_EDGE_RF` raw F3 | −6.18077853 | −5.85511476 |
| `RIB_END_RF` raw F3（**不認可作實體反力**） | −58.8462160 | −31.9722028 |
| 接觸面列印總 F3（依 U 肋受力約定） | +14.408750 | +14.105760 |
| 假定 U 肋除端部、接觸外無外加載重的**自由體推得**端部反力 | −14.408750 | −14.105760 |
| 中心＋板邊－接觸力，自由體殘差 | +0.00000147 | +0.00000524 |
| 原始 `ALL_ORIGINAL_RF` 總 F3 | −44.43746453 | −17.86643756 |

以上只是模型內**另一輸出通道的自由體力帳**，不是獨立實體反力 oracle。列印 `RIB_END_RF` 與自由體推得值的差異，與先前 MPC 回填 RF3 缺口一致，仍不得自行修補/解除原失衡門。

接觸分支對微擾方向明顯不對稱，例如 n=8 板邊 +0.0001 mm 時接觸面 F3 從 14.40875 跳至 50.75045 N，n=16 同方向跳至 130.9482 N；肋端 −0.0001 mm 時 n=8 約 52.87321 N、n=16 約 130.9584 N。對應反方向僅在 14 N 左右變化。這顯示**微擾跨過接觸組態變化**；不能把跨分支的正負能量中央差分當作光滑一致的支承反力。

固定 artifact 候選總能量（`ELSE(PLATE)+ELSE(RIB)+CELS`，尚未正式證明無雙重計數）在較少改變接觸分支的一側給出初步斜率：n=8 板邊 −向 −6.3798 N、肋端 ＋向 −14.1798 N；n=16 板邊 −向 −5.7660 N、肋端 ＋向 −14.1691 N（h=0.0001 mm）。這些只是**有限步長的單側研究觀測**，而非真正接觸一致切線、非認證支承反力；h=0.0002 mm 的差分仍具步長差異，不得視為收斂證明。

新增 `check_ccx221_support_fd.py` 為只讀 artifact verifier，要求 18 案例、輸入 SHA、最終 STA、原始位移/力節點覆蓋、能量與接觸列印有限性、自由體合計、舊 raw RF3 門 fail-closed，並輸出不同微擾方向的接觸分支不對稱摘要。這個 verifier 不證明接觸法則、完整旋轉功共軛或六分量平衡；獨立物理 admission 仍須額外證據。`CONTACT_NOT_ADMITTED`／`MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED`／`ENGINEERING_ACCEPTANCE_NOT_ADMITTED` 維持，PR #131 保持 OPEN／UNMERGED。

## 力矩解析基準與接觸合力座標驗證（2026-10-19，研究限定）

獨立解析兩對稱彈簧力偶：x=±100 mm，k=120 N/mm，θ=2×10⁻⁵ rad，uz=−xθ。合力 0 N，My=48 N·mm；解析能量導數以兩種步長均驗得 48 N·mm，原點平移後力偶不變。本地 11 項解析／負向測試 PASS。

以原版 CalculiX 2.21 [run 39190965338](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/39190965338) 的 SHA-256 固定 n8/n16 .dat，檢查 M_cg=M_origin−r_cg×F。n8 三向差分 1.44×10⁻⁶／1.71×10⁻⁴／5.12×10⁻¹⁰ N·mm，n16 為 7.74×10⁻⁶／2.12×10⁻³／6.10×10⁻⁹ N·mm，皆在來源輸出捨入誤差上界內；這只是接觸合力矩幾何一致性，不是獨立殼旋轉支承反力。

新增唯讀工具 verify_ccx221_contact_moment.py、test_verify_ccx221_contact_moment.py 與專屬 workflow。原始殼 SPC/MPC 旋轉反力矩、六分量平衡與工程 admission 均仍 NOT_ADMITTED；raw RF3 FAIL-CLOSED；PR #131 OPEN／UNMERGED。

## 原始殼 DOF5 反對稱轉角模態研究（2026-10-19／尚未獨立驗收）

新增 pinned S8R 原始殼節點 DOF5 小角度實驗；在板邊節點施加 θ_i=θ·(x_i−600)/600，θ=0、±1×10⁻⁵、±2×10⁻⁵ rad，接觸與無接觸兩分支、n=8／16 總計 20 案例。保留中心 Z=0.02 mm、原有板邊／肋端支承、材料與模型；只增加指定殼轉角與能量列印，無接觸分支移除 CONTACT PAIR/PRINT。此測試是**反對稱角度模態**，不是剛體轉動；其能量導數只對所定模態功共軛，不能代稱實體肋端反力矩或六分量反力。

生成器 `generate_ccx221_rot5.py`、結果驗證器 `verify_ccx221_rot5.py`、負向測試 `test_ccx221_rot5.py` 及隔離 workflow `ccx221-rot5-probe.yml` 均屬研究觀測。本地原始輸入 SHA、20 組生成與 9 項離線測試 PASS；真實 CalculiX 求解／完整接觸分支及結果尚待 exact-head CI 證據，禁止提前標示 PASS。能量 ELSE+CELS 是否完全涵蓋接觸貢獻，亦尚未 admission。所有原 S8R 物理門 FAIL-CLOSED，PR #131 OPEN／UNMERGED。

## 轉角模態求解與接觸分支重播（2026-10-19／研究觀測，不升格反力矩）

[原版 CCX 2.21 run 39194487445](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/39194487445) 20/20 求解及輸出驗證 SUCCESS。Artifact ID `12161706369`，ZIP SHA-256 `d9b36c420feca6a5f8cd50dc8cb07dbba6c2ebbbf0224abb4df57fbfd2291a8b`；manifest SHA-256 `d4af3bb7edbd06b5acba0343f07a8932281cd3221d35036daea31bdf6025fd9b`。n8 無接觸兩種中央候選能量斜率 3.8570／3.8575 N·mm；n16 無接觸 −0.3670／−0.3675 N·mm，網格間差異顯著。n8 接觸 3.6860／3.10851，n16 接觸 7.79852／22.60886 N·mm，後者無步長穩定性。n16 接觸 F3 隨 θ=−2e−5／−1e−5／0／+1e−5／+2e−5 rad，分別 14.10560／14.10568／14.10576／21.93426／31.65329 N。接觸力對轉角正反向不對稱，但尚無獨立 active-set 覆蓋證據，**不得聲稱已證實接觸切換**。

新增 fixed-manifest、兩份最終接觸合力列印相等、20 組精確 deck SHA／solver 完成／分支限定的唯讀重播器 `verify_ccx221_rot5_branch.py` 與 6 項負向測試，以及**僅下載既有 artifact 的快速 workflow** `ccx221-rot5-branch-replay.yml`。本地 6/6 PASS、固定 ZIP 重播 PASS。候選 ELSE+CELS 是否可直接當總勢能仍未證明；原始殼旋轉反力矩、六分量獨立平衡依然 NOT_ADMITTED。保留原 raw RF3 FAIL-CLOSED，PR #131 OPEN／UNMERGED。

## 接觸彈簧清單變化與壓力觀測待辦（2026-10-19，原始殼 DOF5）

已獨立重播原版 CCX 2.21 [run 39194487445](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/39194487445) 的最後增量 `CNUM`／逐列 `CELS`：n8 依 θ = −2e−5／−1e−5／0／+1e−5／+2e−5 rad 的接觸彈簧列印筆數為 3／3／3／2／3，slave element ID 均屬 79、82；n16 為 7／7／7／19／22，基準的 ID 為 158、159、162、163，正向轉角新增 130、131、190、191。n16 正向角度有新增元素列出能量大於零（130、131）；190、191 為零。列印零能量不等於可證明張開，有非零合力也不等於每筆 spring 均承壓。因此需使用官方支援的 `*CONTACT PRINT CDIS,CSTR` 補充 gap/pressure，先為 n8 3 案與 n16 5 案建立 source-pinned 精確輸入的新研究 workflow；未實際驗證前此輸出保持 NOT_RUN。完整原始殼轉角與 MPC 支承反力矩仍未建立，舊 RF3 門維持 FAIL-CLOSED，PR #131 未合併。

## 接觸壓力與相對間隙實測覆核（2026-10-19，限定求解器列印觀測）

原版 CCX 2.21 [run 39197070630](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/39197070630) SUCCESS；8 組 `CDIS/CSTR` 輸出 artifact `12162044405`、ZIP SHA-256 `5a025b9f7e87ec3b03078cfaddc4fc11e3bfdcd04c2ce95eec97076d6bc45354`。比較 [20 組原版 run 39194487445](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/39194487445) 的原始 ZIP SHA-256 `d9b36c420feca6a5f8cd50dc8cb07dbba6c2ebbbf0224abb4df57fbfd2291a8b`，確認新增輸出要求以外的 deck 內容未修改。

於最終時間 1.0：n8 角度 −1e−5／0／+1e−5 有 3／3／2 筆接觸彈簧；n16 角度 −2e−5／−1e−5／0／+1e−5／+2e−5 有 7／7／7／19／22 筆。**每個列印的 spring 均具有負法向相對位移及正壓力**。n16 正向新增 ID 130、131、190、191 均有正壓力；因此求解器層級的受壓接觸分布擴張已確認。注意 n8 3 組及 n16 部分組別 `CELS=0` 仍存在正壓力，故 CELS 單項不可用來判斷接觸是否張開或構成獨立接觸能量 oracle。

對同一案例兩次求解，8 案中 7 案的接觸合力、總列印接觸能與 STA 完全一致；n16 最大正轉角因迭代路徑變更，其接觸 F3 為 31.65338 N，前次為 31.65329 N，差 0.00009 N。此敏感性不得抹除或借此擴大物理容差。新增 `check_ccx221_contact_state.py` 與 `test_ccx221_contact_state.py`，local exact ZIP 八案例重播與 6 項正反向測試 PASS；快速 CI 需另驗 exact artifact ZIP SHA 並維持 NOT_ADMITTED。原始 S8R 殼旋轉支承反力矩與獨立六分量功共軛尚未建立；`OPEN_U_CONTACT_RF_GLOBAL_Z_IMBALANCE` FAIL-CLOSED；PR #131 OPEN／UNMERGED。

## 旋轉約束歸屬：原始殼 DOF5 對應擴充輔助 SPC（2026-10-19／僅運動學數值傳遞）

固定 CalculiX 2.21 原始碼 `gen3dboun.f` 顯示：一般靜態 shell 的 DOF4–6 經 tangent-plane projection 與 `MEANROTBS` MPC 轉為輔助節點的第 1 平移方向 SPC；旋轉約束不能以原始殼 `RF` 列印或 expanded-node 任意三維節點力直接當反力矩。研究-only、唯讀插樁 `ccx221_rot5_owner_instrument.py` 只在 `ne2boun(1/2,node)` 建立時列印 owner、原始旋轉軸、輔助 SPC 節點／方向及約束值，未修改 MPC 係數或求解程式的數值向量。

[原版／插樁版 run 39203418753](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/39203418753) **SUCCESS**，六組 n8／n16 × 無接觸負角／零角／正角的 `.dat/.sta` 對應逐位元組一致。原始輸入角度節點 n8=64（正負角非零各 62），n16=96（正負角非零各 94）；插樁版每案記錄 `KB_ROT_OWNER`：n8=156、n16=220 筆，兩個 auxiliary SPC owner／原始節點（含額外非角度驅動的支承）。就已指定 DOF5 的各原始節點，`axis=2`、第二旋轉約束 owner 的輔助 SPC 值與原始輸入一致；零角全部為 0。專屬 artifact ID `12164552181`、ZIP SHA-256 `01d03784c7fe0521087602262b36446127bad858ad90765170bc40c44c9d0361`。下一階段需對真正 `MEANROTBS` 約束的雙對偶力及 `gen3dboun` 投影係數建立 `Q_theta = sum(force_i * ∂u_i/∂theta)` 的獨立虛功測試；本輪無法取得獨立數值力矩，故 `MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED`／`ENGINEERING_ACCEPTANCE_NOT_ADMITTED` 不變。

## 旋轉虛功候選與能量曲率交叉檢查（2026-10-19／不承認工程反力矩）

原版與唯讀插樁 CalculiX 2.21 在 [PR #131 exact-head e65f0017／run 39213417119](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/39213417119) 完成無接觸 n=8／16，各 θ=−1e−5／0／+1e−5 rad 共六組真實求解；每組 `.dat/.sta` 與同一 pinned 原版案例**逐位元組一致**。該 workflow 的解析／負向測試、固定來源取得、原版及插樁版建置、六組求解、輔助 SPC／`MEANROTBS` MPC 係數與 `fmpc` trace 重播均 **SUCCESS**；不代表任何物理反力矩已成立。保存 artifact ID `12168916202`、GitHub ZIP SHA-256 `dd4e72c67cf3e05a6a1e54975d564cd123a8034356917aa68c5919100f345a79`、內含 `dual-report.json` SHA-256 `d754ed3c807c658ffea7ab73f4ffeeb05dcf9fdcc43d85a445561b3168a3baf3`。上游 20 組求解 ZIP SHA-256 `d9b36c420feca6a5f8cd50dc8cb07dbba6c2ebbbf0224abb4df57fbfd2291a8b`；owner 映射 ZIP SHA-256 `01d03784c7fe0521087602262b36446127bad858ad90765170bc40c44c9d0361`。

實測 `MEANROTBS` 含 4／6 個非零 MPC 項，不能假設轉角項固定在倒數第二項；已按**輔助節點 ID＋DOF**與固定的角度係數 `−1` 找到所指定原始殼 DOF5 的 owner，並保留 SPC owner 缺漏、係數錯誤、重複與非有限資料的負向拒絕。本輪原版 2.21 `resultsforc.c` 的 `fmpc` 由 dependent 項原始 `fn` 除以其 MPC 係數得到，`MEANROT` 的 `fn` 回填也會排除特定非結構節點；這是**內部 MPC 力帳**，並非經外部虛功證明的支承反力矩。

在同一組 artifact 中，令 `E(θ)` 為無接觸 PLATE＋RIB 列印 `ELSE` 的候選能量，`q(θ)` 為依 `−Σ fmpc·c_angle·(∂θ_i/∂θ)` 得到的候選廣義力，取 `h=1e−5 rad`：

| 網格 | `q(0)`（N·mm） | `[E(+h)−E(−h)]/(2h)`（N·mm） | `q(0)−dE/dθ`（N·mm） | `q'`／`E''`（無因次） |
| --- | ---: | ---: | ---: | ---: |
| n=8 | +1.92119125 | +3.85700000 | −1.93580875 | 0.4999997353 |
| n=16 | −0.15657761 | −0.36700000 | +0.21042239 | 0.4999999690 |

上表 `q'=[q(+h)−q(−h)]/(2h)`，`E''=[E(+h)−2E(0)+E(−h)]/h²`；用固定 ZIP 的原始列印值獨立重算。n=8 的 `E''≈184,089,000 N·mm/rad²`、`q'≈92,044,451 N·mm/rad`；n=16 分別 `116,147,600`、`58,073,796`。比例約 0.5 是**同源 solver trace 與捨入能量輸出之觀測關係**，不是已推導的理論因子；`ELSE` 作為完整總勢能的適用性與殼轉動 constraint dual 的物理定義均未被獨立證明。不能乘以 2 強迫通過、不能用中央差分代表跨接觸啟閉分支的唯一導數，也不能拿結果宣稱原始六分量支承平衡。

最小後續研究須先辨識完整 SPC/MPC constraint dual 與原始殼角度的**外部功共軛**（含平移力、旋轉軸投影、MPC 變分與非齊次項），由獨立可解的已知力偶檢驗力矩方向／單位後，才考慮 n=8／16 的真實殼模型。抽象兩彈簧 48 N·mm 解析式通過，只驗符號與算式，**不是**真實 S8R `fmpc` 的獨立 oracle。原始 `OPEN_U_CONTACT_RF_GLOBAL_Z_IMBALANCE_-44.4374645` 不變；PR #131 維持 OPEN／UNMERGED，`CONTACT_NOT_ADMITTED`、`MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED`、`ENGINEERING_ACCEPTANCE_NOT_ADMITTED`。

## 原始內力完整 MPC 消去重播與負值自由度歸屬（2026-10-19／僅研究演算法對帳）

固定 [PR #131 run 39228061706](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/39228061706) 的最終狀態是 **FAILURE**，但失敗階段是新增 `verify_ccx221_rot5_full_work.py` 的 `CCX221_FULL_WORK_FN_OWNER` 資料解析，**不是**真正求解失敗。該次 run 既有解析與負向測試、固定原始碼／artifact 取得、原版與唯讀插樁版 CalculiX 2.21 建置，以及無接觸 n8／n16 × 角度 −1e−5／0／+1e−5 rad 六組 `.dat/.sta` 位元組一致，皆個別 **PASS**。原始 trace 保存 artifact ID `12175920429`，ZIP SHA-256 `bcd509d1e082de9527d3b9da44ea503842d618a4e99ffc8e0407114684619d56`；來源 ZIP 與 owner ZIP 仍使用前述固定 hash。此 artifact 並未保留新求解 `.dat/.sta`，故本地重播使用固定原版 ZIP 的檔案補足驗證器輸入，原版／插樁版一致性只依同次 CI 的 `cmp` 日誌聲明。

實際 trace 的 `nactdof` 包含 `−2475`（n8）與 `−4139`（n16）。CalculiX 2.21 `mastruct.c` 使用負偶數 `−2(i+1)` 表示 SPC，自 `−1` 開始的負奇數 `−2i−1` 表示 dependent MPC；先前驗證器的 `eq < −2` 拒絕條件因而錯誤。更正為保留有效編碼、檢查負奇數所參照 MPC 編號未超出 `nmpc`，另保留節點／方向唯一性與非有限值等拒絕條件。本地負向及解析測試 18/18 PASS，六組固定 artifact 的完整 MPC 消去重播皆成功：每案例 n8 `nmpc=1238`、n16 `nmpc=2070`；各案例內，觀測 `MEANROTBS fmpc` 與重播最大絕對差均為 `0.0 N`（原始 trace 列印精度下）。

以全部 MPC 消去後的原始殼 DOF5 輔助 SPC 權重候選，比對既有 PLATE＋RIB `ELSE` 最終正負角列印能量中央差分：

| 網格 | 完整 MPC 後 `Qθ` 候選（θ=0，N·mm） | `ELSE` 中央斜率（N·mm） | 候選減能量斜率（N·mm） |
| --- | ---: | ---: | ---: |
| n8 | +3.8571396467 | +3.8570000000 | +0.0001396467 |
| n16 | −0.3672852155 | −0.3670000000 | −0.0002852155 |

後者用 `h=1e−5 rad`，且 `ELSE` 只列印有限有效位數；觀測差值與 PLATE 的列印量化尺度相容，**但並非**完整總勢能、真正 Lagrange multiplier、外部 SPC dual 或反力矩功共軛的獨立證明。新結果縮小了先前約 1:2 差額的來源至**未完整計入 MPC 串聯傳力的局部帳值**，而非可任意乘二的校正規則。對接觸分支、六分量自由體、@300 mm 植釘承載與真實工程容量均未建立新驗收。原始 `OPEN_U_CONTACT_RF_GLOBAL_Z_IMBALANCE` 門檻保持 FAIL-CLOSED，PR #131 必須 OPEN／UNMERGED，`CONTACT_NOT_ADMITTED`、`MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED`、`ENGINEERING_ACCEPTANCE_NOT_ADMITTED` 不變。

## 原始內力與 MPC 逆向運動學虛功對帳（2026-10-19／僅代數交叉驗證）

使用固定來源 ZIP SHA-256 `d9b36c420feca6a5f8cd50dc8cb07dbba6c2ebbbf0224abb4df57fbfd2291a8b` 與成功的 [DOF5／MEANROTBS CI #39236618417](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/39236618417) trace artifact `12179018108`（SHA-256 `1ca889801caaab50f92bf4d65e9f5a21ae553b2fdd26badc0ceae18b6005225e`），對六組無接觸 n8／n16、θ=−1e−5／0／+1e−5 rad 進行逆向 MPC 運動學切線重建。此法從指定輔助 SPC 角度模態出發，反向代入完整 MPC 約束係數求虛位移，再與**消去前**原始 `fn` 內積；與正向 MPC 消去後 SPC 加權力帳比較，兩條路徑分開計算。所有六組最大約束切線殘差約 `1.11e−16`；最大虛功差約 `2.27e−13 N·mm`（n8 負角），其餘在 `4.44e−16 N·mm` 內。新增解析、串聯與負向控制本地 9/9 PASS；不使用 `fmpc` 作為逆向內力虛功起點。

這是凍結線性 MPC 係數下的**轉置代數恆等式**，並未量測或獨立求得真正的 SPC dual／外部支承力矩；未指定的獨立平移虛位移設為零，且不包含幾何變動下的係數導數、非線性接觸啟閉或完整外部功。原有 `OPEN_U_CONTACT_RF_GLOBAL_Z_IMBALANCE_-44.4374645` 不得放寬。`CONTACT_NOT_ADMITTED`、`MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED`、`ENGINEERING_ACCEPTANCE_NOT_ADMITTED` 均維持，PR #131 保持 OPEN／UNMERGED。

## 固定六組無接觸輸入的外力來源稽核（2026-10-19／外部 SPC dual 仍未建立）

針對固定來源 artifact `12161706369`（ZIP SHA-256 `d9b36c420feca6a5f8cd50dc8cb07dbba6c2ebbbf0224abb4df57fbfd2291a8b`），直接解析 `n8/n16 × no_contact/minus1/zero/plus1` 六個原始 `panel.inp`：每案 `*STEP` 一次、`*BOUNDARY` 兩個區塊，`*CLOAD`、`*DLOAD`、`*DSLOAD`、`*DFLUX`、`*TEMPERATURE` 均為零個區塊。已知激勵為中心 U3=0.02 mm 與指定原始殼 DOF5 角度；其餘支承由 `*BOUNDARY` 指定。這是對**輸入卡片**的範圍限定稽核，不代表已對 CalculiX 所有可能的內生力、殘餘力或外力來源做完動態稽核。

在這六案中，不得虛構非零的顯式節點力或面載重向量，也不得將 `fn` 直接命名為完整 `f_int−f_ext`。先前完整 MPC 消去與逆向運動學虛功兩路徑一致，僅證明**相同內力資料與凍結約束係數**的代數轉置關係；不是外部 SPC reaction 或非線性 KKT residual 的獨立觀測。下階段必須先在求解器收斂後的實際 force-balance assembly 位置辨識內力／外力／約束分量、時間步與 active DOF，再增加最小唯讀插樁；如無法確認來源語意，保持 `INDEPENDENT_EXTERNAL_SPC_DUAL_NOT_ESTABLISHED`，不得以能量中央差分代替。

最新 [PR #131 exact-head `a3b5a855` 的 MPC CI #39246746684](https://github.com/masini1491/building-envelope-engineering-kb/actions/runs/39246746684) 已 SUCCESS，artifact `12183851724`；其 `adjoint-report.json` 六案 `constraint_physical_dual=NOT_ESTABLISHED`，`independent_external_spc_dual=NOT_ESTABLISHED`。原接觸 RF3 失衡及 `CONTACT_NOT_ADMITTED`、`MPC_REACTION_RECONSTRUCTION_NOT_ESTABLISHED`、`ENGINEERING_ACCEPTANCE_NOT_ADMITTED` 不變；PR 保持 OPEN／UNMERGED。
