---
title: "帷幕牆結構計算審查 Checklist"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 帷幕牆結構計算審查 Checklist

本 checklist 用於工程計算書、AI 輸出或 future calculator 的 completeness review。

## 1. Design basis

- governing code / standard / edition 是否明確？
- project specification / criteria 是否有來源？
- design pressure 與 test pressure 是否分開？
- positive / negative load cases 是否分開保存？
- allowable / resistance / factor 是否有 provenance？

若缺失：`INCOMPLETE`。

## 2. Geometry / system definition

- system type 是否明確？
- mullion / transom / panel / glass / sash / bracket / anchor 的實際 load path 是否定義？
- span / support locations 是否明確？
- local axes / strong-weak axis 是否定義？
- splice / sleeve / stack joint 是否有 mechanics model？
- multi-part extrusion composite action 是否已確認？

## 3. Load sources

至少依適用性確認：

- wind
- dead load
- seismic component force
- inter-story movement / imposed displacement
- thermal movement
- maintenance / BMU / concentrated attachment
- operable-element dead / operating loads
- other project-required loads

## 4. Load generation

- pressure → tributary area / width 是否正確？
- transom triangular / trapezoidal distribution 是否按 support geometry 建模？
- glass dead load 是否透過 setting blocks / actual supports 傳遞？
- point load 是否保持 concentrated load，而非無依據平均化？
- load combination / envelope 是否有 governing basis？

## 5. Framing model

- single-span / multi-span / continuous beam 是否與實際相符？
- support DOF 是否明示？
- rotational restraint 是否有依據？
- splice 是 release / rigid / semi-rigid / sliding？
- EI 是否沿 member 一致？若有 sleeve / reinforcement 是否分段？
- male / female / reinforcement 是否真的具 compatible curvature？

## 6. Member global response

依適用性檢查：

- bending stress
- shear
- axial force
- major / minor axis
- biaxial bending
- torsion
- global deflection
- resultant deflection
- stability / buckling where relevant

## 7. Glass / structural glass

- ASTM E1300 applicable scope 是否符合 support condition？
- laminated effective thickness 是否有 current method / interlayer data？
- drilled / point-supported local stress 是否另行檢查？
- glass edge clearance / relative support movement 是否檢查？
- post-breakage / redundancy 是否需要？
- structural silicone bite / adhesion / compatibility / dead-load support 是否分開？

## 8. Transom / dead-load path

- glass setting-block load 是否形成 point load / eccentricity？
- transom wind-load 與 dead-load bending 是否分開？
- end reaction 是否傳到 transom-to-mullion connection？
- local torsion / local extrusion deformation 是否可能 governing？

## 9. Fasteners

Fastener body 與 connected material 必須分開：

- tension
- shear
- tension-shear interaction
- eccentric fastener-group distribution
- bearing
- edge distance / tear-out where applicable
- pull-out / thread stripping
- thread engagement
- local extrusion wall bending
- pretension / slip when relevant
- corrosion / galling / galvanic compatibility

## 10. Welds

- weld type / effective throat / effective length 是否有 basis？
- weld group centroid / geometry 是否正確？
- direct force + eccentric moment / torsion 是否合成？
- critical point 是否有檢查？
- weld metal strength source 是否 current？
- base metal / HAZ / connected plate / bracket 是否另行檢查？

## 11. Brackets / local sections / anchors

- bracket local bending
- local bearing
- plate / angle / channel section strength
- installation tolerance / stand-off eccentricity
- anchor group force distribution
- concrete edge / spacing / embedment / breakout / pullout where applicable
- cast-in vs post-installed anchor design basis

## 12. Metal panels / stiffeners

- panel skin bending / membrane response
- folded returns
- stiffener section / spacing
- panel-to-stiffener interface
- stud / rivet / screw / adhesive / weld
- perimeter attachment
- plate / shell FEA boundary condition
- mesh convergence
- local singularity interpretation
- buckling / geometric nonlinearity if relevant

## 13. Operable windows / vents

- sash / frame bending / racking
- glass / infill dead load
- hinge / stay / lock reactions
- hardware eccentricity
- hardware fasteners
- local extrusion reinforcement
- whole-product performance
- operability / life cycle where required

## 14. Seismic movement / thermal movement

- story drift demand source
- support movement / building joint
- stack joint / splice movement capacity
- slot direction / length / washer / friction assumptions
- glass edge clearance
- sealant / gasket movement capability
- adjacent panel collision / hard contact

## 15. Test / analysis relationship

- analysis prediction 與 test result 是否分開？
- E330 / E283 / E331 / AAMA tests 的用途是否正確？
- mock-up geometry / support / load 是否代表 design condition？
- test PASS 是否被錯誤延伸到未測 failure mode？

## 16. Calculation trace

每個重要結果至少應能追到：

`input → source → derived load → structural model → equation / solver → result → criterion → status`

若只有 `OK / NG` 而無 trace，至少標 `WARNING`。

## 17. Final coverage review

不要只問「是否 PASS」，而應輸出 failure-mode coverage table：

| Domain | Status | Governing case | Evidence / source | Missing items |
|---|---|---|---|---|
| framing flexure | PASS / ... | ... | ... | ... |
| deflection | ... | ... | ... | ... |
| connection | ... | ... | ... | ... |
| movement | ... | ... | ... | ... |

完整系統只有在所有 applicable critical domains 均有 traceable result 時，才可稱為 calculation package complete。
