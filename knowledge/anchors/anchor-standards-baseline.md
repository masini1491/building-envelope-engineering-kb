---
title: "帷幕牆錨栓標準基線"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-02"
canonical_owner: true
---

# 帷幕牆錨栓標準基線

建築外殼工程中的 anchor 不應被視為單一材料類別。最少要先區分：

- cast-in / headed anchor bolts；
- cast-in embedded plates / welded studs / welded deformed bars；
- mechanical post-installed anchors；
- adhesive anchors；
- post-installed reinforcing bar systems；
- proprietary anchor channels。

不同類型的 load-transfer mechanism、qualification、design provision 與 installation requirement 可能不同。

## 現行 ACI routing（2026-09-02 查證）

### ACI CODE-318-25

**ACI CODE-318-25 — Building Code for Structural Concrete** 是目前 ACI structural-concrete 主體規範；其 scope 包含 mechanical / adhesive anchoring to concrete，也包含 reinforcement development / splicing 等相關結構規定。

實際專案仍須先確認 governing code / adopted edition；本頁的 current-edition snapshot 不能取代 project specification 或主管機關採用版本。

### ACI CODE-355.2-24

**ACI CODE-355.2-24 — Post-Installed Mechanical Anchors in Concrete—Qualification Requirements and Commentary** 用於 post-installed mechanical anchors 的 qualification / evaluation。

其 scope 涵蓋用於結構應用、承受 tension / shear / combined tension and shear，以及 static / seismic load 的 post-installed mechanical anchors，並區分 cracked / uncracked concrete 的適用性。

**355.2 是 qualification 標準，不應被誤當成單獨完成 project design 的替代品。**

### ACI CODE-355.4-24

**ACI CODE-355.4-24 — Post-Installed Adhesive Anchors in Concrete—Qualification Requirements and Commentary** 用於 post-installed adhesive anchors 的 qualification / evaluation。

Mechanical anchor 與 adhesive anchor 不得互相代用 qualification rules。

### Post-installed reinforcing bar systems

若系統是 post-installed reinforcing bar，而不是一般 mechanical / adhesive anchor，必須辨識其專屬 qualification / design routing；不可只因施工方式使用黏著劑就自動視為一般 adhesive anchor。

## ASTM F1554

**ASTM F1554/F1554M** 是 anchor bolts / anchor rods 的材料與機械性質規格之一，常見 Grades 36 / 55 / 105。

但 ASTM F1554 的 scope 明確排除 mechanical expansion anchors，因此不可把所有後置式 expansion anchor 都寫成 `ASTM F1554`。

## Cast-in embedded plate routing

若為預埋鋼板系統，不能只寫「anchor PASS」。至少要辨識：

- headed stud / headed anchor；
- straight or hooked deformed bar；
- cast-in anchor bolt；
- proprietary channel；
- plate / weld / bracket / anchor / concrete 的完整 load path。

Canonical methodology：[`cast-in-embedded-plate-design.md`](cast-in-embedded-plate-design.md)。

## 後置式機械錨栓 routing

Mechanical post-installed anchor 應把以下項目一起納入 review：

1. exact product / anchor family；
2. applicable qualification / evaluation document；
3. governing design code / method；
4. substrate / concrete strength / member thickness；
5. cracked / uncracked status；
6. effective embedment / nominal embedment；
7. edge distance / spacing / group effect；
8. tension / shear / combined load；
9. concrete breakout / pullout / pryout / steel / edge failure 等適用 failure modes；
10. seismic qualification（需要時）；
11. installation torque / drilling / hole cleaning / setting / inspection；
12. base plate / bracket rigidity、bearing、bending 與完整 connection load path。

Canonical methodology：[`post-installed-mechanical-anchor.md`](post-installed-mechanical-anchor.md)。

## Adhesive anchor routing

Adhesive anchor 至少還要額外確認：

- adhesive product qualification；
- bond strength basis；
- sustained loading；
- temperature / environment；
- hole cleaning / installation condition；
- installer / inspection requirements where applicable。

目前本 KB 尚未建立完整 adhesive-anchor canonical design page；遇到正式專案應回 governing code + ACI CODE-355.4-24 + exact product evaluation evidence，不得用 mechanical-anchor page 代替。

## Manufacturer software／ESR／ETA

Manufacturer software、ICC-ES ESR、ETA / EAD 等可以是重要 product evidence，但必須保存：

- exact product；
- evaluation identifier；
- edition / issue date；
- governing design method；
- cracked / uncracked applicability；
- embedment / edge / spacing limits；
- installation condition；
- seismic category / qualification if applicable；
- software assumptions（例如 rigid anchor plate）。

**Manufacturer software `OK` ≠ façade connection PASS。**

外側 bracket / plate / weld / bolt / slot / aluminum local failure 與 reaction provenance 仍需獨立 review。

## 帷幕牆設計 routing

幕牆 anchor / bracket 設計至少分開檢查：

1. attachment type；
2. substrate：concrete / steel / masonry / other；
3. tension / shear / combined load；
4. anchor group / eccentricity / plate rigidity；
5. concrete / substrate failure modes；
6. anchor steel / bond / development failure modes；
7. edge distance / spacing / group effect；
8. cracked / uncracked concrete；
9. seismic qualification（需要時）；
10. installation / inspection / proof-test requirements；
11. base plate / bracket bearing and bending；
12. weld / bolt / anchor channel 等完整 load path；
13. factor / resistance provenance。

## 不可推論事項

- `F1554 anchor bolt = expansion anchor`：錯誤。
- `ACI 355.2 qualification PASS = project design PASS`：錯誤。
- mechanical anchor 與 adhesive anchor 的 qualification / factor 可互換：錯誤。
- 只看螺桿鋼材強度就代表整個 anchor capacity：錯誤。
- 廠商型錄最大拉力可直接當設計值：錯誤。
- manufacturer software 顯示 `OK` 就代表 bracket / plate / façade connection 全部 PASS：錯誤。
- cast-in 與 post-installed anchor 只因 failure-mode 名稱相同，就可以共用公式／係數：錯誤。

## 主要來源

- ACI CODE-318-25 — American Concrete Institute。
- ACI CODE-355.2-24 — American Concrete Institute。
- ACI CODE-355.4-24 — American Concrete Institute。
- ASTM F1554/F1554M — ASTM International。
- ICC-ES evaluation services：產品適用時。
- ETA / EAD：專案接受該 evaluation route 且 exact product / edition / method 已確認時。

> 本頁是 anchor 類型與 governing-standard routing 的 canonical owner；實際 resistance、factor、interaction equation、installation requirement 與 project acceptance 應依本次專案採用 code、exact product evaluation 與可追溯計算確認。