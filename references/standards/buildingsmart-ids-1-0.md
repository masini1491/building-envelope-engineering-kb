---
title: "buildingSMART IDS 1.0 — Information Delivery Specification 來源 dossier"
verification_status: "VERIFIED_PRIMARY"
verified_at: "2026-09-11"
document_type: "reference-standard-dossier"
standard_id: "buildingSMART IDS 1.0"
organization: "buildingSMART International"
current_status: "Final"
edition: "1.0"
---

# 資訊交付規格 buildingSMART IDS 1.0 來源 dossier

- 驗證狀態：`VERIFIED_PRIMARY`
- 標準：Information Delivery Specification（IDS）1.0
- 組織：buildingSMART International
- 狀態：Final Standard；buildingSMART 表示 IDS 1.0 於 2024-06-01 成為正式標準
- 官方來源：https://www.buildingsmart.org/standards/bsi-standards/information-delivery-specification-ids/
- machine-readable standards server：https://standards.buildingsmart.org/
- 查證日期：2026-09-11
- authority type：openBIM information-requirement standard

## 適用範圍路由（Scope routing）

IDS 用 machine-interpretable 方式描述 IFC 模型的資訊要求，可指定 object、classification、material、property 與 value 等交付要求，並支援 automatic compliance checking。

對本 KB 的直接價值在於 shop-drawing／BIM semantic QA：先把「模型應交付哪些資料」轉成可執行 contract，再把 engineering design rule 留在獨立 canonical owner／validator，不把資訊完整性與工程安全判定混成同一層。

## 軟體實作路由

- GitHub specification repository：`buildingSMART/IDS`
- buildingSMART validation stack：`buildingSMART/validate`
- IFC parsing／audit 可與 `IfcOpenShell` 等工具搭配，但 implementation 不取代 IDS standard 本身。

## 不可推論事項

- IDS 驗證資料是否存在／符合 exchange requirement，不等於該數值的 engineering correctness 已驗證。
- IFC property 存在不代表 source、unit、revision、design basis 或 acceptance criterion 正確。
- development branch 的 repository state 不等於 IDS 1.0 Final Standard 的 canonical released text；版本判斷應回 buildingSMART official standard surface。

> IDS 最適合成為 information contract，不應被擴張成未經定義的 façade engineering rule engine。
