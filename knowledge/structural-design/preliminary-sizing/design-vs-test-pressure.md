---
title: "設計風壓（Design Pressure）與試驗壓力（Test Pressure）分流"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 設計風壓（Design Pressure）與試驗壓力（Test Pressure）分流

## 核心原則

`Design Pressure` 與 `Test Pressure` 是不同 engineering objects，必須分開保存、分開顯示、分開追溯來源。

### 設計風壓（Design Pressure）

用於 structural sizing / verification 的設計荷載來源可能包括：

- governing wind code calculation
- wind-tunnel result
- project specification
- consultant-issued design criteria

Positive pressure 與 Negative pressure 應保留為獨立 load cases，不應只保留一個 absolute value。

### 試驗壓力（Test Pressure）

ASTM E330 / E330M 等試驗方法所使用的 pressure 是 performance-test input，通常來自 project test specification、mock-up protocol 或其他測試要求。

Test pressure 不應反向自動修改 design pressure。

## 防呆規則

- 不得將 test pressure 偷偷當成 design pressure。
- 不得因 test pressure 高於 design pressure，就自動把其差值解讀成通用 safety factor。
- 不得把 positive / negative case 壓成單一絕對值後失去方向語意。
- 若專案規範明確指定 design / test / proof relationship，應保存其 source 與 revision，而不是 hard-code 成 repository 通則。

## 建議資料欄位

Design load case 至少保存：

- id
- name
- direction: positive / negative
- pressure
- zone / location（若適用）
- source
- source revision / edition
- status: provisional / confirmed
- notes

Test pressure 則應使用獨立 object / namespace，避免與 structural design load 混用。

## 相關頁面

- [Taiwan Design Wind Pressure Workflow](../wind/taiwan-design-wind-pressure-workflow.md)
- [Curtain Wall Performance Test Crosswalk](../../standards/performance-testing/curtain-wall-performance-crosswalk.md)

> 本頁定義資料與工程責任邊界，不自行規定任何 project-specific pressure multiplier。