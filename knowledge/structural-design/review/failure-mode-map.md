---
title: "建築外殼結構破壞模式圖（Failure-Mode Map）"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# 建築外殼結構破壞模式圖（Failure-Mode Map）

本頁把 building-envelope structural design 視為一條由 load source 到 primary structure 的 failure-mode chain。

## 頂層荷載路徑

```text
Environmental / imposed action
        ↓
Glass / panel / sash / attachment
        ↓
Secondary framing / stiffener / transom
        ↓
Primary mullion / frame
        ↓
Bracket / cleat / hardware
        ↓
Fastener / weld / anchor
        ↓
Primary building structure
```

任一箭頭都代表 load-transfer assumption；任一 box 都可能有自己的 failure modes。

## 破壞模式族群

### A. 荷載定義失敗

- wrong design pressure
- positive / negative case omitted
- design vs test pressure confused
- missing dead / seismic / movement / concentrated load
- unsupported factor / criterion

### B. 荷載傳遞失敗

- wrong tributary area / width
- concentrated load incorrectly smeared
- setting-block path omitted
- component force not transferred into connections
- eccentricity ignored

### C. 整體 framing 失敗

- flexural yielding / allowable overstress
- excessive deflection
- biaxial response
- shear / torsion
- stability / buckling
- wrong span / support model
- splice / sleeve mechanics wrong
- composite action assumed without evidence

### D. 玻璃／glazing 失敗

- glass strength / load resistance
- excessive deflection
- point-support / drilled-hole local stress
- edge clearance / glass-to-frame contact
- laminated-glass effective-section assumption
- structural silicone demand / adhesion / compatibility
- post-breakage / redundancy gap

### E. 連接失敗

- fastener tension / shear
- fastener interaction
- eccentric fastener-group overload
- bearing
- tear-out / edge failure
- pull-out / thread stripping
- local extrusion wall bending
- bracket local bending
- prying / stand-off eccentricity

### F. 焊接連接失敗

- weld-group demand
- effective throat / length error
- eccentric moment / torsion omitted
- weld metal capacity
- base-metal / HAZ failure
- connected plate / angle / bracket failure

### G. 錨栓／基材失敗

- anchor steel failure
- concrete breakout / pullout / pryout where applicable
- insufficient edge distance / spacing / embedment
- wrong anchor category / evaluation basis
- primary-structure interface not verified

### H. 金屬面板／補強材失敗

- panel skin stress / deflection
- local fold / return failure
- stiffener bending / instability
- panel-to-stiffener connection failure
- perimeter attachment failure
- FEA boundary / mesh / singularity interpretation error

### I. 可開啟構件失敗

- sash / vent frame bending / racking
- hinge / stay / lock reaction overload
- hardware-body failure
- hardware-fastener failure
- local extrusion failure
- loss of operability after loading
- life-cycle / repeated-operation deterioration

### J. 位移相容性失敗

- inter-story drift incompatibility
- thermal movement restraint
- stack-joint closure / bottoming
- splice binding
- slot exhaustion
- glass edge collision
- sealant / gasket movement exceedance

### K. 驗證／證據失敗

- outdated standard edition
- wrong standard scope
- project-specific criterion presented as universal
- analysis/test scope mismatch
- unsupported PASS
- missing calculation trace

## 連鎖失效概念

建築外殼的破壞模式常呈連鎖發展，而不是彼此完全獨立。

Example generic chain:

```text
support eccentricity underestimated
        ↓
anchor reaction underestimated
        ↓
fastener-group demand underestimated
        ↓
local extrusion / bracket bending omitted
        ↓
connection incorrectly reported PASS
```

或：

```text
splice assumed rigid
        ↓
member moment distribution changes
        ↓
anchor reactions change
        ↓
glass-support relative deflection changes
        ↓
member strength may PASS while glazing compatibility FAILS
```

因此「一個假設只影響一個公式」通常不是安全假設。

## 審查問題集

對任何 system / component，至少問：

1. **What is the load source?**
2. **What receives it first?**
3. **What path carries it to the building?**
4. **Where are the discontinuities / eccentricities?**
5. **What global failure modes exist?**
6. **What local failure modes exist?**
7. **What movement must be accommodated?**
8. **Which assumptions are unverified?**
9. **Which standard / test covers each check?**
10. **What has not yet been checked?**

## 與 canonical 頁面的關係

- load generation → `../load-generation/`
- framing → `../framing/`
- connections → `../connections/`
- seismic → `../seismic/`
- structural glass → `../../structural-glass/`
- metal panel / stiffener → `../../cladding/structural-analysis/`
- operable elements → `../../operable-elements/`

> 本 map 用來找「漏算什麼」，不提供 project-specific capacity 或固定 acceptance value。