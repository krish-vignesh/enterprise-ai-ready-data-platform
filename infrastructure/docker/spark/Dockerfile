# Base Linux environment for our custom Spark image
FROM ubuntu:24.04

# Install Java 21 and wget for the Spark runtime
RUN apt-get update && \
    apt-get install -y openjdk-21-jdk wget && \
    rm -rf /var/lib/apt/lists/*

# Install Python 3.12 and pip
RUN apt-get update && \
    apt-get install -y python3.12 python3.12-venv python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install the minimum Python packages needed for the current ingestion-to-Spark path
RUN python3.12 -m pip install --no-cache-dir --break-system-packages pandas openpyxl camelot-py

# Copy the verified Apache Spark 4.2.0 distribution into the image
COPY infrastructure/docker/spark/spark-4.2.0-bin-hadoop3.tgz /tmp/

# Extract and install Spark
RUN tar -xzf /tmp/spark-4.2.0-bin-hadoop3.tgz -C /opt && \
    mv /opt/spark-4.2.0-bin-hadoop3 /opt/spark && \
    rm /tmp/spark-4.2.0-bin-hadoop3.tgz 

# Add S3A support for MinIO / S3-compatible object storage
RUN wget -q -O /opt/spark/jars/hadoop-aws-3.5.0.jar \
        https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.5.0/hadoop-aws-3.5.0.jar && \
    wget -q -O /opt/spark/jars/bundle-2.35.4.jar \
        https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.35.4/bundle-2.35.4.jar && \
    wget -q -O /opt/spark/jars/analyticsaccelerator-s3-1.3.1.jar \
        https://repo1.maven.org/maven2/software/amazon/s3/analyticsaccelerator/analyticsaccelerator-s3/1.3.1/analyticsaccelerator-s3-1.3.1.jar

    # Define the locations of Java and Spark inside the container
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV SPARK_HOME=/opt/spark

# Make Java and Spark commands available from the terminal
ENV PATH="${JAVA_HOME}/bin:${SPARK_HOME}/bin:${SPARK_HOME}/sbin:${PATH}"

# Tell Spark/PySpark to use Python 3.12
ENV PYSPARK_PYTHON=/usr/bin/python3.12
ENV PYSPARK_DRIVER_PYTHON=/usr/bin/python3.12

# Tell Python where Spark's Python libraries are located
ENV PYTHONPATH="/workspace/backend:${SPARK_HOME}/python"