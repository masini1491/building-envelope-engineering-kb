---
title: "點支承／鑽孔結構玻璃"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
---

# 點支承／鑽孔結構玻璃

## 適用範圍

本頁處理 drilled hole、point support、bolt / fitting / bushing 接觸等結構玻璃局部問題。

## ASTM E1300 適用範圍防呆

ASTM E1300-24 是建築玻璃 load resistance 的重要 practice，但其 scope 不應被延伸成「所有 drilled / notched / grooved glass 的完整設計方法」。遇到孔洞、開槽或其他局部不連續時，必須另做 local stress / contact verification。

## 局部驗證項目

至少確認：

- hole diameter
- edge distance
- hole-to-hole distance
- glass thickness / ply make-up
- bolt / fitting diameter
- sleeve / bushing geometry
- bushing material stiffness
- hole clearance
- bearing / contact area
- bolt preload 或安裝夾持力
- installation tolerance / eccentricity
- local principal tensile stress
- movement-induced contact
- fabrication quality、tempering / heat treatment 與 edge / hole finish

## 高分子套管（Polymer sleeve）／PTFE 防呆

Polymer sleeve、PTFE 或其他隔離／緩衝材料可用來降低 glass-to-metal 直接接觸、改善 bearing contact 與容許施工公差，但不得因此宣稱「孔邊應力集中已被消除」。

若 local behavior 對安全控制，應採 validated analytical method、local FEA、component test 或其他可追溯 verification。

## 支承策略

Point support 的數量、拘束自由度與 load path 應同時考慮：

- wind reaction
- dead load
- thermal movement
- inter-story drift
- rotation
- construction tolerance

增加固定點不一定總是更安全；過度拘束可能提高 thermal / seismic secondary stress。反之，減少固定點也不能只以「降低鑽孔數」作為充分設計理由，仍需確認整體穩定與 redundancy。

## 不可推論事項

- 一個 bolt = 一個理想 pin support
- bushing = zero local stress concentration
- bolt force 平均分配
- point support global model 可以省略 local contact check
- heat-soak treatment 可以取代孔邊結構檢核

## 主要來源

- ASTM E1300-24: https://store.astm.org/e1300-24.html

> 本頁提供 local-design routing，不提供 project-specific hole spacing、allowable stress 或 fitting capacity。