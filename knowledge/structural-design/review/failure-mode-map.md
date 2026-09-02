---
title: "Façade Structural Failure-Mode Map"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
---

# Façade Structural Failure-Mode Map

本頁把 building-envelope structural design 視為一條由 load source 到 primary structure 的 failure-mode chain。

## Top-level load path

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

## Failure-mode families

### A. Load-definition failure

- wrong design pressure
- positive / negative case omitted
- design vs test pressure confused
- missing dead / seismic / movement / concentrated load
- unsupported factor / criterion

### B. Load-transfer failure

- wrong tributary area / width
- concentrated load incorrectly smeared
- setting-block path omitted
- component force not transferred into connections
- eccentricity ignored

### C. Global framing failure

- flexural yielding / allowable overstress
- excessive deflection
- biaxial response
- shear / torsion
- stability / buckling
- wrong span / support model
- splice / sleeve mechanics wrong
- composite action assumed without evidence

### D. Glass / glazing failure

- glass strength / load resistance
- excessive deflection
- point-support / drilled-hole local stress
- edge clearance / glass-to-frame contact
- laminated-glass effective-section assumption
- structural silicone demand / adhesion / compatibility
- post-breakage / redundancy gap

### E. Connection failure

- fastener tension / shear
- fastener interaction
- eccentric fastener-group overload
- bearing
- tear-out / edge failure
- pull-out / thread stripping
- local extrusion wall bending
- bracket local bending
- prying / stand-off eccentricity

### F. Welded-connection failure

- weld-group demand
- effective throat / length error
- eccentric moment / torsion omitted
- weld metal capacity
- base-metal / HAZ failure
- connected plate / angle / bracket failure

### G. Anchor / substrate failure

- anchor steel failure
- concrete breakout / pullout / pryout where applicable
- insufficient edge distance / spacing / embedment
- wrong anchor category / evaluation basis
- primary-structure interface not verified

### H. Metal-panel / stiffener failure

- panel skin stress / deflection
- local fold / return failure
- stiffener bending / instability
- panel-to-stiffener connection failure
- perimeter attachment failure
- FEA boundary / mesh / singularity interpretation error

### I. Operable-element failure

- sash / vent frame bending / racking
- hinge / stay / lock reaction overload
- hardware-body failure
- hardware-fastener failure
- local extrusion failure
- loss of operability after loading
- life-cycle / repeated-operation deterioration

### J. Movement-compatibility failure

- inter-story drift incompatibility
- thermal movement restraint
- stack-joint closure / bottoming
- splice binding
- slot exhaustion
- glass edge collision
- sealant / gasket movement exceedance

### K. Verification / evidence failure

- outdated standard edition
- wrong standard scope
- project-specific criterion presented as universal
- analysis/test scope mismatch
- unsupported PASS
- missing calculation trace

## Cascade concept

Façade failure modes often cascade rather than occur independently.

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

## Review question set

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

## Relation to canonical pages

- load generation → `../load-generation/`
- framing → `../framing/`
- connections → `../connections/`
- seismic → `../seismic/`
- structural glass → `../../structural-glass/`
- metal panel / stiffener → `../../cladding/structural-analysis/`
- operable elements → `../../operable-elements/`

> 本 map 用來找「漏算什麼」，不提供 project-specific capacity 或固定 acceptance value。