from pyspark.sql import functions as F


def transform_customer_data(df):
    """Add a spending category derived from the total_spend column."""
    return df.withColumn(
        "spending_category",
        F.when(F.col("total_spend") < 3000, "Low")
        .when(
            (F.col("total_spend") >= 3000)
            & (F.col("total_spend") <= 6000),
            "Medium",
        )
        .when(F.col("total_spend") > 6000, "High")
        .otherwise("Low"),
    )