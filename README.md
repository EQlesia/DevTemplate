# DevTemplate
開発時のテンプレートをまとめておいておく
# 以下これを作った方法忘れたとき見る用
# DevTemplate — インデックス自動生成 導入手順

> `SpecificationsDoc/` 以下の HTML をブラウザで一覧できるようにする  
> GitHub Actions による `index.html` 自動更新のセットアップ手順

---

## 前提条件

| 項目 | 条件 |
|------|------|
| リポジトリ | `github.com/EQlesia/DevTemplate`（Public または Private） |
| ブランチ | `main` がデフォルトブランチ |
| Actions | リポジトリの Settings → Actions が **有効** になっていること |
| 権限 | リポジトリへの `write` 権限（push できること） |

---

## Step 1 — ファイルをリポジトリに配置する

以下のディレクトリ構成になるようにファイルを配置します。  
すでに `git clone` 済みのローカルリポジトリで作業してください。

```
DevTemplate/
├── index.html                            ← ルート用テンプレート
├── SpecificationsDoc/
│   ├── index.html                        ← フォルダ用テンプレート
│   └── GUIAppSpecificationTemplateForWin.html
├── .github/
│   ├── workflows/
│   │   └── update-index.yml
│   └── scripts/
│       └── gen_index.py
```

```bash
# ディレクトリを作成
mkdir -p .github/workflows .github/scripts SpecificationsDoc

# 各ファイルをコピー（ダウンロードしたファイルを配置）
cp update-index.yml  .github/workflows/
cp gen_index.py      .github/scripts/
cp index.html        ./
cp SpecificationsDoc_index.html  SpecificationsDoc/index.html
cp GUIAppSpecificationTemplateForWin.html  SpecificationsDoc/
```

---

## Step 2 — Actions の書き込み権限を確認する

GitHub Actions がコミットを push できるよう、権限を設定します。

1. リポジトリページ → **Settings** → **Actions** → **General**
2. ページ下部の **Workflow permissions** を開く
3. **Read and write permissions** を選択して **Save**

```
Settings
└── Actions
    └── General
        └── Workflow permissions
            ☑ Read and write permissions  ← これを選択
```

---

## Step 3 — コミットして push する

```bash
git add .
git commit -m "feat: add index auto-generation via GitHub Actions"
git push origin main
```

push すると `update-index.yml` のトリガー条件（`*.html` の変更）に合致するため、  
**Actions が自動実行**され `index.html` が更新されます。

---

## Step 4 — Actions の実行結果を確認する

1. リポジトリページ → **Actions** タブを開く
2. **Update Index Pages** ワークフローが実行中または完了しているのを確認
3. 成功すると以下のログが表示される

```
✅  生成: SpecificationsDoc/index.html  (1 files)
✅  生成: index.html  (1 folders)
No changes to commit.   # すでに最新の場合
```

4. `main` ブランチに `chore: update index pages [skip ci]` というコミットが追加されていれば完了

---

## Step 5 — ブラウザで確認する

GitHub Pages を使う場合はそちらの URL で、  
ローカル確認の場合は `git pull` 後に直接 HTML を開きます。

```bash
# 最新を取得
git pull origin main

# ローカルで確認（ブラウザで開く）
open index.html                          # macOS
start index.html                         # Windows
xdg-open index.html                      # Linux
```

---

## 新しいテンプレートを追加するとき

`SpecificationsDoc/` に HTML ファイルを追加して push するだけで  
次回 Actions 実行時に自動でインデックスに反映されます。

```bash
cp NewTemplate.html SpecificationsDoc/
git add SpecificationsDoc/NewTemplate.html
git commit -m "docs: add NewTemplate"
git push origin main
# → Actions が自動起動 → index.html が更新される
```

---

## 新しいフォルダを追加するとき（将来の拡張）

例: `ArchitectureDocs/` を追加する場合

**① フォルダと HTML を追加**

```bash
mkdir ArchitectureDocs
cp SomeTemplate.html ArchitectureDocs/
git add ArchitectureDocs/
git commit -m "docs: add ArchitectureDocs"
git push origin main
```

**② `gen_index.py` の `FOLDER_META` に説明を追記（任意）**

説明を書かなくてもデフォルト値で動きますが、  
書いておくとルートの `index.html` に説明文とアイコンが表示されます。

```python
# .github/scripts/gen_index.py  L32 付近
FOLDER_META: dict[str, dict] = {
    'SpecificationsDoc': {
        'icon': '📄',
        'desc': '仕様書テンプレート集 — Windows GUI アプリ・その他',
    },
    # ↓ 追記
    'ArchitectureDocs': {
        'icon': '🏗️',
        'desc': 'アーキテクチャ設計ドキュメント',
    },
}
```

---

## トリガーのまとめ

| トリガー | 条件 |
|----------|------|
| `main` への push | `*.html` が変更されたとき（`index.html` 自身は除外） |
| スケジュール | 毎日 JST 09:00 |
| 手動実行 | Actions タブ → **Run workflow** ボタン |

---

## トラブルシューティング

**Actions が実行されない**  
→ Settings → Actions → General → **Allow all actions** になっているか確認

**`Permission denied` エラーで push に失敗する**  
→ Step 2 の Workflow permissions を再確認。  
それでも失敗する場合は `update-index.yml` に以下を追加:

```yaml
permissions:
  contents: write   # ← すでに記載済みだが念のため確認
```

**`テンプレートが見つかりません` と表示される**  
→ `index.html` と `SpecificationsDoc/index.html` が  
リポジトリルートと正しいパスにコミットされているか確認

**index.html が更新されない**  
→ Actions タブでエラーログを確認。  
手動で **Run workflow** を実行して動作を検証する
