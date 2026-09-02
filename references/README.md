# 來源資料（References）

本目錄保存**可公開散布**的來源 dossier、provenance、版本、適用範圍、限制與查證資訊；不是未整理文件或私人專案資料的堆放區。

## 分類

- [`standards/`](standards/)：CNS / ASTM / AAMA-FGIA / ISO 等正式標準的 public metadata / current-edition / status routing dossier。
- [`government/`](government/)：主管機關、建研所、政府實驗室等公開資料。
- `manufacturers/`：材料／系統製造商正式且可公開引用的技術資料；需要時再建立。
- `research/`：公開學術／研究資料；需要時再建立。
- `public-cases/`：只有案例本身已由公開來源揭露且可合法引用時使用。
- [`github-projects/`](github-projects/)：帷幕牆／建築外殼公開 GitHub 軟體與工程專案索引；一律為 **NON-NORMATIVE implementation reference**。

## 標準版本 ownership

`references/standards/` 是標準 **current edition / status / official URL / verified_at** 的優先 canonical owner。

Knowledge pages 負責工程解讀與使用方法；若同一標準被多個 knowledge pages 使用，這些頁面應連回同一 dossier，而不是各自保存版本快照。

例如 structural silicone family：

- [`standards/astm-c1184.md`](standards/astm-c1184.md)
- [`standards/astm-c1401.md`](standards/astm-c1401.md)
- [`standards/astm-c1135.md`](standards/astm-c1135.md)

材料 CNS routing：

- [`standards/cns-2253.md`](standards/cns-2253.md)
- [`standards/cns-2257.md`](standards/cns-2257.md)

## Public dossier 最低欄位

每份 dossier 應盡量記錄：

- source / organization；
- title / standard number；
- edition / revision；
- status；
- official source URL；
- access / verification date；
- authority type；
- applicable scope；
- knowledge routing；
- limitations / do-not-assume；
- copyright / reuse restriction（若已知）。

## GitHub 專案索引

[`github-projects/README.md`](github-projects/README.md) 只做總 index；詳細 shortlist 依用途拆分，讓 AI progressive reading：

- façade automation / BIM；
- building performance；
- structural analysis / calculation；
- structural connections / glass；
- inspection / monitoring。

GitHub repository 宣稱實作某 standard / code，只代表需要進一步驗證的 software claim；工程結論仍須回 current primary source。

## 私人資料禁止事項

**不得建立 private-project dossier。**

非公開專案文件、維護者對私有施工圖的觀察、直接參與者口頭確認、內部審查紀錄、私人教育訓練原檔或其他 private provenance 應留在 repository 外。

若 private source 產生可泛化 lesson，先去識別，再以 public source 重新驗證後寫入 `knowledge/`；不要把 private source 改名後放進 `references/`。

## 著作權

受版權保護標準全文不放入本公開 repository。Reference dossier 只保存允許公開的 metadata、scope、routing 與 repository-authored commentary。

人類可讀摘要依 [`../LANGUAGE.md`](../LANGUAGE.md) 使用繁體中文（台灣）為主。