# マダミスサポート AI（madamis-ai）システム設計書

## 1. プロジェクト概要

ユーザーがチャット形式で **マーダーミステリー（マダミス）** に関する相談（ルール、用語、進め方、GM 向けの段取りなど）を入力すると、AI が **ネタバレに配慮しつつ** 回答する Web アプリケーションおよび Discord ボット。

- **目的**: プレイ前後の疑問解消、議論の整理、用語理解の補助。**公式シナリオの真相の代弁はしない。**
- **世界観**: 落ち着いたダークトーンのチャット UI（推理・卓上のイメージ）。

---

## 2. システムアーキテクチャ

Docker Compose を用いたマルチコンテナ構成。**`backend/.env`**（`GOOGLE_API_KEY`）と **`interface/.env`**（`DISCORD_BOT_TOKEN`）を各ディレクトリの `.env.example` から作成して使う。Compose の `env_file` は `required: false` のためファイルが無くても起動は可能。Discord Bot は **`discord` プロファイル**（`docker compose --profile discord up`）でのみ起動し、省略時は Backend + Frontend のみ。

- **Frontend (Next.js)**: ユーザーインターフェース。入力を Backend へ送信。
- **Backend (FastAPI)**: `google-adk` 経由で LLM（Gemini）にプロンプトとユーザー入力を渡し、返答を Frontend / Interface に返す。
- **Interface (Discord Bot)**: メンションまたは DM で同じ推論 API を利用。
- **LLM**: `gemini-3-flash-preview`。ペルソナは「マダミスサポート AI」（ルール・進行寄り、ネタバレ抑制ガイドライン付き）。

---

## 3. 技術スタック

| コンポーネント | 技術・ツール | 備考 |
|---|---|---|
| 環境構築 | Docker, Docker Compose | フロント・バックエンド・Bot を分離 |
| Frontend | Next.js (App Router), React, Tailwind CSS | Node.js 20 系 |
| Backend | FastAPI, Uvicorn | Python 3.13 系 |
| パッケージ管理 (Python) | uv | |
| AI SDK | google-adk | |
| LLM | gemini-3-flash-preview | |

---

## 4. ディレクトリ構成（概要）

```
madamis-ai/
├── frontend/             # フロントエンド (Next.js)
├── backend/              # バックエンド (FastAPI)、`madamis/`・`tests/`
├── interface/            # Discord Bot、`madamis_interface/`・`tests/`
├── docs/                 # README 用画像など
├── terraform/
├── backend/.env.example  # → backend/.env（GOOGLE_API_KEY）
├── interface/.env.example # → interface/.env（DISCORD_BOT_TOKEN など）
└── compose.yaml
```

---

## 5. API 仕様 (Frontend ↔ Backend)

### `POST /api/chat`

ユーザーのテキストを送信し、AI の返答を受け取る。

**Request (JSON)**

```json
{
  "text": "初めてマダミスに参加します。議論フェーズで気をつけることは？"
}
```

**Response (JSON)**

```json
{
  "reply": "はじめまして。議論フェーズでは…"
}
```

### `POST /api/interpret`

Discord など外部インターフェース用。`text` と `user_id` を受け取り、セッション単位で会話を維持。

### `GET /health`

死活確認。`{ "status": "ok" }`

---

## 6. フロントエンド実装要件

- **UI**: ダークテーマ。スレート・インディゴ系。背景は粒子（星風）で緊張感のある卓上の雰囲気を補助してよい。
- **状態管理**: `useState` でメッセージ履歴・入力・ローディングを管理。
- **ローディング**: 「手がかりを整理しています…」など、マダミス文脈に合った文言とスピナー。
- **エラー**: 通信失敗時は「接続が途切れました」など、マダミス文脈に合った短いメッセージ。

---

## 7. バックエンド・エージェント要件

- **レイアウト**: Python パッケージは `src/` なしのフラット構成（例: `backend/madamis/`）。`uv sync` で editable インストールし、配布用ホイールは想定しない。
- **CORS**: フロント（例: `http://localhost:3000`）からのリクエストを許可。
- **`agent.py`**: 上記「マダミスサポート」システムプロンプト（ネタバレ禁止・GM 優先・商業シナリオ真相の非開示）。
- **環境変数**: `backend/.env` に `GOOGLE_API_KEY`（ADK / Gemini）。Bot 用は `interface/.env` の `DISCORD_BOT_TOKEN`。

---

## 8. Discord Bot

- メンションまたは DM でテキストを受け取り、`/api/interpret` へ中継。
- 空メッセージ時は「相談内容を送ってください」等の案内。

---

## 9. 非機能・ポリシー

- 本システムは **娯楽用サポート** であり、特定作品の公式見解ではない。
- 利用者には README で **シナリオ・GM の指示を最優先**することを明示する。
