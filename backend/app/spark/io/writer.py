def write_data(df, output_path, output_format, mode="error", options=None):
    """Write a Spark DataFrame to a supported output format at the given path."""
    normalized_format = str(output_format).lower()
    supported_formats = {"parquet"}
    supported_modes = {"append", "overwrite", "ignore", "error", "errorifexists"}

    if normalized_format not in supported_formats:
        raise ValueError(
            f"Unsupported output format '{output_format}'. "
            f"Supported formats: {sorted(supported_formats)}"
        )

    if mode not in supported_modes:
        raise ValueError(
            f"Unsupported write mode '{mode}'. "
            f"Supported modes: {sorted(supported_modes)}"
        )

    if options is None:
        options = {}

    if normalized_format == "parquet":
        df.write.mode(mode).parquet(output_path, **options)
        return None

    raise ValueError(
        f"Unsupported output format '{output_format}'. "
        f"Supported formats: {sorted(supported_formats)}"
    )
