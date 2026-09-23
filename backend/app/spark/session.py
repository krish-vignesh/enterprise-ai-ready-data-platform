"""
Create and return a SparkSession for the application.
"""

from pyspark.sql import SparkSession

def create_spark_session() -> SparkSession:
    """
    Create and return a SparkSession with the necessary configurations.
    """
    spark = (
        SparkSession.builder
        .appName("Enterprise AI Ready Data Platform")
        .getOrCreate()
    )
    return spark