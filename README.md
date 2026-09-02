# Building Envelope Engineering Knowledge Base

以台灣建築外殼工程實務為核心的公開技術知識庫，供工程師與 AI（例如 ChatGPT / Codex）查詢、交叉驗證與持續維護。

本 repository 的範圍包含但不限於：帷幕牆、玻璃、鋁板與金屬外牆、石材、採光罩、材料與扣件、表面處理、防蝕、結構耐風、氣密／水密／層間變位試驗，以及相關 CNS / ASTM / AAMA-FGIA / ISO 標準與台灣工程實務。

## 核心原則

1. **Evidence first**：先有來源，再下工程結論。
2. **Authority aware**：明確區分法規、正式標準、政府手冊、專案文件、製造商資料、工程經驗與未驗證資訊。
3. **Current before cached**：涉及現行規範、版本或產品資料時，優先確認 freshness；舊聊天與 AI memory 不作為正式技術來源。
4. **Reference, don't repeat**：同一規則或技術結論只保留一個 canonical owner，其他頁面以連結／路由為主，避免 drift。
5. **Progressive reading**：AI 不應預設完整掃描 repository；先從本 README 與 `CHAT_INIT.md` 進入，再依題目讀最低必要內容。
6. **Public-safe**：不公開未授權施工圖、客戶／公司機密、受版權保護標準全文或其他不可再散布內容。

## Repository 路由

- `AGENTS.md`：AI / maintainer 的治理、authority、來源與公開安全規則。
- `CHAT_INIT.md`：新聊天室最小啟動流程。
- `knowledge/`：整理後、可供工程師與 AI 直接使用的技術結論。
- `references/`：來源、provenance、版本、適用範圍、限制與 evidence dossier。
- `indexes/`：規範、材料與 cross-reference 的機器可讀索引（待建立）。
- `templates/`：新增標準、材料、工程筆記與專案知識時的固定格式。

## 已建立的 baseline

### Standards / performance testing

- [`knowledge/standards/performance-testing/curtain-wall-performance-crosswalk.md`](knowledge/standards/performance-testing/curtain-wall-performance-crosswalk.md)  
  CNS 13971 / 13972 / 13973 / 13974 / 14281 與 ASTM E283 / E330 / E331、AAMA 501.1 / 501.4 等帷幕性能試驗 crosswalk；另收 AAMA 501.2、501.6、501.7、503、ASTM E1105 / E1233。

### Structural design / manuals

- [`knowledge/structural-design/wind/taiwan-curtain-wall-wind-design-manual.md`](knowledge/structural-design/wind/taiwan-curtain-wall-wind-design-manual.md)  
  內政部建築研究所《帷幕牆系統結構耐風設計手冊》與前身研究之 routing / 工程摘要。
- [`knowledge/structural-design/framing/mullion-transom-design-baseline.md`](knowledge/structural-design/framing/mullion-transom-design-baseline.md)  
  直料／橫料的 load path、section property、strength、deflection 與 connection 基線。
- [`knowledge/structural-design/framing/multi-part-extrusion-load-sharing.md`](knowledge/structural-design/framing/multi-part-extrusion-load-sharing.md)  
  male / female / reinforcement 等多件鋁擠型的共同作用、stiffness sharing 與 `composite_action = unknown → INCOMPLETE` guardrail。
- [`knowledge/structural-design/connections/load-path-and-anchor-reactions.md`](knowledge/structural-design/connections/load-path-and-anchor-reactions.md)  
  帷幕 connection load path、bracket / anchor reaction 與 eccentricity routing。
- [`knowledge/structural-design/connections/fastener-group-analysis.md`](knowledge/structural-design/connections/fastener-group-analysis.md)  
  偏心 bolt / screw group 的 centroid、direct load、moment-induced load、resultant demand 與 connected-material checks。
