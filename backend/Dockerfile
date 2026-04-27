FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# 依存関係のインストール
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-cache

# アプリケーションコードをコピー
COPY . .

EXPOSE 8000

# srcレイアウトに対応するため PYTHONPATH を設定し、パッケージ名指定で起動
ENV PYTHONPATH=/app/src
CMD ["/app/.venv/bin/uvicorn", "yume_uranai.main:app", "--host", "0.0.0.0", "--port", "8000"]
