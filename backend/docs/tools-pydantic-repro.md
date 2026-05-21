# tools + Pydantic structured output 再現

## やりたいこと

**ADK で `tools=[...]` と nested Pydantic `output_schema` を同時に使ったとき**、
Gemini 呼び出しや `SetModelResponseTool` 経路で失敗するケースを再現・記録する。

（genai Client 直呼びの `response_schema` だけの成功例とは別問題。）

## Docker Compose

リポジトリルート（`madamis-ai/`）で実行。事前に `backend/.env` と ADC:

```bash
cp backend/.env.example backend/.env   # 未作成なら
gcloud auth application-default login
```

### Dev UI 起動（`:8001`）

```bash
docker compose -f compose.yaml -f compose.dev.yaml up --build backend
```

バックグラウンド:

```bash
docker compose -f compose.yaml -f compose.dev.yaml up --build -d backend
```

→ http://localhost:8001  
アプリ **`tools_pydantic_repro`** を選ぶ（対照は **`madamis`**）。

### ログ / 停止

```bash
docker compose -f compose.yaml -f compose.dev.yaml logs -f backend
docker compose -f compose.yaml -f compose.dev.yaml down
```

### 再現スクリプト（コンテナ内・Live + offline）

```bash
docker compose -f compose.yaml -f compose.dev.yaml run --rm backend \
  /app/.venv/bin/python scripts/adk_tools_pydantic_error_repro.py
```

### テスト（offline の SchemaError 再現）

```bash
docker compose -f compose.yaml -f compose.dev.yaml run --rm backend \
  uv run pytest tests/test_tools_pydantic_repro.py -q
```

## Dev UI（ローカル uv なし）

```bash
docker compose -f compose.yaml -f compose.dev.yaml up --build backend
```

## ADK の分岐

| 条件 | 経路 |
|------|------|
| Vertex + Gemini 2+ | `response_schema` ネイティブ（tool loop 可）→ **エラーになりにくい** |
| それ以外、または native 非対応モデル | `SetModelResponseTool` を **tools に追加** |

## 確実に落ちる例（API 不要）

raw dict を `SetModelResponseTool` に渡すと declaration 生成で失敗:

```python
from google.adk.tools.set_model_response_tool import SetModelResponseTool

schema = {"type": "object", "properties": {"result": {"type": "string"}}}
SetModelResponseTool(schema)._get_declaration()  # SchemaError
```

`pytest tests/test_tools_pydantic_repro.py` 参照。

## SetModelResponseTool 経路を Live で見る

1. `.env` で `GEMINI_MODEL` を native 非対応にする（例: 古い 1.5 系）**か**
2. `scripts/adk_tools_pydantic_error_repro.py` を実行（fallback を patch して強制）

```bash
cd backend
uv run python scripts/adk_tools_pydantic_error_repro.py
```

## 参考

| パス | 役割 |
|------|------|
| `madamis/agent/support.py` | 本番 `madamis` — `roll_dice` のみ（対照） |
| `madamis/models/recipe.py` | `Recipe` / `Ingredient`（structured output 用） |
| `madamis/tools/dice.py` | `roll_dice` tool |
| `tools_pydantic_repro/agent.py` | `roll_dice` + `output_schema=Recipe` |
| `scripts/adk_tools_pydantic_error_repro.py` | ADK 経路の Live / offline 再現 |
| `scripts/genai_pydantic_repro.py` | ADK なし genai + JSON schema（tools ループ外） |
