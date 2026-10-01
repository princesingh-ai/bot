# ==============================================================================
# Production Multi-Stage Dockerfile for CRIEYA Chatbot
# Compatible with AWS App Runner / ECS, Google Cloud Run, Render, Heroku
# ==============================================================================

FROM python:3.12-slim-bookworm

# Security & Python optimization flags
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PORT=8000 \
    HOST=0.0.0.0 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install official standalone uv binary for high-performance reproducible installs
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Create non-root user for container security
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app -s /bin/bash appuser

# Copy dependency specifications first to leverage Docker layer caching
COPY pyproject.toml uv.lock ./

# Install locked dependencies into /app/.venv without project code or dev packages
RUN uv sync --frozen --no-install-project --no-dev

# Copy application source code and required datasets
COPY app/ ./app/
COPY server/ ./server/
COPY data/ ./data/
COPY config.yaml run.py ./

# Complete project installation
RUN uv sync --frozen --no-dev

# Set permissions for non-root user
RUN chown -R appuser:appgroup /app

USER appuser

# Expose the application port
EXPOSE 8000

# Container healthcheck using standard library urllib
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import os, urllib.request; port = os.getenv('PORT', '8000'); urllib.request.urlopen(f'http://127.0.0.1:{port}/health/live')"

# Production orchestrator entrypoint
CMD ["python", "run.py"]
