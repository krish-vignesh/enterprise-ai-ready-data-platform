
# ============================================================
# Enterprise AI-Ready Data Platform
# Spark Runtime
# ============================================================

# Base Linux environment for the custom Spark image.
FROM ubuntu:24.04

# ------------------------------------------------------------
# uv — pinned Python dependency manager
# ------------------------------------------------------------
COPY --from=ghcr.io/astral-sh/uv:0.13.4 /uv /uvx /bin/

# ------------------------------------------------------------
# System dependencies
# Java 21 and Python 3.12 are required by the Spark platform.
# ------------------------------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openjdk-21-jdk \
        wget \
        python3.12 \
        python3.12-venv && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Java, Spark and Python environment configuration
# ------------------------------------------------------------
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV SPARK_HOME=/opt/spark

# Install the selected dependency group into a dedicated
# Python 3.12 environment inside the container.
ENV UV_PROJECT_ENVIRONMENT=/opt/uv-venv
ENV UV_LINK_MODE=copy

# ------------------------------------------------------------
# Install the centralized Spark Python dependency group
# ------------------------------------------------------------
WORKDIR /app

# Copy only dependency configuration first to improve build caching.
COPY pyproject.toml uv.lock ./

# Use the locked dependency versions and the container's Python 3.12.
# --only-group excludes the default development groups and installs
# only spark-runtime and its transitive dependencies.
RUN uv sync \
    --locked \
    --only-group spark-runtime \
    --python /usr/bin/python3.12

# Make the container's managed Python environment available by default.
ENV PATH="/opt/uv-venv/bin:${JAVA_HOME}/bin:${SPARK_HOME}/bin:${SPARK_HOME}/sbin:${PATH}"

# ------------------------------------------------------------
# Install the verified Apache Spark 4.2.0 distribution
# ------------------------------------------------------------
COPY infrastructure/docker/spark/spark-4.2.0-bin-hadoop3.tgz /tmp/

RUN tar -xzf /tmp/spark-4.2.0-bin-hadoop3.tgz -C /opt && \
    mv /opt/spark-4.2.0-bin-hadoop3 /opt/spark && \
    rm /tmp/spark-4.2.0-bin-hadoop3.tgz

# ------------------------------------------------------------
# Add S3A support for MinIO / S3-compatible object storage
# ------------------------------------------------------------
RUN wget -q -O /opt/spark/jars/hadoop-aws-3.5.0.jar \
        https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.5.0/hadoop-aws-3.5.0.jar && \
    wget -q -O /opt/spark/jars/bundle-2.35.4.jar \
        https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.35.4/bundle-2.35.4.jar && \
    wget -q -O /opt/spark/jars/analyticsaccelerator-s3-1.3.1.jar \
        https://repo1.maven.org/maven2/software/amazon/s3/analyticsaccelerator/analyticsaccelerator-s3/1.3.1/analyticsaccelerator-s3-1.3.1.jar && \
    wget -q -O /opt/spark/jars/delta-spark_2.13-4.4.0.jar \
        https://repo1.maven.org/maven2/io/delta/delta-spark_2.13/4.4.0/delta-spark_2.13-4.4.0.jar && \
    wget -q -O /opt/spark/jars/delta-storage-4.4.0.jar \
        https://repo1.maven.org/maven2/io/delta/delta-storage/4.4.0/delta-storage-4.4.0.jar

# ------------------------------------------------------------
# Configure PySpark to use Python 3.12 from the managed venv
# ------------------------------------------------------------
ENV PYSPARK_PYTHON=/opt/uv-venv/bin/python
ENV PYSPARK_DRIVER_PYTHON=/opt/uv-venv/bin/python

# Preserve the existing project import path and Spark Python libraries.
ENV PYTHONPATH="/workspace/backend:${SPARK_HOME}/python"

# Return to the original default working directory.
WORKDIR /
