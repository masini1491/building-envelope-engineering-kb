# 新增知識決策門（Knowledge Ingestion Gate）

本檔只用於**新增、整理、吸收、匯入或重構知識**的維護任務；一般工程問答不需載入。本規則的目的，是讓 repository 持續成長時仍維持 AI 可讀性、最低必要載入與單一權威歸屬。

## 核心預設

**建立新的 `knowledge/**/*.md` 不是預設動作；預設動作是先尋找並更新既有 canonical owner。**

在建立任何新 knowledge page 前，AI 必須先完成下列決策門。若任一步已能安全容納新內容，就停止新增頁面的路徑。

## 新增知識決策順序

1. **先確認現況**：remote read-back GitHub `main`，再用 `indexes/knowledge-index.json`、對應 domain manifest 與最低必要既有頁面搜尋可能的 canonical owner；不得只依舊聊天、cached copy 或 AI memory 判斷「尚無此頁」。
2. **先判斷資料性質**：區分工程結論、補充 evidence、標準／產品 freshness、reference provenance、routing metadata；不同責任不得為方便而混成同一份文件。
3. **能更新既有 canonical page 就不新增**：若新資料只是補充說明、新 evidence、修正、freshness／status 更新，或能自然落入既有頁面的工程邊界，直接更新原 owner。
4. **只有獨立 retrieval intent 才新增 leaf page**：新主題必須可合理地被單獨詢問、單獨引用，而且塞入既有頁會迫使 AI 為回答其他問題載入大量無關內容。不要只因資料變多、來源變多或單頁變長就拆頁。
5. **避免微頁面膨脹**：不以固定 KB、字數或段落數作拆分門檻。主題仍高度單一時可保留較長頁面；不要把一個工程問題拆成大量只有少量補充內容的小頁。
6. **優先使用既有 top-level domain**：不得因單一新主題建立 `knowledge/<new-domain>/`。只有現有 domain 無法自然容納，且預期形成穩定的多頁問題族時，才考慮新增 top-level domain。
7. **Router 與 index 必須保持薄**：router 只描述邊界與 routing；`knowledge-index.json` 只做 domain selection；`indexes/knowledge-pages/*.json` 只做 page selection。不得在這些 routing artifact 複製工程結論、公式、verification status、標準版次或 evidence。
8. **Top-level aliases 保持高訊號**：只加入能實際幫助判斷 domain 的穩定中英文術語；不得因新增 leaf page 就把該頁所有細部術語塞入 `knowledge-index.json`。
9. **References 與 knowledge 分工不變**：公開來源、標準 provenance 與版本資訊放在 `references/`；整理後的工程判斷放在 `knowledge/`。不要為減少一次讀檔而把 evidence dossier 複製進 knowledge page。
10. **Metadata 不做預測性堆疊**：只有 routing、validator、canonical ownership、provenance／freshness 或已有實際工具消費需求時才增加 metadata 欄位；不要為「AI 也許會用」而預先塞大量 keyword、summary 或重複狀態。

## 建立新頁前的強制說明

若決策結果仍是「需要新增 leaf page」，AI 在實際建立檔案前應能用一句話回答：

> 這個新頁面要獨立回答哪一個既有頁面不能乾淨承擔的工程問題？

若無法清楚回答，預設回到既有 canonical page 整合，而不是新增頁面。

若決策結果是「需要新增 top-level domain」，還必須說明：

- 為什麼現有 domain 都無法自然容納；
- 為什麼這不是單一 leaf topic；
- 預期會形成什麼穩定的多頁問題族。

無法滿足時，不建立新 top-level domain。

## 批次資料吸收規則

一次輸入多份標準、手冊、製造商資料、案例或工程觀察時，不得採「一份來源＝一個 knowledge page」。應先：

1. 去識別與確認公開／版權邊界；
2. 萃取可公開的 engineering claims；
3. 對每個 claim 尋找既有 canonical owner；
4. 更新既有 knowledge page 或 reference dossier；
5. 只有真正形成新的獨立 retrieval intent 時才新增 leaf page。

來源數量增加，不等於 knowledge page 數量應同比增加。

## 完成條件

新增／吸收知識只有在下列條件都成立時才算完成：

- canonical ownership 沒有重複；
- 沒有不必要的新 top-level domain；
- router／index／manifest 沒有被塞入 knowledge 本體；
- 新增或移動 `knowledge/**/*.md` 後已執行 `python scripts/build_knowledge_manifests.py`；
- `python scripts/build_knowledge_manifests.py --check` 與 repository validation 通過；
- GitHub Actions 為 success；
- 最後 remote read-back `main` 確認實際內容與預期一致。

> 原則：**讓 leaf pages 可以隨知識成長，但不要讓每次查詢必讀的 bootstrap、top-level index 與 router 跟著線性膨脹。**
