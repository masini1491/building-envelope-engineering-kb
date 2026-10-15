# U 型加勁肋｜參數化幾何預檢（研究用途）

這是**幾何資料預檢工具**，不是 CalculiX 求解器、扣件力計算器或工程設計驗算。現階段不新增任何材料容量、撓度、連接、接觸或風壓 admission。它與既有 `check_center_rib_plate.py` 的共節點直立肋研究是**不同的物理構造**，不可直接把前者的結果移植過來。

## 現場常見構造與座標

使用者提供的典型構造為鋁板背面 U 型加勁肋：底面貼鋁板，U 型開口背向面板；外寬約 50 mm、外高約 50 mm、肋厚約 3 mm，鋁板常用 3 mm；單排鋁植釘沿加勁肋中心線排列，常見標示 `@300 mm`。尺寸會依構造條件調整，因此**以上均是常用輸入預設，而非不可更改的規定尺寸／強度參數**。

`x` 為 U 型橫向（斷面置中），`y` 為加勁肋縱向，`z=0` 表示底面與鋁板背面的名義接觸平面，U 型開口朝 `z>0`。B、H 採**名義外寬及外高**，角部為尖角理想化，未知折彎內外半徑、實際孔徑及墊片形狀均未計入。斷面以底板 `B×t` 與兩片不重疊的腹板 `t×(H−t)` 形成，不是封閉矩形管。獨立使用多邊形積分與矩形拆分覆核面積、形心及兩個形心斷面二次矩。

## 使用方式

在 `tests/fea_benchmark/envelope_panels` 下執行：

```sh
python -B -m unittest -v test_u_rib_geometry.py
python -B u_rib_geometry.py --defaults
python -B u_rib_geometry.py --input /path/to/synthetic-input.json
```

`--defaults` 只回報 50×50×3 mm 名義斷面及 300 mm *pitch*；**不會推測第一支植釘的位置或肋長，因此沒有植釘座標**。

如需產生植釘點位，請明確提供完整 JSON，例如以下**純合成、非任何實際專案**測試資料：

```json
{
  "section_width_mm": 50.0,
  "section_height_mm": 50.0,
  "rib_thickness_mm": 3.0,
  "panel_thickness_mm": 3.0,
  "stud_pitch_mm": 300.0,
  "rib_length_mm": 900.0,
  "first_stud_offset_mm": 150.0
}
```

此合成配置產生 `y=150、450、750 mm`、`x=0` 的位置，最後端距 150 mm；**端距 150 mm 並非一般工程規定，也不是使用者已提供的施工參數**。所有位置僅為面板背面投影中心點，尚不表示植釘長度、孔位、螺帽夾持、滑移、扭轉拘束或焊接承載能力。

## 驗證與停止條件

輸入必須是 4096 bytes 以內的一般 JSON 檔；重複 key、NaN／Infinity、布林冒充數值、多餘欄位、非有限尺寸、退化 U 型斷面或不完整植釘端距配置均 fail closed。程式限制的尺寸範圍只用於**軟體輸入防護**，不是工程可用／適用範圍；符合這些界線不代表構造合格。

輸出標示 `OPEN_U_NOMINAL_SHARP_CORNER_GEOMETRY_ONLY`、`solver_execution=NOT_RUN`、`fastener_loads=NOT_COMPUTED`、`material_capacity=NOT_ADMITTED` 及 `engineering_acceptance=NOT_ADMITTED`。折彎半徑、面板折邊、孔洞、植釘焊道、面板與肋底面接觸、螺帽預力、支承及真正離散傳力都需要後續**獨立數值／試驗基準**；不得把這個幾何預檢直接改稱可用的 FEA／設計容量分析。
