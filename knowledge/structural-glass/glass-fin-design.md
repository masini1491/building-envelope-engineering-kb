---
title: "玻璃肋／玻璃直料設計（Glass Fin Design）"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 玻璃肋／玻璃直料設計（Glass Fin Design）

## 適用範圍

Glass fin / glass mullion 是以玻璃本身作為主要受彎或受軸構材的結構玻璃系統。設計時不能只把它當成「比較厚的玻璃面板」。

## 設計流程

至少分開處理：

1. glass make-up 與 minimum ply thickness
2. laminated effective stiffness（若為膠合玻璃）
3. member geometry / unsupported length
4. support / restraint / splice condition
5. wind / pressure load path
6. self-weight / permanent load path
7. global bending / shear / axial stress
8. deflection / rotation
9. local connection / hole / clamp / bearing stress
10. inter-story / thermal imposed movement
11. post-breakage / redundancy

## 全域模型防呆

以 beam / frame / shell / solid model模擬 glass fin 時，必須先定義模型代表的是：

- monolithic equivalent section
- laminated effective section
- layered glass + interlayer model
- simplified frame member

不同模型層級不能混用 section property 或 response interpretation。

## 等效截面性質

若使用 effective thickness：

- deflection 與 bending stress 所需 equivalent property 可能不同；
- glass-fin 長細比、支承與 load duration 會影響 applicability；
- multi-ply laminate 不得沒有方法依據就機械合併。

參見 `laminated-glass-effective-thickness.md`。

## 挫屈／穩定性

細長 glass fin 除強度與撓度外，還要確認是否存在 lateral / flexural / torsional stability 問題。若模型或適用標準沒有涵蓋 relevant instability mode，不得只因線性彈性應力低於某值就宣稱整體安全。

## 連接交互作用

Glass fin 的 global PASS 不代表 connection PASS。必須將支承反力傳入：

`glass fin → hole / shoe / clamp / silicone → plate / bolt → anchor / structure`

並分別檢查 local contact、bearing、bolt force、plate bending、weld / anchor 等。

## 位移相容性

結構玻璃系統常需要容許樓層側移與 thermal movement。固定點的位置與自由度應讓系統能傳力，也能避免不必要的 secondary stress。

## 不可推論事項

- glass fin = conventional aluminum mullion with a different E
- global FEA stress contour = hole / contact stress 已經被捕捉
- more restraint = safer
- laminated fin nominal thickness can be used directly as section thickness
- wind-only check covers seismic / movement condition

## 相關公開標準

- ASTM E3491-25 — laminated glass effective thickness
- ASTM E1300-24 — building glass load resistance（注意 scope limitations）

> 玻璃肋通常需要超出一般外牆構件條文式檢核的專業分析；應採用經驗證的建模假設與專案特定驗證。