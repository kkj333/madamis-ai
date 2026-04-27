FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-cache || uv sync --no-cache

COPY . .

# BotはポートをリッスンしないためEXPOSEは不要

ENV PYTHONPATH=/app/src
ENTRYPOINT []
CMD ["/app/.venv/bin/python", "-m", "yume_uranai_interface.main"]
