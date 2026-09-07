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

## 儲存庫讀取取得與復原

當本次問題需要 current repository content，而首選 GitHub／repository-native read path 不可用時，應只降低**取得機制**，不得降低 authority：

`repository-native connector → public canonical GitHub/raw read → minimum user-supplied canonical section → REPOSITORY READ BLOCKED`

- 本 repository 為 public 時，connector unavailable 後可改用官方 GitHub／raw canonical read-only surface；fallback 不授權任何 repository mutation。
- 若仍無法取得 current canonical content，只要求本次 decision 所需的最低必要 file／section，不預設要求使用者貼完整 repository。
- 無法可靠建立 current state 時標示 `REPOSITORY READ BLOCKED`／等價 evidence gap；不得用舊聊天、cache、模型 memory 或相似工程內容補成 repository fact。

核心原則：**Fail over the read mechanism, not the authority.**

## 依任務選擇載入層級

### 一般工程問答／查詢

預設採下列最短路徑：

1. 讀本 `CHAT_INIT.md`。
2. 讀 [`indexes/knowledge-index.json`](indexes/knowledge-index.json)，用 `id / aliases` 選出最可能的 domain。
3. **只讀該 domain 的 `manifest`**（位於 `indexes/knowledge-pages/`），先比對 `slug / path / section`。
4. 若 manifest 已直接命中一個明確 leaf page，直接讀該頁；**不必先經過 router**。
5. 若題意仍有歧義、跨多個 subdomain，或需要先理解 domain 邊界，才讀 `entrypoint / router`。
6. 需要標準版本、來源、scope 或 provenance 時，再讀 [`indexes/standards-index.json`](indexes/standards-index.json) 與對應 `references/` dossier。
7. 若問題要求判斷「repository 有沒有／缺少什麼／尚未支援什麼」，不得只因目前已讀 domain、單一 manifest 或一次 search 沒命中就宣稱不存在。先以 `knowledge-index → 合理 domain manifest／canonical owner → 可用 repository search` 做與 claim scope 相稱的 bounded existence check；找到充分 positive hit 後可停止該分支。最終回答若仍要提出 material negative claim，送出前再逐條 reconciliation；coverage 不足時使用 `NOT FOUND IN CHECKED SCOPE` 或等價的 evidence-bounded wording。
8. Repository search／filename／snippet 命中只作 discovery evidence；先辨識 owner、authority class 與 currentness，再回 current canonical target。**`found` 不等於 authoritative/current，正如 `not found` 不等於 absent。**
9. Repository evidence 不足或 freshness 不明時，再查 current primary source。

**一般明確問答不需要無條件完整載入 `README.md`、`AGENTS.md` 與 `AI_RESPONSE_CONTRACT.md`。**

### 計算書／圖面／規範審查

除上述最低內容外，再讀：

- [`AI_RESPONSE_CONTRACT.md`](AI_RESPONSE_CONTRACT.md)；
- 對應 review / methodology canonical page；
- 若涉及完整結構審查，優先從 `knowledge/structural-design/review/` 路由；
- 若使用者要求審查結果跨聊天室、跨 revision、長期保存，或後續持續 reconciliation，直接讀 [`knowledge/structural-design/review/calculation-review-record.md`](knowledge/structural-design/review/calculation-review-record.md)；持久化是選配，不需要為一次性局部核算強制建立 record；
- 若需要獨立數值重算、reported/recomputed comparison 或 calculation-chain reconciliation，再讀 [`scripts/engineering_calc/README.md`](scripts/engineering_calc/README.md)，並在確認目前 execution capability 足夠後使用其 AI-facing adapter。**只要 `review.py` 已支援該 `check_type`，預設必須優先經 adapter 執行，不直接繞到底層 helper 自行拼接；只有 adapter 不支援時才可 bounded-read 對應 module 作明確標示的 fallback。**若 runtime／filesystem 無法執行，不得把「已讀到程式碼」宣稱成「已完成 deterministic 核算」。

回答呈現採結論優先、最低充分展開；`PASS / WARNING / FAIL / INCOMPLETE / NOT_APPLICABLE` 必須 scope-qualified，局部 `PASS` 不得包裝成整體系統安全。Calculator 的 `COMPUTED / MATCH / MISMATCH / INCOMPLETE_INPUT / UNSUPPORTED_MODEL` 等 execution／comparison status 不得與工程 acceptance status 混成同一維度。

### 儲存庫（Repository）維護／新增／修改內容

必須再讀：

- [`AGENTS.md`](AGENTS.md) — authority、canonical ownership、公開安全、metadata 與維護治理；
- [`LANGUAGE.md`](LANGUAGE.md) — 若修改人類可讀內容；
- 相關 `templates/`、`schemas/`、`scripts/validate_repo.py` — 依任務需要載入。

**若任務涉及新增、整理、吸收、匯入或重構 knowledge，建立任何新的 `knowledge/**/*.md` 前必須先讀 [`KNOWLEDGE_INGESTION.md`](KNOWLEDGE_INGESTION.md) 並執行其中的「新增知識決策門」。預設優先更新既有 canonical owner，不以新增檔案作為預設動作。**

**任何準備寫入 GitHub 的 repository 維護任務，在第一次 remote write 前必須讀 [`PRE_PUSH_VALIDATION.md`](PRE_PUSH_VALIDATION.md) 並執行「推送前驗證門」；預設先收斂 deterministic checks，再以單一 batched commit／最少必要 push 寫入，GitHub Actions 只作 remote independent confirmation。**

維護時以 GitHub `main` 為 source of truth；修改前先 read-back current remote，避免依舊聊天或 cached copy 覆蓋新內容。

新增、刪除或移動 `knowledge/**/*.md` 後，執行：

```bash
python scripts/build_knowledge_manifests.py
```

再執行 repository validation。`indexes/knowledge-pages/*.json` 是**由路徑自動產生的 routing artifact**，不得手工塞入工程結論或 verification status。

## 儲存庫新鮮度補查（Freshness Probe）

長期問答／審查若跟隨 floating `main`，不要把 session 開始時讀到的 repository identity 永久視為 current。當使用者明確表示 KB 已更新，或在跨階段續審、repository mutation、completion acceptance／最終工程結論等 material boundary 前，而 currentness 會影響判斷時，先做一次低成本 HEAD probe。

- HEAD unchanged：沿用已確認 working context，不全文重讀。
- HEAD changed：先做 bounded diff，僅重讀會影響本次 routing／authority／engineering conclusion／validation 的 changed owner。
- 固定 SHA／tag baseline 不因 upstream `main` 前進而自行升級。
- Probe unavailable 時保留 freshness gap；只有 current decision materially 依賴最新 repository authority 時才 STOP，否則在標示 limitation 下維持最低風險工作。

核心原則：**Check identity cheaply, reload selectively.**

## 路由原則

- `knowledge-index.json` 只負責選 domain。
- `indexes/knowledge-pages/<domain>.json` 只負責在該 domain 內選 page。
- `entrypoint` 是 domain 的預設第一頁；只有明確標示 `router` 的項目才代表真正 router page。
- Page manifest 只保存 `path / slug / kind / section`；工程內容、驗證狀態與 evidence 必須回到目標頁本身。
- 若 leaf page 已精準命中，就不要為了流程完整而多讀一層 router。
- 只有當現有頁面明確 cross-reference、問題跨 domain，或缺少必要 evidence 時，才繼續開下一頁。
- 不因某頁列出很多相關連結，就自動全部載入。

核心原則：**先用最小 routing metadata 找到正確 canonical owner，再只讀足以回答本題的內容。**
