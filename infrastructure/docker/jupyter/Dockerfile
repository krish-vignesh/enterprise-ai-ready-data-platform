# Jupyter Workspace runtime for the Enterprise AI-Ready Data Platform.
# This intentionally keeps the image focused on the interactive Workspace
# environment and does not install a second Spark cluster or backend app.

FROM ubuntu:24.04

# Set noninteractive mode for apt-get to avoid prompts during package installation
ARG DEBIAN_FRONTEND=noninteractive

# Java 21 and the system Python 3.12 runtime required by the existing Spark platform.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    openjdk-21-jdk-headless \
    python3.12 \
    python3.12-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64 \
    PATH="${JAVA_HOME}/bin:${PATH}"

# Install the minimal Jupyter + Spark runtime needed by the Workspace driver.
RUN python3.12 -m pip install --no-cache-dir --break-system-packages \
        "pyspark==4.2.0" \
        "delta-spark==4.4.0" \
        "jupyterlab==4.3.6" \
        "minio==7.2.15" \
        "pydantic" \
        "pydantic-settings"

# Align the Workspace runtime with the existing Spark platform runtime.
# The Python executable is /usr/bin/python3.12, not /usr/local/bin/python.
ENV SPARK_HOME=/usr/local/lib/python3.12/dist-packages/pyspark \
    PYSPARK_PYTHON=/usr/bin/python3.12 \
    PYSPARK_DRIVER_PYTHON=/usr/bin/python3.12 \
    PYTHONPATH="${SPARK_HOME}/python:${PYTHONPATH}" \
    PATH="${SPARK_HOME}/bin:${PATH}"

# Add the Hadoop AWS S3A client jars needed for eventual MinIO/S3 access.
RUN mkdir -p "${SPARK_HOME}/jars" && \
    curl -fsSL https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.5.0/hadoop-aws-3.5.0.jar -o "${SPARK_HOME}/jars/hadoop-aws-3.5.0.jar" && \
    curl -fsSL https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.35.4/bundle-2.35.4.jar -o "${SPARK_HOME}/jars/bundle-2.35.4.jar" && \
    curl -fsSL https://repo1.maven.org/maven2/software/amazon/s3/analyticsaccelerator/analyticsaccelerator-s3/1.3.1/analyticsaccelerator-s3-1.3.1.jar -o "${SPARK_HOME}/jars/analyticsaccelerator-s3-1.3.1.jar" && \
    curl -fsSL https://repo1.maven.org/maven2/io/delta/delta-spark_2.13/4.4.0/delta-spark_2.13-4.4.0.jar -o "${SPARK_HOME}/jars/delta-spark_2.13-4.4.0.jar" && \
    curl -fsSL https://repo1.maven.org/maven2/io/delta/delta-storage/4.4.0/delta-storage-4.4.0.jar -o "${SPARK_HOME}/jars/delta-storage-4.4.0.jar"

# Create a dedicated non-root user for the Workspace/Jupyter runtime.
RUN groupadd --system workspace && \
    useradd --system --gid workspace --create-home --home-dir /home/workspace workspace && \
    mkdir -p /workspace /home/workspace && \
    chown -R workspace:workspace /home/workspace /workspace

WORKDIR /workspace
EXPOSE 8888

USER workspace

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser"]
