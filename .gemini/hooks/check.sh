#!/usr/bin/env bash

# 進行状況を stderr に出力
echo "--- 🔍 自動品質チェック中... ---" >&2

# backend のチェック
echo "[backend] Linting and Testing..." >&2
(cd backend && uv run ruff check . >/dev/null 2>&1 && uv run ty check madamis >/dev/null 2>&1 && uv run pytest >/dev/null 2>&1)
BACKEND_RES=$?

# interface のチェック
echo "[interface] Linting and Testing..." >&2
(cd interface && uv run ruff check . >/dev/null 2>&1 && uv run ty check madamis_interface >/dev/null 2>&1 && uv run pytest >/dev/null 2>&1)
INTERFACE_RES=$?

# frontend のチェック
echo "[frontend] Linting and Testing..." >&2
(cd frontend && npm run lint >/dev/null 2>&1 && npm test >/dev/null 2>&1)
FRONTEND_RES=$?

if [ $BACKEND_RES -eq 0 ] && [ $INTERFACE_RES -eq 0 ] && [ $FRONTEND_RES -eq 0 ]; then
    echo "{\"decision\": \"allow\", \"systemMessage\": \"✅ すべての自動チェックにパスしました。\"}"
else
    # 失敗したコンポーネントを特定
    FAILED=""
    [ $BACKEND_RES -ne 0 ] && FAILED="$FAILED backend"
    [ $INTERFACE_RES -ne 0 ] && FAILED="$FAILED interface"
    [ $FRONTEND_RES -ne 0 ] && FAILED="$FAILED frontend"
    
    echo "{\"decision\": \"deny\", \"reason\": \"以下のコンポーネントでチェックが失敗しました:$FAILED。修正が必要です。\", \"systemMessage\": \"❌ 自動チェック失敗:$FAILED\"}"
fi
