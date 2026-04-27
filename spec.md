# 🌙 夢占いAIエージェント システム設計書

## 1. プロジェクト概要

ユーザーがチャット形式で夢の内容を入力すると、AIが夢占いの結果（心理状態、吉凶、アドバイスなど）を返答するWebアプリケーション。神秘的で落ち着いた世界観を提供する。

---

## 2. システムアーキテクチャ

Docker Composeを用いたマルチコンテナ構成。

- **Frontend (Next.js)**: ユーザーインターフェースを提供。ユーザーの入力を受け取り、Backendへリクエストを送信。
- **Backend (FastAPI)**: Frontendからのリクエストを受け取り、`google-adk` を介してLLM（Gemini）にプロンプトとユーザー入力を送信し、結果をFrontendに返す。
- **LLM**: `gemini-3-flash-preview` を使用し、夢占い師としてのペルソナに基づきテキストを生成。

---

## 3. 技術スタック

| コンポーネント | 技術・ツール | 備考 |
|---|---|---|
| 環境構築 | Docker, Docker Compose | フロント・バックエンドを別コンテナで分離 |
| Frontend | Next.js (App Router), React, Tailwind CSS | Node.js 20系 |
| Backend | FastAPI, Uvicorn | Python 3.13系 |
| パッケージ管理 (Python) | uv | 高速なPythonパッケージマネージャー |
| AI SDK | google-adk | GoogleのAIエージェント構築フレームワーク |
| LLM | gemini-3-flash-preview | |

---

## 4. ディレクトリ構成

```
yume-uranai/
├── frontend/             # フロントエンド (Next.js)
│   ├── app/              # App Router (page.tsx, layout.tsx, globals.css)
│   ├── package.json
│   └── Dockerfile        # Node.js環境用
├── backend/              # バックエンド (FastAPI)
│   ├── yume_uranai/
│   │   └── agent.py      # LLM呼び出しロジック (google-adk使用)
│   ├── main.py           # FastAPI ルーティング設定
│   ├── pyproject.toml    # uv用依存関係定義
│   ├── uv.lock           # ロックファイル
│   └── Dockerfile        # Python/uv環境用
├── .env                  # APIキー (GOOGLE_API_KEY)
└── compose.yaml          # コンテナオーケストレーション
```

---

## 5. API仕様 (Frontend ↔ Backend)

### `POST /api/chat`

夢の内容を送信し、占い結果を受け取る。

**Request (JSON)**
```json
{
  "text": "空を飛んでいて、急に落ちる夢を見ました"
}
```

**Response (JSON)**
```json
{
  "reply": "あなたが「空を飛んでいて、急に落ちる夢」を見たのですね。それは..."
}
```

### `GET /health`

バックエンドの死活確認。

**Response (JSON)**
```json
{ "status": "ok" }
```

---

## 6. フロントエンド実装要件

- **UI/デザイン**: ダークテーマを基調とし、夜や夢を連想させるカラーパレット（Slate, Indigo, Purpleなど）を使用。星をランダム配置したアニメーション背景。
- **状態管理**: Reactの `useState` を用いて、チャット履歴（`messages`）、入力中のテキスト（`input`）、ローディング状態（`isLoading`）を管理。
- **ローディング表現**: バックエンド通信中は入力を無効化し、「星の導きを読み解いています… ✨」といったテキストとスピナーで待機状態を視覚的に表現する。
- **エラーハンドリング**: バックエンドとの通信に失敗した場合は、チャットUI上にエラーメッセージ（例: 「夢と現実の境界で通信が途絶えました。もう一度お試しください。」）を表示する。

---

## 7. バックエンド実装要件

- **CORS設定**: フロントエンドコンテナ（`http://localhost:3000`）からの通信を許可する。
- **エージェント実装 (`agent.py`)**: `google-adk` を初期化し、`gemini-3-flash-preview` モデルを指定する。
- **システムプロンプト要件**:
  - 役割: 神秘的で親しみやすい夢占い師のAI（「夢見師」）
  - 出力内容: 夢の象徴の解説、現在の心理状態、吉凶の判定、未来への優しいアドバイス
  - トーン＆マナー: 専門的でありながら、優しく寄り添い、落ち着いた口調
- **環境変数**: `.env` ファイルから `GOOGLE_API_KEY` を読み込み、エージェントの認証に使用する。


## 8. discord botとして実装する


