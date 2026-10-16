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
