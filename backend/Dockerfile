
# ============================================================
# Enterprise AI-Ready Data Platform
# Backend API Runtime
# ============================================================

FROM python:3.12-slim

# Use the same pinned uv release as the other migrated images.
COPY --from=ghcr.io/astral-sh/uv:0.13.4 /uv /uvx /bin/

# Keep dependency installation inside a dedicated container venv.
ENV UV_PROJECT_ENVIRONMENT=/opt/uv-venv
ENV UV_PYTHON_DOWNLOADS=0
ENV UV_LINK_MODE=copy

WORKDIR /app

# Copy the central dependency configuration first for build caching.
COPY pyproject.toml uv.lock ./

# Install only the backend dependency group using the committed lockfile.
# Python 3.12 matches the existing backend container runtime.
RUN uv sync \
    --locked \
    --only-group backend \
    --python /usr/local/bin/python

# Make the managed environment's executables available to the container.
ENV PATH="/opt/uv-venv/bin:${PATH}"

# Copy the backend application after installing dependencies.
COPY backend/app ./app

# Preserve the existing API port and application entry point.
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
