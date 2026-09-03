# 機器可讀索引（Indexes）

`indexes/` 只保存 routing / lookup metadata，不保存第二份工程結論。

## 知識路由

- `knowledge-index.json`：第一層 domain routing；`id / aliases` 用來選 domain，`entrypoint / router` 提供預設入口。
- `knowledge-pages/<domain>.json`：第二層 page routing；依 `slug / path / section` 直接命中該 domain 內的 leaf page。

Page manifest 只保存路由資訊：

- `path`
- `slug`
- `kind`
- `section`（有子目錄時）

**不在 manifest 複製 verification status、工程結論、公式、標準版本或 evidence。** 這些內容必須回到 canonical knowledge page / reference dossier。

`knowledge-pages/*.json` 由下列指令自動產生：

```bash
python scripts/build_knowledge_manifests.py
```

Repository CI 會使用 `--check` 確認 manifest 與 `knowledge/**/*.md` 路徑同步；新增、刪除或移動 knowledge page 後若未重建 manifest，CI 應失敗。

## 標準索引

- `standards-index.json`：標準 ID → `references/standards/` dossier path。
- Edition / status / verification metadata 仍由 dossier frontmatter 與正文維護，index 不建立第二份版本快照。

> 原則：index 幫 AI 找到該讀的頁；真正工程判斷仍由目標頁面的 canonical content 決定。
