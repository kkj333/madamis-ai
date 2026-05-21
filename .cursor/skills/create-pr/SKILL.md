---
name: create-pr
description: >-
  このリポジトリの変更をブランチに切り出し、日本語のプルリクエストを作成する。
  PR を出す、プルリクを作る、ブランチを切ってPRを出す、と言われたら使う。
disable-model-invocation: true
---

# PR 作成（madamis-ai）

## 事前チェック

PR を出す前に必ず通す。

```bash
cd backend && uv run ruff check . && uv run ty check madamis && uv run pytest -q
cd interface && uv run ruff check . && uv run ty check madamis_interface && uv run pytest -q
cd terraform && terraform fmt -check -recursive && terraform validate   # Terraform を変更した場合のみ
```

`README.md`・`spec.md`・`*.example`・`backend/docs/` を触った PR では、**`redact-project-info`** スキルに従いスキャンする。

```bash
.cursor/skills/redact-project-info/scripts/scan.sh
```

失敗したら先に直す。

## ブランチ作成

```bash
git checkout main && git pull origin main
git checkout -b <prefix>/<slug>
```

prefix: `feature/`（新機能）、`fix/`（バグ修正）、`chore/`（設定・依存更新）、`refactor/`（リファクタ）

## コミット

意味のある単位でコミットする。メッセージは日本語または英語（リポの慣習に合わせる）。

```bash
git add -A
git commit -m "$(cat <<'EOF'
<件名（何をどう変えたか>

<必要なら本文>
EOF
)"
```

## Push & PR 作成

```bash
git push -u origin <branch>
gh pr create --title "<日本語タイトル>" --body "$(cat <<'EOF'
## Summary
<1〜3行で何のPRか>

## Changes
| ファイル／領域 | 内容 |
| --- | --- |
| `path/to/file` | 説明 |

## Test plan
- [ ] `cd backend && uv run pytest` 通過
- [ ] `cd backend && uv run ruff check .` クリーン
- [ ] （interface 変更時）`cd interface && uv run pytest` 通過
- [ ] （Terraform 変更時）`terraform validate` 通過
EOF
)"
```

## タイトルの書き方

| 種別 | 例 |
| --- | --- |
| 新機能 | `feat: ADK Dev UI overlay for tools+Pydantic repro` |
| バグ修正 | `fix(terraform): Vertex AI env vars on Cloud Run` |
| 設定 | `chore: add Cursor git-workflow rules` |

## やらないこと

- `main` へ直接 push しない
- `--force` push は明示指示がない限り使わない
- テストが落ちたまま PR を出さない
- `terraform.tfvars` / `.env` をコミットしない
