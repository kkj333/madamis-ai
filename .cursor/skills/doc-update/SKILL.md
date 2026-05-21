---
name: doc-update
description: >-
  Updates README.md, spec.md, and backend/docs/ when code or ops change.
  Use after backend/interface routes, env vars, Docker, Terraform, CI/CD, or ADK agent changes.
disable-model-invocation: true
---

# ドキュメントアップデート（madamis-ai）

実装・設定を変えたら、**対応する Markdown を同じ PR で更新する**。

## 正本

| ファイル | 内容 |
| --- | --- |
| `README.md` | 入口・セットアップ・Docker・Dev UI |
| `spec.md` | 全体構成・環境変数・デプロイ方針 |
| `backend/docs/*.md` | 再現手順など（例: `tools-pydantic-repro.md`） |
| `backend/.env.example` / `interface/.env.example` | 環境変数の例 |

## 変更種別 → 更新先

| 触った領域 | 更新先 |
| --- | --- |
| FastAPI / ADK エージェント / API | `README.md`, `spec.md` |
| Vertex / Firestore / Gemini 設定 | `README.md`, `backend/.env.example`, `spec.md`, `terraform/` コメント |
| Docker / compose / Dev UI | `README.md`, `compose.yaml`, `compose.dev.yaml` コメント |
| Terraform / Cloud Run | `README.md`, `spec.md`, `terraform/variables.tf` の description |
| tools + Pydantic 再現 | `backend/docs/tools-pydantic-repro.md`, `README.md` |
| CI | `.github/workflows/ci.yml` と README のテスト手順 |

## 手順

1. 上表で当たるファイルを開き、古い記述がないか確認。
2. コマンド例は **実際の `compose.yaml` / CI / `pyproject.toml` と一致**させる。
3. PR 前に **`redact-project-info`** で example / docs に実 project_id・トークンが無いか確認。

## やらないこと

- 仕様の長文を README に貼って `spec.md` と二重管理する。
- 依頼されていない無関係ドキュメントの大量リライト。
