# syntax=docker/dockerfile:1
# ── Backend — FastAPI / uvicorn ───────────────────────────────────────────────
# Build context: project root (pyproject.toml lives there, and the import
# path is app.backend.app.main so the whole project tree must be present)

FROM python:3.12-slim

# Install uv (copies the single binary from the official image)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# ── Install dependencies ──────────────────────────────────────────────────────
# Copy only the manifest first so this layer is cached on code-only changes.
# uv.lock is gitignored in this repo, so we use plain `uv sync` (no --frozen).
COPY pyproject.toml ./
RUN uv sync --no-dev

# ── Copy source ───────────────────────────────────────────────────────────────
# The uvicorn entry point is  app.backend.app.main:app
# so the full app/ tree must be at /app/app/
COPY app/ ./app/

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.backend.app.main:app", \
     "--host", "0.0.0.0", "--port", "8000"]
