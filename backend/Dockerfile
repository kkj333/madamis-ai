FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# 依存関係のインストール
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-cache

# アプリケーションコードをコピー
COPY . .

EXPOSE 8000

CMD ["/app/.venv/bin/uvicorn", "madamis.main:app", "--host", "0.0.0.0", "--port", "8000"]
