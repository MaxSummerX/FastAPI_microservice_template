# === build stage ===
FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-group dev --no-install-project


# === runtime stage ===
FROM python:3.13-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

RUN useradd --create-home appuser
COPY --from=builder /app/.venv /app/.venv

COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini ./

RUN mkdir -p /app/logs && chown appuser:appuser /app/logs
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
