from backend.app.spark.session import create_spark_session


def main():
    spark = create_spark_session()

    print("Spark version:", spark.version)
    print("Driver memory:", spark.conf.get("spark.driver.memory"))

    data = [
        ("Vicky", 25),
        ("Rahul", 30),
        ("Anu", 28),
    ]

    df = spark.createDataFrame(data, ["name", "age"])

    df.show()

    spark.stop()


if __name__ == "__main__":
    main()

