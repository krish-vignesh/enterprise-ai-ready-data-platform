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

# Download and install Apache Spark 4.2.0
RUN wget -q https://archive.apache.org/dist/spark/spark-4.2.0/spark-4.2.0-bin-hadoop3.tgz && \
    tar -xzf spark-4.2.0-bin-hadoop3.tgz && \
    mv spark-4.2.0-bin-hadoop3 /opt/spark && \
    rm spark-4.2.0-bin-hadoop3.tgz

# Define the locations of Java and Spark inside the container
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV SPARK_HOME=/opt/spark

# Make Java and Spark commands available from the terminal
ENV PATH="${JAVA_HOME}/bin:${SPARK_HOME}/bin:${SPARK_HOME}/sbin:${PATH}"

# Tell Spark/PySpark to use Python 3.12
ENV PYSPARK_PYTHON=/usr/bin/python3.12
ENV PYSPARK_DRIVER_PYTHON=/usr/bin/python3.12

# Tell Python where Spark's Python libraries are located
ENV PYTHONPATH="${SPARK_HOME}/python"