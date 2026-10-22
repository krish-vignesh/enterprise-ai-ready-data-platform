
# ============================================================
# Enterprise AI-Ready Data Platform
# MinIO Bucket Initialization Container
# ============================================================

FROM python:3.12-slim

# Use the same pinned uv release as the other migrated images.
COPY --from=ghcr.io/astral-sh/uv:0.13.4 /uv /uvx /bin/

# Use a dedicated virtual environment inside this container.
ENV UV_PROJECT_ENVIRONMENT=/opt/uv-venv
ENV UV_PYTHON_DOWNLOADS=0
ENV UV_LINK_MODE=copy

WORKDIR /app

# Copy the central dependency configuration first for build caching.
COPY pyproject.toml uv.lock ./

# Install only the MinIO initialization dependency group.
# Preserve Python 3.12 and require the committed lockfile to be current.
RUN uv sync \
    --locked \
    --only-group minio-init \
    --python /usr/local/bin/python

# Ensure the container uses the uv-managed Python environment.
ENV PATH="/opt/uv-venv/bin:${PATH}"

# Copy the initialization script from the repository root build context.
COPY infrastructure/docker/minio_init/init_minio.py ./init_minio.py

# Preserve the existing one-time initialization behavior.
ENTRYPOINT ["/opt/uv-venv/bin/python", "init_minio.py"]
