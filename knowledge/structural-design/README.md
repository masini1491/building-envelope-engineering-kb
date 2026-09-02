---
title: "帷幕牆結構設計方法總覽"
verification_status: "HIGH_CONFIDENCE"
verified_at: "2026-09-02"
canonical_owner: true
document_type: "router"
domain: "structural-design"
canonical_key: "structural-design.router"
---

# 帷幕牆結構設計方法總覽

本目錄是建築外殼結構設計與計算審查的 domain router。使用時採 progressive reading：先辨識問題位於哪一層，再讀最低必要的子目錄與 canonical page。

## 結構工作鏈

`project specification / design basis`
→ `wind / seismic / dead / maintenance inputs`
→ `load generation`
→ `framing / panel / glass response`
→ `connections / anchors`
→ `secondary support / primary-structure interface`
→ `movement compatibility`
→ `review / completeness`

任何一層 `PASS` 都不自動代表整條 load path `PASS`。

## 子目錄 routing

- [`wind/`](wind/)：台灣帷幕牆風壓、耐風設計手冊與 design-pressure workflow。
- [`seismic/`](seismic/)：台灣 façade component seismic force、connection load path、movement compatibility。
- [`load-generation/`](load-generation/)：pressure / dead load / tributary geometry → member / support demand。
- [`framing/`](framing/)：mullion / transom、continuous member、biaxial bending、splice、multi-part extrusion、glass-edge relative deflection。
- [`connections/`](connections/)：fastener group、weld group、screw pull-out、local extrusion failure、connection reaction routing。
- [`secondary-support/`](secondary-support/)：back brace、reaction handoff、supporting-steel local effect、design responsibility boundary。
- [`preliminary-sizing/`](preliminary-sizing/)：required `I / S`、support/composite assumptions、design vs test pressure、traceability。
- [`review/`](review/)：Project Design Basis、failure-mode map、coverage、hidden multiplier audit、calculation-review checklist。

## 外部 subsystem routing

不是所有結構問題都應搬進本目錄。專屬 subsystem mechanics 保留在其 domain：

- [`../structural-glass/`](../structural-glass/)：glass fin、point-supported / drilled glass、laminated effective thickness、post-breakage。
- [`../cladding/structural-analysis/`](../cladding/structural-analysis/)：metal panel、stiffener、panel FEA。
- [`../operable-elements/`](../operable-elements/)：sash、hinge / stay / lock、hardware load path。
- [`../anchors/`](../anchors/)：cast-in embedded plate、post-installed mechanical anchor 與 anchor standards routing。

此結構避免把所有「有結構計算」的內容集中成單一巨大目錄。

## 結構審查最低規則

1. 先確認 Project Design Basis，而不是先套公式。
2. Design pressure、test pressure、reaction、imposed displacement 是不同 engineering objects。
3. Support DOF、composite action、load path、axis 與 eccentricity 必須明確。
4. Global member PASS 不取代 local connection / extrusion / anchor / supporting-structure check。
5. 任何 factor、allowable、resistance、interaction equation 必須有 governing source / edition / scope。
6. 缺必要資料回傳 `INCOMPLETE`，不得以方便的假設補成 PASS。

> 本頁只負責 structural-design routing；個別工程結論由各子目錄 canonical page 維護。