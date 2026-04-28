FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-cache || uv sync --no-cache

COPY . .

# BotはポートをリッスンしないためEXPOSEは不要

ENTRYPOINT []
CMD ["/app/.venv/bin/python", "-m", "madamis_interface.main"]
