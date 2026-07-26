# Build context is the REPO ROOT, not backend/ — the image needs assets/ for the
# fallback resume/aboutme copies:
#   docker build -f backend/Dockerfile -t osher-ai-twin .

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Dependencies first so the layer caches until the lockfile actually changes.
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev


FROM python:3.13-slim

# Cloud Run terminates TLS and sends traffic to $PORT (8080 by default).
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    ASSETS_DIR=/app/assets \
    PORT=8080

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY backend/app ./app
# Fallback content + static copies, used only when a live fetch fails.
COPY assets ./assets

RUN useradd --create-home --uid 1001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# Shell form so $PORT expands at runtime; exec keeps uvicorn as PID 1 for signals.
CMD exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
