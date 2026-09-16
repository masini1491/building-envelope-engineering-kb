# 啟動轉接（GitHub Copilot）

本檔只提供 GitHub Copilot 的 repository bootstrap 相容性。它不是第二份治理文件，不建立新的 canonical authority，也不變更 `AGENTS.md` 所宣告的 Project AI mode、permission 或 write scope。

## 啟動路由

- 處理本 repository 的任何任務時，先讀 `CHAT_INIT.md`，再依其中的 task classification 與 minimum-sufficient retrieval routing 執行。
- 不要預設掃描整個 repository，也不要為一般工程問答固定載入 `README.md`、`AGENTS.md`、`AI_RESPONSE_CONTRACT.md`、全部 manifests 或全部 `knowledge/`。
- 一般工程問答維持 `CHAT_INIT → knowledge-index → domain manifest → canonical leaf → sufficient then STOP`。
- Repository 維護、修改、Git／write、validation 或 AI context／retrieval architecture 任務，依 `CHAT_INIT.md` 再讀 `AGENTS.md` 與其指向的最低充分 owners。
- 若 runtime 同時載入其他 agent-instruction surfaces，重疊的 bootstrap／routing 只視為 compatibility handoff，不形成平行 authority。
- 本 adapter 不會改變本 repository 的 `Project AI mode: ChatGPT-Only`；相容性只讓此 host discover、read、route、follow current canonical governance，不會讓此 host 自動成為 canonical executor。
- 本檔存在不代表 task authorization、repository write authority、runtime execution authority、credential／deployment authority 或 completion evidence。

## 權威邊界

若本檔與 `CHAT_INIT.md`、`AGENTS.md` 或其路由到的 current canonical owner 發生衝突，以 target repository 的 current canonical authority 為準；不要在本檔複製或維護第二份規則。
