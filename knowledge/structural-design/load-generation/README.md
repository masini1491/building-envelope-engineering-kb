---
title: "帷幕牆結構荷載生成方法"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 帷幕牆結構荷載生成方法

本目錄處理「外部設計荷載如何轉換成個別帷幕構件的 structural demand」。

重點不是保存某個專案的固定風壓或經驗係數，而是明確描述：

`design action → tributary geometry → line / point load → member analysis → support reaction → connection design`

## 核心原則

1. Design pressure 與 component load 不可混為同一資料。
2. Positive / negative pressure 應保留為不同 load cases，除非特定後續步驟只需要取 envelope。
3. Tributary width / area 應由實際 support geometry 決定，不是固定常數。
4. 面材壓力轉成 framing line load 時，應保存 load-distribution assumption。
5. 玻璃 dead load 與 wind load 的 load path 通常不同，應分別處理。
6. Setting block、point attachment、maintenance attachment 等 concentrated load 不得偷偷平均成 UDL。
7. 任何 reduction factor、load factor、impact factor、seismic coefficient 或 safety factor 都必須附 source；不得從舊計算書直接泛化。

## 相關頁面與 routing

- [Facade Tributary Loads](facade-tributary-loads.md)
- [Transom Wind-Load Distribution](transom-wind-load-distribution.md)
- [Glass Dead Load and Setting Blocks](glass-dead-load-and-setting-blocks.md)
- [Taiwan Design Wind Pressure Workflow](../wind/taiwan-design-wind-pressure-workflow.md)
- [Mullion / Transom Design Baseline](../framing/mullion-transom-design-baseline.md)
- [Load Path / Anchor Reactions](../connections/load-path-and-anchor-reactions.md)

## 資料模型建議

Future calculators should preserve at least:

```yaml
load_case:
  action_type: wind | dead | seismic | maintenance | other
  sign: positive | negative | not_applicable
  source: ...
  source_value: ...

load_transfer:
  receiving_component: ...
  tributary_geometry: ...
  distribution_type: uniform | triangular | trapezoidal | point | custom
  assumptions: ...
```

不要在失去來源追溯的情況下，把整條鏈縮成單一純量 `w`。

## 公開來源 routing

- 內政部建築研究所《帷幕牆系統結構耐風設計手冊》與相關研究：要求依面材、直料、橫料的位置、有效受風面積與風壓傳導機制分別建立設計風壓與構件需求。
- ASTM E1300-24：玻璃 load resistance routing；玻璃受力模型不能直接替代 framing load-generation model。

> 本目錄是 structural-load transformation framework，不保存 project-specific design load。