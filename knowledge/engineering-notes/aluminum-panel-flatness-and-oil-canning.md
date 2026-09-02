---
title: "鋁板平整度與 Oil Canning 工程筆記"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 鋁板平整度與 Oil Canning 工程筆記

## 核心結論

建築外牆金屬板的「平整度」至少要區分兩個層次：

1. **原材料 flatness / dimensional tolerance**：mill / coil / sheet 交貨狀態是否符合適用材料標準與採購規格。
2. **完成面視覺平整度 / oil canning**：經裁切、折彎、補強、塗裝、運輸與安裝後，板面是否出現可視波浪、應力皺曲或反射不均。

兩者相關，但不能互相取代。

## Oil canning 是什麼

Metal Construction Association (MCA) 將 oil canning 說明為金屬屋面／牆面板平坦區域可見的波浪狀變形，技術上常稱 elastic buckling / stress wrinkling。鋼、鋁、鋅、銅等金屬板都可能發生。

MCA 同時指出，oil canning 受多種生產、材料選擇、panel design 與 installation 因素影響，無法由單一 alloy / temper 保證完全避免。

## 主要影響因子

依 MCA 技術資料與建築外殼工程實務，至少應檢查：

- 板厚；較薄的平板區域通常更容易顯現波浪
- panel flat width / 面板尺寸與長寬比
- coil / sheet leveling 品質
- 原材料與加工後殘留應力
- 裁切、沖孔、折彎造成的應力重新分布
- 折盒幾何、折邊與轉角配置
- stiffener 數量、位置、固定／黏接方式與 read-through
- 塗裝／烘烤熱歷程
- 支承面容許差與 subframe 平整度
- 安裝拘束、固定方式與 thermal movement 是否被限制
- 運輸、堆放與吊裝方式
- finish 反射性、顏色、觀察距離、視角與日照角度

## Temper 不等於完成面平整度

H12 與 H14 是不同加工硬化狀態；但不能從「H12 的加工硬化程度較低」直接推出「H12 成品一定較不平」。

完成面 oil canning 是 panel system-level 現象，不只是材料 coupon 的強度問題。材料牌號／temper 只是其中一個變因。

## 3004-H12 導入時的建議驗證

若專案由 3003-H14 改為 3004-H12，建議將審查拆成：

1. alloy / temper 是否符合專案材料規範
2. governing material standard 與 mill certificate
3. 原板 flatness / dimensional tolerance
4. 實際板厚與最大 panel size
5. fabrication method（裁切、折彎、補強）
6. coating / bake process
7. attachment / subframe tolerance
8. full-size finished panel mock-up（建築師對視覺要求高時優先）

## 視覺驗收注意

MCA 指出 oil canning 的可見程度會受觀看角度、日照角度與反射影響；同一板面在不同時間或視角下可能呈現顯著不同外觀。

因此若專案對完成面有高外觀要求，最好在契約／材料送審階段就明確約定：

- 觀察距離
- 觀察方向
- 自然光／人工光條件
- 可接受樣品或 mock-up
- panel size / thickness / stiffener configuration

不要在完工後才用未事先定義的主觀標準判退。

## 不可推論事項

- 不要把 `H14 > H12` 的硬化程度排序直接等同於 flatness 排序。
- 不要把 material standard 的原板 tolerance 當成已保證完成盒板外觀。
- 不要把 tensile / yield strength 合格當成 oil canning 已被控制。
- 不要在沒有專案定義的情況下自行發明完成面容許波幅。

## 來源

- Metal Construction Association, `Oil Canning in Metal Roof and Metal Wall Systems`: https://www.metalconstruction.org/index.php/online-education/oil-canning-in-metal-roof-and-metal-wall-systems
- MCA, `Visual Acceptance for Single Skin Architectural Metal Wall Panels`: https://www.metalconstruction.org/view/download.php/online-education/education-materials/walls-educational-files/materials/visual-acceptance-for-single-skin-architectural-metal-wall-panels
- The Aluminum Association, ANSI H35.2 / Aluminum Standards & Data information: https://www.aluminum.org/bookstore

> 本頁是工程判斷框架，不取代專案材料規範、材料標準或已核准 mock-up。