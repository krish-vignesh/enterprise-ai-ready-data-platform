def read_data(spark, input_path, input_format, options=None):
    """Read structured data from a supported input format into a Spark DataFrame.

    The caller must explicitly provide the input format; this function does not
    infer formats from file extensions.
    """
    normalized_format = str(input_format).lower()
    supported_formats = {"csv", "json", "jsonl", "parquet"}

    if normalized_format not in supported_formats:
        raise ValueError(
            f"Unsupported input format '{input_format}'. "
            f"Supported formats: {sorted(supported_formats)}"
        )

    reader = spark.read
    if options is None:
        options = {}

    if normalized_format == "csv":
        return reader.csv(input_path, **options)

    if normalized_format in {"json", "jsonl"}:
        return reader.json(input_path, **options)

    if normalized_format == "parquet":
        return reader.parquet(input_path, **options)

    raise ValueError(
        f"Unsupported input format '{input_format}'. "
        f"Supported formats: {sorted(supported_formats)}"
    )
