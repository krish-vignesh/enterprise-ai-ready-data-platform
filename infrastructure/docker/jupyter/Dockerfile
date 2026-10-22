
# ============================================================
# Enterprise AI-Ready Data Platform
# Jupyter Workspace Runtime
# ============================================================

FROM ubuntu:24.04

# Pin the dependency manager used by the Python project.
COPY --from=ghcr.io/astral-sh/uv:0.13.4 /uv /uvx /bin/

ARG DEBIAN_FRONTEND=noninteractive

# Install system-level requirements.
# Python dependencies are installed separately through uv.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        openjdk-21-jdk-headless \
        python3.12 \
        python3.12-venv && \
    rm -rf /var/lib/apt/lists/*

# Java and uv environment configuration.
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV UV_PROJECT_ENVIRONMENT=/opt/uv-venv
ENV UV_PYTHON_DOWNLOADS=0
ENV UV_LINK_MODE=copy

WORKDIR /app

# Copy central dependency configuration first for build caching.
COPY pyproject.toml uv.lock ./

# Install only the Jupyter runtime group using Python 3.12.
# The lockfile must already match pyproject.toml.
RUN uv sync \
    --locked \
    --only-group jupyter-runtime \
    --python /usr/bin/python3.12

# Use the PySpark distribution installed in the uv environment.
ENV SPARK_HOME=/opt/uv-venv/lib/python3.12/site-packages/pyspark
ENV PYSPARK_PYTHON=/opt/uv-venv/bin/python
ENV PYSPARK_DRIVER_PYTHON=/opt/uv-venv/bin/python

ENV PATH="${SPARK_HOME}/bin:${JAVA_HOME}/bin:/opt/uv-venv/bin:${PATH}"
ENV PYTHONPATH="${SPARK_HOME}/python:${PYTHONPATH}"

# Add the existing Hadoop S3A and Delta Lake JARs.
RUN mkdir -p "${SPARK_HOME}/jars" && \
    curl -fsSL \
        https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.5.0/hadoop-aws-3.5.0.jar \
        -o "${SPARK_HOME}/jars/hadoop-aws-3.5.0.jar" && \
    curl -fsSL \
        https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.35.4/bundle-2.35.4.jar \
        -o "${SPARK_HOME}/jars/bundle-2.35.4.jar" && \
    curl -fsSL \
        https://repo1.maven.org/maven2/software/amazon/s3/analyticsaccelerator/analyticsaccelerator-s3/1.3.1/analyticsaccelerator-s3-1.3.1.jar \
        -o "${SPARK_HOME}/jars/analyticsaccelerator-s3-1.3.1.jar" && \
    curl -fsSL \
        https://repo1.maven.org/maven2/io/delta/delta-spark_2.13/4.4.0/delta-spark_2.13-4.4.0.jar \
        -o "${SPARK_HOME}/jars/delta-spark_2.13-4.4.0.jar" && \
    curl -fsSL \
        https://repo1.maven.org/maven2/io/delta/delta-storage/4.4.0/delta-storage-4.4.0.jar \
        -o "${SPARK_HOME}/jars/delta-storage-4.4.0.jar"

# Create a dedicated non-root user for Jupyter.
RUN groupadd --system workspace && \
    useradd --system \
        --gid workspace \
        --create-home \
        --home-dir /home/workspace \
        workspace && \
    mkdir -p /workspace /home/workspace && \
    chown -R workspace:workspace /home/workspace /workspace

WORKDIR /workspace

EXPOSE 8888

USER workspace

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser"]
