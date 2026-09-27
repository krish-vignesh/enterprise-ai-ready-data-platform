"""
Create and return a SparkSession for the application.
"""

from pyspark.sql import SparkSession


def create_spark_session() -> SparkSession:
    """
    Create and return a SparkSession with the necessary Delta configuration.
    """
    spark = (
        SparkSession.builder
        .appName("Enterprise AI Ready Data Platform")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .getOrCreate()
    )
    return spark