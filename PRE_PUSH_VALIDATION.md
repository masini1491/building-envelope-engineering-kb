# 推送前驗證門（Pre-push Validation Gate）

本檔只用於 AI／維護者準備把 repository 變更寫入 GitHub 時；一般工程問答不需載入。目標是把可預期的 deterministic failure 留在 remote push 之前處理，避免 ChatGPT 維護過程以多個中間 commit 反覆觸發 GitHub Actions failure 與 Email 通知。

## 核心預設

**不要把 GitHub Actions 當成互動式除錯器。**

同一維護任務應先完成必要檢查與修正，再以單一 batched commit／最少必要 push 寫入 `main`。不得採用「先 push 看 CI → 修一點再 push → 再看 CI」作為預設工作流程。

## 決定性執行機會掃描（Execution Opportunity Scan）

若目前已讀範圍直接出現 repository-owned validator、generator、parser、calculator、test 或其他可界定輸入／輸出與失敗語意的 deterministic workload，應先做最低充分 execution opportunity scan，而不是預設把 GitHub Actions 當成第一個 execution surface。

只有候選同時具有實際價值且本任務允許執行時，才檢查該候選真正需要的 runtime、dependency、filesystem 或 network capability；不得為了盤點「ChatGPT 能做什麼」而完整掃描 repository 或 sandbox。

若可由 exact commit／tree 的 canonical snapshot 在本 session 安全重現 deterministic check，優先於 remote push 前執行，以降低人工錯誤與 remote debugging noise。Sandbox 只作暫時計算 surface；執行結果是 evidence，不取得 GitHub persistence／write authority，也不成為新的 source of truth。

## 執行能力門

準備執行 repository validator 前，先確認本次 AI session 實際具備所需能力，不從「模型會寫 Python」推論「目前環境一定能執行 Python」。

至少依任務確認：

1. Python runtime 可實際執行；
2. 必要 dependency 可用；
3. validator 所需的 canonical repository snapshot／filesystem 已完整取得；
4. 只有檢查本身需要時，才要求 network、Git CLI 或其他外部服務。

Retrieval capability、GitHub connector capability 與 local execution capability 必須分開判斷。

若缺少 runtime、dependency 或完整 repository snapshot，應明確標示 **pre-push validation unavailable**；不得把「本 session 無法執行」說成 repository validation failure，也不得假裝已跑過檢查。

## 推送前流程

在 remote write 前，依目前可用能力執行：

1. remote read-back 最新 GitHub `main`，確認 base 未漂移；
2. 完成所有預定修改，包含 deterministic generated artifact；
3. 若有新增、刪除或移動 `knowledge/**/*.md`，先執行：

```bash
python scripts/build_knowledge_manifests.py
```

4. 若完整 repository snapshot 與 Python runtime 可用，至少執行：

```bash
python scripts/build_knowledge_manifests.py --check
python scripts/validate_repo.py
```

5. 任一 deterministic check failure 時，**先在 remote push 前修正並重跑**；不得為了取得 CI 訊息而先把已知 failure 推到 `main`。
6. 所有預定檔案與 generated artifact 應盡量合併為**單一 batched commit**，避免每個檔案各自形成會觸發 CI 的中間 commit。
7. push 後仍保留 GitHub Actions 作為 remote independent confirmation；CI success 後再 remote read-back `main` 完成任務。

## 無法做完整 pre-push validation 時

ChatGPT 的某些 GitHub 維護 session 可能只有 connector remote-write 能力，沒有完整 repository filesystem。此時：

- 仍先 remote read-back 所有受影響 canonical files；
- 以 deterministic generator／validator contract 做最低必要靜態檢查；
- **一次完成所有可合理確認的修改，再做單一 remote commit**；
- 不建立多個「試跑 CI」中間 commit；
- 第一次 remote CI 若失敗，再讀取實際 failure log，將修正收斂成下一個單一 commit；不要逐條猜測式 push。

這個 fallback 不能宣稱等同完整 pre-push validation，但能降低 CI failure burst 與通知噪音。

## 持續整合（CI）定位

目前 `Repository 自動驗證` 保留在 `main` push／pull request，角色是**獨立的 remote enforcement**，不是主要除錯迴圈。

是否未來改成 local-only、manual、path-filtered 或其他 placement，應依實際 mutation path、多人協作、CI 成本與通知噪音重新評估；validator 存在不代表永遠必須固定在同一 execution placement。

> 原則：**先在能控制的地方把 deterministic error 消掉，再讓 CI 驗證已收斂的候選版本；不要用一排 remote failure 取代本來可以在 push 前完成的檢查。**
