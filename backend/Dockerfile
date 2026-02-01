# Multi-stage build for minimal backend image (AG-UI server for Next.js frontend).
# Build stage: install deps with uv, production only.
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv via pip (avoids ghcr.io pull; slim image has pip).
RUN pip install --no-cache-dir uv

# Copy dependency manifests and app code (README.md required by hatchling).
COPY pyproject.toml uv.lock README.md ./
COPY main.py ./
COPY academic_research ./academic_research/

# Install production deps and project; no dev, no cache.
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
RUN uv sync --no-dev --no-install-project --no-cache && \
    uv pip install --no-deps -e . --no-cache

# Trim venv: remove bytecode caches to shrink image.
RUN find /app/.venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /app/.venv -name "*.pyc" -delete 2>/dev/null || true

# Runtime stage: minimal image.
FROM python:3.12-slim AS runtime

WORKDIR /app

# Create non-root user.
RUN adduser --disabled-password --gecos "" appuser

# Copy venv and app from builder.
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/main.py ./
COPY --from=builder /app/academic_research ./academic_research/

# Ensure .env can be mounted at runtime (optional).
ENV PATH="/app/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/app/.venv"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

USER appuser

EXPOSE 8000

# Run AG-UI server; Next.js frontend should point at this (e.g. NEXT_PUBLIC_AG_UI_URL=http://backend:8000).
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
