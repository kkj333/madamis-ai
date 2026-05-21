---
name: redact-project-info
description: >-
  Scans docs, examples, and workflows for project-specific secrets (GCP project
  IDs, Discord tokens, Cloud Run hosts) before a public PR. Use before create-pr
  when touching README, spec, or .env.example files.
disable-model-invocation: true
---

# プロジェクト固有情報の洗い出し（madamis-ai）

**実運用の GCP project_id・Discord トークン・本番 URL** がコミット対象に混ざっていないか調べる。

## 手順

```bash
chmod +x .cursor/skills/redact-project-info/scripts/scan.sh
.cursor/skills/redact-project-info/scripts/scan.sh
```

## コミットしてはいけないもの

| 種別 | 例 |
| --- | --- |
| GCP `project_id` の実値 | `.env.example` で `your-gcp-project-id` 以外 |
| Discord Bot Token | `MTQ…` / `eyJ…` |
| Cloud Run URL | 具体 `*.run.app` |
| `terraform.tfvars` / `backend/.env` | gitignore 済みだがコミット禁止 |

## プレースホルダ慣例

| 種類 | 例 |
| --- | --- |
| GCP | `your-gcp-project-id`, `YOUR_GCP_PROJECT_ID` |
| Discord | `your-discord-bot-token`（example のみ） |

## 実値の置き場所

- `terraform/terraform.tfvars`, `backend/.env`, `interface/.env`（gitignore）
- GitHub Actions Secrets / Secret Manager

## リポ固有パターン（任意）

```bash
cp .cursor/skills/redact-project-info/patterns.local.example patterns.local
# patterns.local は gitignore 済み
```

## 関連スキル

- `doc-update`, `create-pr`
