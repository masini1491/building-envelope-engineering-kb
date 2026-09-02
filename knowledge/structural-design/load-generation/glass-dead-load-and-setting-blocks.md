---
title: "玻璃自重與 Setting Block 荷載路徑"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 玻璃自重與 Setting Block 荷載路徑

## 核心概念

玻璃自重通常不是均勻傳給整支 transom，而是經由 setting blocks、glass shoes、mechanical supports 或其他 bearing points 形成集中反力，再傳入橫料／框架。

因此應把：

- glass dead load
- setting-block reaction
- transom local/global response

分成不同層級處理。

## 基本流程

1. 取得實際 glass make-up、尺寸與重量資料。
2. 確認真正承受自重的 mechanical support points。
3. 依 support configuration 求各 setting block / bearing point reaction。
4. 保留每一反力的作用位置。
5. 將 point load 施加到 transom / shoe / support member。
6. 檢查 global bending / deflection 與 local bearing / local extrusion behavior。
7. 將 end / connector reaction 繼續傳到 mullion / bracket / anchor。

## 玻璃重量

若沒有產品實際重量，可用密度與 glass make-up 做 preliminary estimate；但正式設計應優先使用實際產品／製造商資料，尤其 laminated / IGU / specialty glass 還包含 interlayer、spacer、coating 或其他構造。

任何額外 dead-load factor 都必須帶 source，不得把舊專案常數直接當 universal rule。

## 玻璃墊塊（Setting block）位置很重要

即使總玻璃重量相同，setting-block 位置改變也會改變：

- transom bending moment
- local web / flange force
- torsion
- connector reaction
- glass edge support condition

所以計算輸入至少要保存：

- number of support points
- position along transom
- bearing length / width if relevant
- supported glass lite / panel
- load per point

## 結構矽利康防呆

除非 approved structural glazing system 明確設計 structural silicone 承受永久自重，否則不得假設 glass dead load 主要由 silicone 吊掛。

應明確區分：

- wind-load transfer path
- dead-load support path

## 局部檢核

Setting-block point load 除了造成 transom global bending，還可能控制：

- local flange / web bending
- local bearing
- screw race / hook deformation
- setting-block compression / compatibility
- glass edge stress / support quality

因此「整支 transom flexural stress PASS」不代表 setting-block region 已完成檢核。

## 不可推論事項

- 不得一律假設兩個 setting blocks 各承受 50%，除非 support geometry 與 stiffness 足以支持此假設。
- 不得把 glass dead load 平均成 full-span UDL 來忽略 concentrated effect。
- 不得用 nominal glass thickness alone 當產品實際重量的唯一依據。
- 不得把 wind-load support model 自動套用到 dead load。

## 公開來源 routing

- ASTM E1300-24：玻璃 load-resistance design routing；其 glass support assumption 不取代 framing dead-load support design。
- Glass manufacturer / glazing manuals：setting block 與 edge support requirements 應依實際 glass make-up、support system 與產品技術資料確認。
- 內政部建築研究所《帷幕牆系統結構耐風設計手冊》：framing / load-path overall routing。

> 本頁不保存固定 setting-block spacing、固定 bearing length 或 project-specific dead-load factor。