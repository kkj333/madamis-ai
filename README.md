# 🌙 夢占いAIエージェント

夢の内容をチャットで入力すると、AIが夢占いの結果を解き明かしてくれるアプリケーションです。  
神秘的な夢見師のAIが、あなたの夢のシンボル・心理状態・吉凶・アドバイスを丁寧に解釈します。

![Web チャット UI（トップ画面）](docs/screenshot.png)

---

## 🏗 アーキテクチャ

このプロジェクトは、役割ごとに以下の3つのコンポーネントで構成されています。

- **Backend (FastAPI)**: Google ADK を用いた夢占いの推論エンジンを提供。Cloud Run でホスト。
- **Frontend (Next.js)**: 美しい星空の背景を持つ Web チャット UI。Cloud Run でホスト。
- **Interface (Discord Bot)**: Discord からも夢占いを利用できるインターフェース。Compute Engine で常時稼働。

---

## ⚡ クイックスタート

### 1. 開発環境の準備

ツール管理に [mise](https://mise.jdx.dev/) を使用しています。

```bash
mise install
```

### 2. APIキーの設定

`.env` ファイルを作成し、必要なキーを設定してください。

```bash
GOOGLE_API_KEY="AIzaSy..."
DISCORD_BOT_TOKEN="MTQ5..."
```

### 3. Docker Compose で起動（一括起動）

```bash
docker compose up --build
```

- **Web UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Discord Bot**: 起動後、設定した Bot がオンラインになります。

---

## 🛠 開発・テスト

### 各コンポーネントの操作

#### バックエンド / インターフェース (Python)
パッケージ管理には [uv](https://docs.astral.sh/uv/) を使用しています。

```bash
# 型チェック
cd backend && uv run ty check
cd interface && uv run ty check

# Lint (ruff)
cd backend && uv run ruff check
cd interface && uv run ruff check

# テスト実行
cd backend && uv run pytest
cd interface && uv run pytest
```

#### フロントエンド (Node.js)

```bash
cd frontend
npm install
npm run lint
npm test
```

---

## 🚀 GCP デプロイと CI

`terraform/` には GCP 上に載せるための定義（Cloud Run、Compute Engine、Secret Manager、Artifact Registry など）があります。  
**GitHub Actions による CD（イメージのプッシュや Terraform の自動 apply）は現状未実装**です。本番へ出す場合は、ローカルまたは別パイプラインで Docker ビルド・レジストリへのプッシュ・`terraform apply` を行う想定です。

### インフラ構成（Terraform 想定）
- **Cloud Run**: Backend API, Web Frontend
- **Compute Engine (e2-micro)**: Discord Bot (Free Tier 活用)
- **Secret Manager**: APIキー・トークンの安全な管理
- **Artifact Registry**: Docker イメージの管理

### CI（GitHub Actions）
`main` へのプッシュおよび `main` 向けプルリクエストで [`.github/workflows/ci.yml`](.github/workflows/ci.yml) が動き、backend / interface / frontend それぞれで Lint・型チェック・テストを実行します。

---

## 📁 ディレクトリ構造

```
yume-uranai/
├── docs/             # README 用スクリーンショットなど
├── backend/          # FastAPI 推論層
├── frontend/         # Next.js Web UI
├── interface/        # Discord Bot インターフェース層
├── terraform/        # GCP インフラ定義
├── tests/            # コンポーネント別テスト
├── .github/          # GitHub Actions（CI のみ）
├── .mise.toml        # 開発ツール管理
└── compose.yaml      # ローカル開発用
```

---

## 技術スタック

| 分類 | 技術 |
|---|---|
| AI エージェント | [google-adk](https://google.github.io/adk-docs/) |
| LLM | `gemini-3.0-flash` |
| Web UI | Next.js (React 19), Tailwind CSS, Vitest |
| API | FastAPI, Uvicorn, Pytest |
| Infra | Terraform, GCP (Cloud Run, GCE), Docker |
| Dev Tools | uv, mise, ruff, ty (type checker) |
