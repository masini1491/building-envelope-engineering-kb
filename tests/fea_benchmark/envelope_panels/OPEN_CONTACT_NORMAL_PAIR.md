# 最小單向法向接觸數值基準（隔離合成研究）

## 問題與假設

兩個不同節點的 1 × 1 × 1 mm C3D8 立方體，初始接觸面重合。只定義法向、無摩擦、無植釘、無 U 型殼、無鋁板；人工 E=1000 MPa、ν=0；線性 penalty K=100000 MPa/mm 僅為**合成求解參數**。

下層底面拘束、上層頂面位移控制兩組互反工況：壓縮 −0.002 mm、張開 +0.002 mm。上層額外只施加最小面內剛體拘束。**無風壓、實物接觸剛度或設計材質推定。**

## 獨立 oracle 與反例

在一維均勻壓縮且忽略接觸 penalty 柔度時，兩段串聯桿的名義支承力 E × A × |Δ| / (L1+L2) = 1 N；接觸有限 penalty 下只做 ±20% 受限 screening。張開工況應近乎零兩端 Z 反力且介面 gap 為正。兩端反力方向相反，並核對輸出節點完整、實際位移間隙、工作目錄、輸入 bytes、DAT/STA/FRD 雜湊。負向測試拒絕假壓縮傳力、假拉力、錯誤間隙、錯誤節點、無效數值。

## 出處、邊界

CalculiX `*CONTACT PAIR`、`*SURFACE BEHAVIOR` 定義參考官方 CalculiX 手冊（2.18 公開參考）：https://www.feacluster.com/CalculiX/ccx_2.18/doc/ccx/node236.html 及 https://www.feacluster.com/CalculiX/ccx_2.18/doc/ccx/node337.html；本 Repo 的 CI 使用其實際安裝套件獨立覆驗，不能直接把舊版文件當成 2.21 PASS。

本階段不含實際板肋面接觸、摩擦滑移、角碼、植釘容量、壓力荷載、接觸點力與力矩全域平衡、材料容量或真實工程 acceptance。所有結果均 `EVIDENCE GATED`／`NOT_ADMITTED`；不得將 1 N 合成結果轉作扣件需求。
