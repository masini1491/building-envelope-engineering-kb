# 新聊天室初始化

本 repository 是以台灣建築外殼工程實務為核心的公開技術知識庫。本檔是 AI 使用本 repository 時的**精簡啟動層（bootstrap）**；目標是在不犧牲工程治理的前提下，讓一般工程問答以最低充分 Context 直接命中 current canonical authority。

## 最低啟動規則

所有任務先遵守以下最低規則：

1. **證據優先**：先取得足以支持本次結論的最低充分 evidence，再下工程判斷。
2. **不得補猜工程數值**：Repository 沒有可靠設計數值、適用條件、係數、材料性質或等價證據時，明確標示未知／待驗證；不得自行生成看似合理的值。
3. **單一權威歸屬**：同一工程結論、標準版本或狀態以 canonical owner 為準，其他頁只作 routing / cross-reference。
4. **公開安全**：不得把私人專案名稱、圖號、尺寸、荷載、節點、截圖或非公開 provenance 寫入 public KB。
5. **漸進式讀取**：不要預設掃完整個 repository；先路由，再讀回答問題所需的最低必要頁面。
6. **來源分層**：法規／正式標準／政府資料／製造商資料／工程實務／推論不可混成同一證據層級。
7. **繁體中文（台灣）優先**：除非使用者另有要求，回答依 `LANGUAGE.md` 的原則；正式標準名、材料牌號、schema key、公式與必要英文工程術語保留原文。

## 共通回覆契約（Shared reporting）

形成 substantive user-facing engineering reply 時，shared reporting 是 adoption-level 的窄化例外，不因一般工程問答維持 project-native route 而失效：

1. 只 bounded-read `AGENTS.md` 的 current adoption declaration，取得唯一的 `Playbook baseline`；不要因此完整載入 governance。
2. Baseline 是 moving ref 時，以最低成本解析足以支持本次 reporting action 的 exact revision；同一 session 已驗證且沒有 material freshness trigger 時可重用。
3. 直接讀該 revision 的 `REPORTING.md`，套用共通 result-first、scope fidelity、progress integrity、reporting timestamp 與 pre-send contract。
4. 這個 reporting-only direct-leaf **不會**啟用 shared `CHAT_INIT.md`、Git／validation／research／Codex execution 或其他 Playbook owners，也不擴張任何 Task／write／execution／completion authority。
5. 只有 task 需要 KB-specific engineering presentation rule 時，再讀 `AI_RESPONSE_CONTRACT.md`；它只保存 project-specific delta，不是第二份 shared reporting owner。

## 儲存庫讀取取得與復原

本次問題 materially 依賴 current repository content 時，優先使用 repository-native read；首選機制不可用時，可依最低充分 canonical path 降級：

`repository-native read → public canonical read / direct canonical download → user-mediated exact artifact / minimum canonical section → REPOSITORY READ BLOCKED`

Fallback 只改變 transport，不改變 source authority、task authority或 write authority。若 source identity 會影響判斷，保留可得的 repository／ref／revision／path／hash 等最低充分 evidence；無法可靠建立 current canonical content 時，不得用舊聊天、cache、AI memory、search hit或相似工程內容補成 repository fact。同一 acquisition mechanism 已證實 blocked 時，不做無界等價 retry。

## 依任務選擇載入層級

### 一般工程問答／查詢

預設採下列最短路徑：

1. 讀本 `CHAT_INIT.md`。
2. 讀 [`indexes/knowledge-index.json`](indexes/knowledge-index.json)，用 `id / aliases` 選出最可能的 domain。
3. 只讀該 domain 的 `indexes/knowledge-pages/<domain>.json`，用 `slug / path / section` 選擇最低必要 page。
4. Manifest 已唯一命中 leaf page時直接讀 leaf；題意仍有歧義、跨多個 subdomain或需要理解 domain 邊界時，才讀 `entrypoint / router`。
5. 需要標準版本、來源、scope或 provenance 時，再讀 [`indexes/standards-index.json`](indexes/standards-index.json) 與對應 `references/` dossier。
6. Repository evidence不足或 freshness不明時，再查 current primary source。

Repository-level absence claim需要與 claim scope相稱的 bounded coverage；單一 manifest／search未命中只代表 checked scope未找到，不能單獨證明不存在。Search／filename／snippet命中也只作 discovery evidence，最後仍回 current canonical owner判斷 authority與語意。Coverage不足時使用 `NOT FOUND IN CHECKED SCOPE` 或等價 evidence-bounded wording。

**一般明確問答不需要無條件完整載入 `README.md`、`AGENTS.md`、`AI_RESPONSE_CONTRACT.md` 或 shared AI Development Playbook 的其他 owners；上方 `REPORTING.md` reporting-only direct-leaf 例外不等於 shared Playbook activation。**

### 計算書／圖面／規範審查

除上述最低內容外，再讀：

