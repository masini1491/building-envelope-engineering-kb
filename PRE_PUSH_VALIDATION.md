# 推送前驗證門（Pre-push Validation Gate）

本檔是 `building-envelope-engineering-kb` 的 **repository-specific pre-push validation recipe**。只在準備寫入本 repository 時載入；一般工程問答不需要。

共通 methodology 不在此重複維護：Action Contract Closure／AI Context 由 selected Playbook `AI_CONTEXT.md` 擁有；repository identity／write／permission 由 `REPOSITORY_EXECUTION.md` 擁有；GitHub object mutation／Actions mechanics 由 `GITHUB_OPERATIONS.md` 擁有；runtime／materialization capability 由 `CHATGPT_RUNTIME_EXECUTION.md` 擁有；snapshot／evidence identity 由 `INFORMATION_INTEGRITY.md` 擁有；validation／completion semantics 由 `DEBUG_VALIDATION.md` 擁有。本檔只追加本 KB 實際要跑哪些 deterministic checks、何時需要 generated artifact，以及 remote confirmation 的 local contract。

## 核心預設

在 shared pre-action contract 已 closure 的前提下，先收斂本次 candidate，再執行下列最低充分 local checks；不要把 GitHub Actions 當成第一個互動式除錯 surface。若 current capability不足以執行某個 required local check，保留該 evidence gap，不把「未執行」寫成 PASS 或 repository failure。

## 決定性執行機會掃描（Execution Opportunity Scan）

是否由目前 ChatGPT/runtime 執行 repository-owned validator、generator、test或其他 deterministic workload，直接依 selected Playbook `CHATGPT_RUNTIME_EXECUTION.md` → `Execution Opportunity Scan`／`Execution Capability Gate`。本 KB 不另建第二份 capability methodology。

本 repository 已知的主要 deterministic surfaces包括：

- `scripts/preflight_markdown_headings.py`
- `scripts/build_knowledge_manifests.py`
- `scripts/check_cross_agent_adapters.py`
- `scripts/check_ai_fastpath.py`
- `scripts/validate_repo.py`
- `tests/engineering_calc/`
- `tests/ai_routing/`

只有 current diff／validation contract需要時才執行或 materialize 對應 surface；存在工具不代表每次全部必跑。

## 單一快照一致性（Snapshot Consistency Guard）

多檔 validator／test 所需 snapshot identity與 same-revision要求，直接依 selected Playbook `INFORMATION_INTEGRITY.md` → `Snapshot Consistency Guard`。本地附加要求只有：repository-owned validator／test若納入同一 run，必須來自該 run 所宣稱的同一 KB revision；無法建立時不得宣稱該 revision 的 full validation PASS。

## 執行能力門

Runtime、dependency、filesystem、network與 materialization capability直接依 selected Playbook `CHATGPT_RUNTIME_EXECUTION.md`。本 KB 不從「模型會寫 Python」推論 runtime可用，也不因 local execution unavailable 就把 repository本身判成 FAIL。

## 推送前流程

在 current authorized candidate 上依實際 diff執行：

1. **人類可讀 Markdown 有變更**：若完整 repository validation暫時不可用，但 changed-file snapshot可可靠 materialize，至少執行：

   ```bash
   python scripts/preflight_markdown_headings.py <changed.md> [...]
   ```

2. **新增、刪除或移動 `knowledge/**/*.md`**：先更新 generated routing artifact：

   ```bash
   python scripts/build_knowledge_manifests.py
   ```

3. **完整 repository snapshot與必要 Python dependency可用**：以目前 CI baseline做 local-equivalent deterministic validation：

   ```bash
   python -m unittest discover -s tests/engineering_calc -p "test_*.py"
   python -m unittest discover -s tests/ai_routing -p "test_*.py"
   python scripts/check_cross_agent_adapters.py
   python scripts/build_knowledge_manifests.py --check
   python scripts/check_ai_fastpath.py
   python scripts/validate_repo.py
   ```

   `validate_repo.py` 的 JSON Schema檢查使用 `jsonschema`；CI current baseline為 Python 3.12。若 local environment缺 dependency，應標示該 check未執行，而不是自行降低 assertion。

4. **只改特定 tooling／routing surface**：可先跑與 diff直接相關的 targeted check縮短 feedback loop，但 targeted PASS不取代本 Stage／current recipe真正要求的較大 validation scope。

5. Candidate準備完成後，依 shared repository／GitHub contract重新確認 destination ref沒有 material drift，再進行 authorized mutation。Multi-file coherent change優先形成單一 candidate commit。

## 無法做完整 pre-push validation 時

若目前 session無法可靠 materialize full canonical snapshot：

- 只對能建立 exact identity的 changed files／validator input做 targeted deterministic check；
- Markdown changed-file snapshot可可靠建立時，優先執行 heading preflight；
- AI routing／bootstrap／manifest contract有變更時，至少確認 changed routing target、stable pointer與 affected deterministic checker contract；若 corresponding test/runtime不可執行，明確保留 limitation；
- 不以 mixed-revision、model-reconstructed canonical bytes或未執行 command宣稱 full validation PASS；
- Candidate仍應保持單一 bounded batch，remote CI作為後續 independent confirmation，而不是用多個猜測式 push逐步除錯。

這是 capability fallback，不改變 required validation的語意，也不把較窄 evidence升格成 repository-wide PASS。

## 持續整合（CI）定位

Current remote enforcement 是 `.github/workflows/validate-repo.yml` 的 **Repository 自動驗證**。它目前在 `main` push／pull request執行與上方 local-equivalent baseline對應的 engineering-calculator tests、AI-routing tests、cross-agent adapter check、knowledge manifest check、AI fast-path check與 repository validation。

GitHub Actions 的 run／tested commit／PASS scope與 completion semantics依 selected Playbook `GITHUB_OPERATIONS.md`／`DEBUG_VALIDATION.md`；workflow success 是 remote independent confirmation，不取代 candidate形成前能執行的 deterministic checks。完成 repository mutation 後，仍需 canonical remote read-back證明 current `main` 實際包含 intended bounded change。

> 核心原則：**Shared Playbook 擁有共通 validation／execution methodology；本檔只擁有 building-envelope-engineering-kb 的 deterministic validation recipe。**
