# 新聊天室初始化

本 repository 是以台灣建築外殼工程實務為核心的公開技術知識庫。本檔是 AI 使用本 repository 時的**精簡啟動層（bootstrap）**；目標是在不犧牲工程治理的前提下，避免每個問題都先載入整套治理文件。

## 最低啟動規則

所有任務先遵守以下最低規則：

1. **證據優先**：先取得足以支持本次結論的最低充分 evidence，再下工程判斷。
2. **不得補猜工程數值**：Repository 沒有可靠設計數值、適用條件、係數、材料性質或等價證據時，明確標示未知／待驗證；不得自行生成看似合理的值。
3. **單一權威歸屬**：同一工程結論、標準版本或狀態以 canonical owner 為準，其他頁只作 routing / cross-reference。
4. **公開安全**：不得把私人專案名稱、圖號、尺寸、荷載、節點、截圖或非公開 provenance 寫入 public KB。
5. **漸進式讀取**：不要預設掃完整個 repository；先路由，再讀回答問題所需的最低必要頁面。
6. **來源分層**：法規／正式標準／政府資料／製造商資料／工程實務／推論不可混成同一證據層級。
7. **繁體中文（台灣）優先**：除非使用者另有要求，回答依 `LANGUAGE.md` 的原則；正式標準名、材料牌號、schema key、公式與必要英文工程術語保留原文。

## 依任務選擇載入層級

### 一般工程問答／查詢

預設採下列最短路徑：

1. 讀本 `CHAT_INIT.md`。
2. 讀 [`indexes/knowledge-index.json`](indexes/knowledge-index.json)，用 `id / aliases` 選出最可能的 domain。
3. **只讀該 domain 的 `manifest`**（位於 `indexes/knowledge-pages/`），先比對 `slug / path / section`。
4. 若 manifest 已直接命中一個明確 leaf page，直接讀該頁；**不必先經過 router**。
5. 若題意仍有歧義、跨多個 subdomain，或需要先理解 domain 邊界，才讀 `entrypoint / router`。
6. 需要標準版本、來源、scope 或 provenance 時，再讀 [`indexes/standards-index.json`](indexes/standards-index.json) 與對應 `references/` dossier。
7. Repository evidence 不足或 freshness 不明時，再查 current primary source。

**一般明確問答不需要無條件完整載入 `README.md`、`AGENTS.md` 與 `AI_RESPONSE_CONTRACT.md`。**

### 計算書／圖面／規範審查

除上述最低內容外，再讀：

- [`AI_RESPONSE_CONTRACT.md`](AI_RESPONSE_CONTRACT.md)；
- 對應 review / methodology canonical page；
- 若涉及完整結構審查，優先從 `knowledge/structural-design/review/` 路由。

回答呈現採結論優先、最低充分展開；`PASS / WARNING / FAIL / INCOMPLETE / NOT_APPLICABLE` 必須 scope-qualified，局部 `PASS` 不得包裝成整體系統安全。

### 儲存庫（Repository）維護／新增／修改內容

必須再讀：

- [`AGENTS.md`](AGENTS.md) — authority、canonical ownership、公開安全、metadata 與維護治理；
- [`LANGUAGE.md`](LANGUAGE.md) — 若修改人類可讀內容；
- 相關 `templates/`、`schemas/`、`scripts/validate_repo.py` — 依任務需要載入。

維護時以 GitHub `main` 為 source of truth；修改前先 read-back current remote，避免依舊聊天或 cached copy 覆蓋新內容。

新增、刪除或移動 `knowledge/**/*.md` 後，執行：

```bash
python scripts/build_knowledge_manifests.py
```

再執行 repository validation。`indexes/knowledge-pages/*.json` 是**由路徑自動產生的 routing artifact**，不得手工塞入工程結論或 verification status。

## 路由原則

- `knowledge-index.json` 只負責選 domain。
- `indexes/knowledge-pages/<domain>.json` 只負責在該 domain 內選 page。
- `entrypoint` 是 domain 的預設第一頁；只有明確標示 `router` 的項目才代表真正 router page。
- Page manifest 只保存 `path / slug / kind / section`；工程內容、驗證狀態與 evidence 必須回到目標頁本身。
- 若 leaf page 已精準命中，就不要為了流程完整而多讀一層 router。
- 只有當現有頁面明確 cross-reference、問題跨 domain，或缺少必要 evidence 時，才繼續開下一頁。
- 不因某頁列出很多相關連結，就自動全部載入。

核心原則：**先用最小 routing metadata 找到正確 canonical owner，再只讀足以回答本題的內容。**