- [`AI_RESPONSE_CONTRACT.md`](AI_RESPONSE_CONTRACT.md)；
- 對應 review / methodology canonical page；
- 若涉及完整結構審查，優先從 `knowledge/structural-design/review/` 路由；
- 若使用者要求審查結果跨聊天室、跨 revision、長期保存或後續持續 reconciliation，讀 [`knowledge/structural-design/review/calculation-review-record.md`](knowledge/structural-design/review/calculation-review-record.md)；一次性局部核算不強制建立 record；
- 若需要獨立數值重算、reported/recomputed comparison或 calculation-chain reconciliation，再讀 [`scripts/engineering_calc/README.md`](scripts/engineering_calc/README.md)，並在 execution capability成立後使用其 AI-facing adapter。只要 `review.py` 已支援該 `check_type`，預設優先經 adapter執行；只有 adapter不支援時才 bounded-read對應 module作明確 fallback。Runtime／filesystem無法執行時，不得把「已讀到程式碼」宣稱成「已完成 deterministic 核算」。

回答呈現採結論優先、最低充分展開；`PASS / WARNING / FAIL / INCOMPLETE / NOT_APPLICABLE` 必須 scope-qualified，局部 `PASS` 不得包裝成整體系統安全。Calculator 的 `COMPUTED / MATCH / MISMATCH / INCOMPLETE_INPUT / UNSUPPORTED_MODEL` 等 execution／comparison status 不得與工程 acceptance status混成同一維度。

### 儲存庫（Repository）維護／新增／修改內容

Repository maintenance 是 shared AI Development Playbook 的 activation trigger。先讀 [`AGENTS.md`](AGENTS.md) 取得 current project governance／adoption state，再依 selected shared baseline 關閉本次 action真正需要的共通 contract；本檔不重複 Git／write／permission／runtime／validation／completion mechanics。

本 repository 的 local conditional owners：

- 修改人類可讀內容 → [`LANGUAGE.md`](LANGUAGE.md)
- 新增、整理、吸收、匯入或重構 knowledge → [`KNOWLEDGE_INGESTION.md`](KNOWLEDGE_INGESTION.md)，並先執行「新增知識決策門」
- 準備第一次 remote write → [`PRE_PUSH_VALIDATION.md`](PRE_PUSH_VALIDATION.md)
- Template／schema／router／validator 變更 → 只讀本次修改直接相關的 local owner／tooling
- 新增、刪除或移動 `knowledge/**/*.md` → 執行 `python scripts/build_knowledge_manifests.py`；`indexes/knowledge-pages/*.json` 只作 generated routing artifact，不得手工加入工程結論或 verification status

### 共通人工智慧開發治理的條件式啟用

一般工程問答、knowledge retrieval、標準／材料／構造查詢與一般工程 evidence research 維持 project-native hot path：

`CHAT_INIT → knowledge-index → domain manifest → canonical leaf → sufficient then STOP`

只有 repository maintenance、Git／write、deterministic execution／materialization、validation／debugging、AI context／retrieval architecture、research／architecture workflow governance或其他共通 AI development／repository workflow治理型任務，才讀 `AGENTS.md` 取得 current Playbook adoption state並 activate shared baseline。

Shared baseline activation後的 exact-revision resolution、owner loading、Action Contract Closure與 completion evidence由 AI Development Playbook current canonical owners負責；本 repository只保留自己的 engineering knowledge、public safety、canonical ownership、routing與其他 project-specific authority。

## 已驗證內容重用與新鮮度

同一 session 已確認 current repository identity、domain manifest／router／canonical leaf後，沒有 material freshness或 scope trigger時直接 reuse，不為 routing ceremony重複 fetch。

Material trigger包括：使用者明確要求 latest/current或表示 KB 已更新、已知 repository mutation、跨階段續審、task scope／owner materially改變，或 currentness會改變工程結論／completion claim。

- HEAD unchanged：沿用已確認 working context。
- HEAD changed：先做 bounded diff，只重讀會影響本題 routing／authority／engineering conclusion／validation 的 changed owner。
- 固定 SHA／tag baseline：不因 upstream `main` 前進自行升級。
- Probe unavailable：保留 freshness gap；只有 current decision materially依賴 latest authority時才停止依賴該 claim。

## 路由原則

- `knowledge-index.json` 只負責選 domain。
- `indexes/knowledge-pages/<domain>.json` 只負責在該 domain內選 page。
- `entrypoint` 是 domain預設第一頁；只有明確標示 `router` 的項目才代表真正 router page。
- Page manifest只保存 `path / slug / kind / section`；工程內容、驗證狀態與 evidence回到目標 canonical page。
- Exact leaf已精準命中時，不為流程完整增加 routing hop；只有 cross-reference、跨 domain或 evidence缺口才繼續擴張 retrieval。
- **Sufficient then STOP**：已取得支持本題結論的最低充分 canonical evidence後停止擴張，不把「多讀幾頁」當成可靠度本身。

核心原則：**先用最小 routing metadata 找到正確 canonical owner，再只讀足以回答本題的內容。**
