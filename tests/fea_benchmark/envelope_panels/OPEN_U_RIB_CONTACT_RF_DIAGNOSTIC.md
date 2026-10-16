# 開口 U 肋底面接觸｜RF、CFN 與 MPC 觀測限制

## 背景及證據

PR #131 的合成鋁板／U 型肋 S8R 面接觸，CalculiX 2.21 已能以 `*CONTACT PRINT,SLAVE=RIB_BASE_UNDERSIDE,MASTER=PLATE_TOP` 輸出 `CF/CFN/CNUM`，但 `*NODE PRINT RF` 三組原始觀測在接觸工況仍不能重建全域平衡。原始 artifact：CalculiX run `38855616149`、artifact `12027213102`。第一輪真正求解的接觸工況，n=8、n=16 壓合 `RF3` 殘差分別約 −44.4375 N、−17.8664 N；無接觸工況則近零。**絕對不可改用更寬容差宣稱 PASS**。

重新讀取資料後，n=8／16 壓合的 slave CFz 分別約 +14.4088／+14.1058 N；接觸面積分別為 34.02925／59.4862 mm²。分離工況的接觸面積與力也不為零且對網格敏感。**這不是合格單向接觸與設計傳力證據。**

## 驗證邊界

CalculiX 的 `RF` 官方輸出契約指出 MPC 相關作用力不被直接計算。S8R shell 內部展開與 contact 需要額外的 MPC／作用力語意查證，因此三個 `RF3` 區塊相加 **不是經證實的完整全域平衡 oracle**；但這也不表示模型已平衡。`CF/CFN` 是接觸面觀測量，屬內力，不能直接加到所有外部 RF 以湊出平衡。參考：<https://feacluster.com/CalculiX/ccx_2.18/doc/ccx/node305.html> 及 <https://github.com/Dhondtguido/CalculiX/issues/97>（issue 只作調查線索，非本案 bug 確證）。

`check_u_rib_contact_observations.py` 只取同一次求解的 final-time 節點 RF3 區塊及 `*CONTACT PRINT` slave 表面統計；明確標示 `UNPROVEN`／`NOT_ESTABLISHED`／`NOT_ADMITTED`，不是新的 contact physics PASS，亦不會停止或放寬既有 `check_u_rib_base_contact.py` 的 fail-closed 驗證。

**下一門**：建立獨立可驗證的 MPC 約束傳力重建／完整反力觀測，或可核對的其他數值 oracle 後，才允許研究 contact／網格收斂及合成植釘共同作用。
