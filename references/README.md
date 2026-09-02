# 來源資料（References）

本目錄保存**可公開散布**的來源 dossier、provenance、版本、適用範圍、限制與查證資訊；不是未整理文件或私人專案資料的堆放區。

建議分類：

- `standards/`：CNS / ASTM / AAMA-FGIA / ISO 等正式標準的公開 metadata / routing dossier
- `government/`：主管機關、建研所、政府實驗室、TAF 等公開資料
- `manufacturers/`：材料／系統製造商正式且可公開引用的技術資料
- `research/`：公開學術與研究報告
- `public-cases/`：只有在案例本身已由公開來源揭露且可合法引用時使用
- [`github-projects/`](github-projects/)：與帷幕牆／建築外殼相關的公開 GitHub 工程與軟體專案參考索引；只作 **NON-NORMATIVE software / implementation reference**，不得取代 governing code、正式標準、project design basis 或專業工程判斷

**不得建立 private-project dossier。** 非公開專案文件、維護者對私有施工圖的觀察、直接參與者口頭確認、內部審查紀錄或其他 private provenance 應留在 repository 外的私人工作流程。

每份 public dossier 應盡量記錄：

- 來源／組織（source / organization）
- 標題／標準編號（title / standard number）
- 版本／修訂（edition / revision）
- 來源網址（source URL）
- 存取／查證日期（access / verification date）
- authority type
- 適用範圍（applicable scope）
- 重要觀察（observations）
- 限制／不可推論事項（limitations / do-not-assume）
- 著作權／再利用限制（copyright / reuse restriction，若已知）

同一標準的 current edition / status 宜由單一 canonical dossier 或 standard page 維護，其他 knowledge pages 只引用該 routing，避免版本 drift。

GitHub 專案若宣稱實作某項 standard / code，該宣稱只代表需要進一步查證的 software claim；若要形成工程結論，仍須回到 current primary source 獨立驗證。

人類可讀摘要依 [`../LANGUAGE.md`](../LANGUAGE.md) 以繁體中文（台灣）為主；來源原始標題、標準正式名稱與必要技術術語保留原文。

受版權保護標準全文不放入本公開 repository。