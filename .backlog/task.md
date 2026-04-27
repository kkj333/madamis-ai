# 夢占いAI プロジェクト タスクリスト

## 1. インフラ・基盤整備
- [x] `mise` に `terraform` を追加
- [x] Terraform による GCP 基本設定 (Artifact Registry, APIs)
- [x] GCE `e2-micro` インスタンスの定義 (Discord Bot 用)
- [x] Cloud Run (推論サーバー & フロントエンド) の定義

## 2. バックエンド - 推論層 (Cloud Run)
- [x] ADK 推論用 API エンドポイントの作成 (`/api/interpret`)
- [x] セッション管理の整理 (InMemory実装)
- [ ] Cloud Run へのデプロイ確認 (GitHub Actions 経由)
- [ ] Firestore による永続化の検討 (将来タスク)

## 3. バックエンド - インターフェース層 (Discord Bot)
- [x] 送信インターフェース (`interface.py`) の定義
- [x] 軽量 HTTP クライアントを用いた Bot の実装 (interface/ ディレクトリ)
- [x] GCE 上での Docker 起動設定 (Terraform metadata_startup_script)

## 4. 定期投稿・自動化
- [ ] Cloud Scheduler による定期投稿トリガーの作成
- [ ] 特定のチャンネルへ「今日の一言」を投稿する機能の実装

## 5. フロントエンド連携
- [x] Cloud Run API を Web フロントエンドから直接叩けるように調整
- [x] CORS 設定の再確認
- [x] フロントエンドのビルド・デプロイ最適化 (Dockerfile 修正)

## 完了済み
- [x] FastAPI + Discord Bot (Gateway) の統合
- [x] プロジェクト構成の整理 (backend, frontend, interface 分離)
- [x] テスト基盤の導入 (pytest, vitest)
- [x] 静的解析・型チェックの導入 (ruff, ty)
- [x] GitHub Actions による CI/CD 構築
