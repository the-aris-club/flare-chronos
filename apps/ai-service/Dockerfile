# syntax=docker/dockerfile:1
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
COPY packages ./packages
COPY apps/ai-service ./apps/ai-service
COPY src ./src

RUN uv sync --frozen --group dev

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/packages/harmonization-core/src:/app/packages/firms-ingestion/src:/app/apps/ai-service/src:/app/src"

WORKDIR /app

RUN groupadd -r -g 1001 flare && useradd -r -u 1001 -g flare flare

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/packages /app/packages
COPY --from=builder /app/apps/ai-service /app/apps/ai-service
COPY --from=builder /app/src /app/src

RUN mkdir -p /app/data/runtime && chown -R flare:flare /app/data

USER flare
VOLUME ["/app/data/runtime"]
EXPOSE 5901

HEALTHCHECK --interval=10s --timeout=5s --retries=10 --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5901/health')"

CMD ["python", "-m", "ai_service.serve", "--host", "0.0.0.0", "--port", "5901"]