- [`knowledge/structural-design/connections/local-extrusion-failure.md`](knowledge/structural-design/connections/local-extrusion-failure.md)  
  bolt channel、screw race、hook、sleeve 等局部鋁擠型的 bearing、local bending、pull-out / thread engagement failure-mode framework。
- [`knowledge/structural-design/connections/weld-group-analysis.md`](knowledge/structural-design/connections/weld-group-analysis.md)  
  arbitrary weld-group geometry、effective throat、centroid、`Aw / Ix / Iy / J`、偏心荷載與 critical-point demand 的通用分析框架。

### Materials

- [`knowledge/materials/aluminum/common-curtain-wall-alloys.md`](knowledge/materials/aluminum/common-curtain-wall-alloys.md)  
  3003-H14、3004-H12、6063-T5、6005-T5、6105-T5 的 product-form 與 governing-standard baseline；3003-H14 → 3004-H12 的台灣實務趨勢目前保守標為 field observation，待補公開一手證據。
- [`knowledge/materials/steel/astm-a36.md`](knowledge/materials/steel/astm-a36.md)  
  ASTM A36/A36M 結構鋼 baseline，並提醒不得直接視為 CNS 2473 SS400 完全等價。

### Finishes / corrosion protection

- [`knowledge/finishes/aluminum-organic-coatings-aama-2603-2604-2605.md`](knowledge/finishes/aluminum-organic-coatings-aama-2603-2604-2605.md)  
  AAMA 2603-26 / 2604-26 / 2605-26 的性能層級與「性能規範 ≠ 固定塗料 chemistry」原則，另路由 AAMA 611-26。
- [`knowledge/corrosion-protection/hot-dip-galvanizing-astm-family.md`](knowledge/corrosion-protection/hot-dip-galvanizing-astm-family.md)  
  ASTM A123 / A153 / A384 / A385 / A780 熱浸鍍鋅 family 的分工與建築外殼工程使用注意事項。

### Fasteners / project knowledge

- [`knowledge/fasteners/stainless/iso-3506-a2-70-a2-90.md`](knowledge/fasteners/stainless/iso-3506-a2-70-a2-90.md)  
  ISO 3506-1:2020、A2-70 與非標準 property class A2-90；包含已去識別化的 `VERIFIED_PROJECT` / `HIGH_CONFIDENCE` 特殊工程知識，不公開原施工圖或可辨識專案資訊。

## 下一批預定範圍

- structural load generation：tributary load、transom wind-load distribution、glass dead load / setting blocks、concentrated attachment loads
- framing：continuous mullion、biaxial bending、resultant / glass-edge relative deflection
- connection：tension-shear interaction、screw pull-out、thread engagement、bracket local bending 的 primary-source 深化
- seismic façade component / connection force 與 inter-story-drift routing
- metal panel / stiffener / plate-FEA modeling methodology
- operable window / sash / hardware structural load path
- 個別 CNS / ASTM / AAMA-FGIA 標準專頁與 machine-readable index
- 3003-H14、3004-H12、6063-T5、6005-T5、6105-T5 個別材料頁
- `3003-H14-vs-3004-H12` 與 aluminum panel flatness / oil canning 工程筆記
- AAMA 611 陽極處理
- CNS 10007 / CNS 1247 熱浸鍍鋅
- 玻璃、structural silicone、gasket、stone、skylight 等 building-envelope 領域

## Copyright / licensing boundary

ASTM、AAMA-FGIA、ISO、CNS 與其他第三方標準可能受著作權或授權條款限制。本 repository 原則上只保存：

- 標準編號與版本資訊
- 適用範圍與工程摘要
- 必要的 cross-reference
- 合法可引用的最低充分內容
- 官方或合法來源連結
- 自行整理的工程解讀與注意事項

不把付費／受限制標準全文或未授權 PDF 直接 commit 到公開 repository。

## Status

可信 baseline 與第一批 structural-calculation methodology 已建立。後續維護以「先補 primary evidence → 再擴充 canonical knowledge → 最後建立 machine-readable index」為原則。