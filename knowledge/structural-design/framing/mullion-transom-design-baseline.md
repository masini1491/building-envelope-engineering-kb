---
title: "帷幕牆直料／橫料結構設計基線"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 帷幕牆直料／橫料結構設計基線

## 角色

直料（mullion）與橫料（transom）是帷幕牆常見的局部受力構件。風壓由玻璃／金屬板等面材傳入 framing，再由 framing 將反力傳至繫件與主體結構。

## 設計流程

至少應依序確認：

1. governing design pressure
2. tributary width / effective wind area
3. span / support condition
4. section properties（Ix / Iy / Sx / Sy / torsion-related properties as applicable）
5. alloy / temper / certified material properties
6. bending / shear / local bearing / connection effects
7. deflection / serviceability criteria
8. splice / sleeve / connection stiffness
9. thermal movement / inter-story movement compatibility
10. anchor reactions and load path continuity

## 簡化力學不等於正式設計

對簡單單跨直料可用基本梁理論做初步理解，例如 uniformly distributed load 下的 bending / deflection；但實際 curtain wall framing 可能包含：

- multiple spans
- pinned / semi-rigid / sliding connections
- splice sleeves
- eccentric load transfer
- coupled mullions
- male / female interlock
- transom-to-mullion joint stiffness
- glass / panel restraint interaction

因此示意梁公式只能作初步 sanity check，不能取代 project-specific structural model。

## 撓度防呆

Deflection criterion 可能來自：

- project specification
- glass edge-clearance / gasket / sealant functional requirement
- AAMA / ASTM test acceptance
- governing design standard
- architect visual requirement

AI 不得自行宣稱所有 curtain wall mullion 都固定採同一個 `L/x` 或固定 mm 限值。

## 截面性質防呆

複雜鋁擠型截面不可只用外包矩形估算 section properties。應使用：

- verified CAD section property
- extrusion supplier section data
- validated engineering calculation

若截面有 thermal break、screw race、snap cap、male/female interlock、非對稱 cavity 或組合件，需依實際 load transfer 判斷 effective section。

## 橫料特定注意事項

橫料除風壓外還可能承受：

- glass / panel dead load via setting blocks
- local torsion
- eccentric glass load
- transom-to-mullion connector forces

不能只用「橫料與直料同一套風壓彎矩公式」處理所有 case。

## 破壞模式檢核表

- flexural stress
- shear
- excessive deflection
- local yielding / bearing
- screw / bolt connection failure
- transom cleat / end connection failure
- splice slip / instability
- local extrusion wall deformation
- anchor reaction overload

## 主要來源／routing

- 內政部建築研究所《帷幕牆系統結構耐風設計手冊》
- governing aluminum material standard（如 CNS 2257 / ASTM B221 family）
- project specification / approved structural calculation

> 本頁是結構設計 routing，不提供可直接套用的固定 allowable stress 或 deflection limit。