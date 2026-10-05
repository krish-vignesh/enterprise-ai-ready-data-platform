from unittest.mock import Mock, patch

from app.lakehouse.bronze.source import SourceArtifact
from app.services.ingest import process_source_artifact


def _source_artifact() -> SourceArtifact:
    return SourceArtifact(
        company_id="company-001",
        company_name="Test Company",
        source_id="source-001",
        source_object_path="s3a://ai-data/test/source/file.csv",
    )


def test_process_source_artifact_new_artifact_happy_path() -> None:
    spark = Mock()
    source_artifact = _source_artifact()

    with patch("app.services.ingest.artifact_exists", return_value=False) as mock_artifact_exists, \
        patch("app.services.ingest.run_bronze_ingestion", return_value={
            "status": "success",
            "ingestion_id": "ing-123",
            "bronze_table_path": "s3a://ai-data/bronze/tables/test_dataset/",
        }) as mock_bronze, \
        patch("app.services.ingest.run_silver_pipeline", return_value=Mock()) as mock_silver, \
        patch("app.services.ingest.write_processed_artifact") as mock_processed_artifact, \
        patch("app.services.ingest.write_processing_state") as mock_processing_state:
        result = process_source_artifact(
            source_artifact=source_artifact,
            dataset_name="test_dataset",
            source="minio",
            source_format="csv",
            source_object_path="s3a://ai-data/test/source/file.csv",
            file_size=42,
            file_hash="abc123",
            spark=spark,
            silver_table_path="s3a://ai-data/silver/tables/test_dataset/",
        )

    assert result["status"] == "SUCCESS"
    mock_artifact_exists.assert_called_once()
    mock_bronze.assert_called_once()
    mock_silver.assert_called_once()
    mock_processed_artifact.assert_called_once()
    mock_processing_state.assert_called_once()


def test_process_source_artifact_skips_when_already_processed() -> None:
    source_artifact = _source_artifact()
    spark = Mock()

    with patch("app.services.ingest.artifact_exists", return_value=True) as mock_artifact_exists, \
        patch("app.services.ingest.run_bronze_ingestion") as mock_bronze, \
        patch("app.services.ingest.run_silver_pipeline") as mock_silver, \
        patch("app.services.ingest.write_processed_artifact") as mock_processed_artifact, \
        patch("app.services.ingest.write_processing_state") as mock_processing_state:
        result = process_source_artifact(
            source_artifact=source_artifact,
            dataset_name="test_dataset",
            source="minio",
            source_format="csv",
            source_object_path="s3a://ai-data/test/source/file.csv",
            file_size=42,
            file_hash="abc123",
            spark=spark,
            silver_table_path="s3a://ai-data/silver/tables/test_dataset/",
        )

    assert result["status"] == "SKIP"
    assert result["reason"] == "artifact already successfully processed"
    mock_artifact_exists.assert_called_once()
    mock_bronze.assert_not_called()
    mock_silver.assert_not_called()
    mock_processed_artifact.assert_not_called()
    mock_processing_state.assert_not_called()


def test_process_source_artifact_propagates_bronze_failure() -> None:
    source_artifact = _source_artifact()
    spark = Mock()

    with patch("app.services.ingest.artifact_exists", return_value=False), \
        patch("app.services.ingest.run_bronze_ingestion", side_effect=RuntimeError("bronze failed")), \
        patch("app.services.ingest.run_silver_pipeline") as mock_silver, \
        patch("app.services.ingest.write_processed_artifact") as mock_processed_artifact, \
        patch("app.services.ingest.write_processing_state") as mock_processing_state:
        try:
            process_source_artifact(
                source_artifact=source_artifact,
                dataset_name="test_dataset",
                source="minio",
                source_format="csv",
                source_object_path="s3a://ai-data/test/source/file.csv",
                file_size=42,
                file_hash="abc123",
                spark=spark,
                silver_table_path="s3a://ai-data/silver/tables/test_dataset/",
            )
            raise AssertionError("RuntimeError expected from Bronze failure")
        except RuntimeError as exc:
            assert "bronze failed" in str(exc)

    mock_silver.assert_not_called()
    mock_processed_artifact.assert_not_called()
    mock_processing_state.assert_not_called()


def test_process_source_artifact_propagates_silver_failure() -> None:
    source_artifact = _source_artifact()
    spark = Mock()

    with patch("app.services.ingest.artifact_exists", return_value=False), \
        patch("app.services.ingest.run_bronze_ingestion", return_value={
            "status": "success",
            "ingestion_id": "ing-456",
            "bronze_table_path": "s3a://ai-data/bronze/tables/test_dataset/",
        }), \
        patch("app.services.ingest.run_silver_pipeline", side_effect=RuntimeError("silver failed")) as mock_silver, \
        patch("app.services.ingest.write_processed_artifact") as mock_processed_artifact, \
        patch("app.services.ingest.write_processing_state") as mock_processing_state:
        try:
            process_source_artifact(
                source_artifact=source_artifact,
                dataset_name="test_dataset",
                source="minio",
                source_format="csv",
                source_object_path="s3a://ai-data/test/source/file.csv",
                file_size=42,
                file_hash="abc123",
                spark=spark,
                silver_table_path="s3a://ai-data/silver/tables/test_dataset/",
            )
            raise AssertionError("RuntimeError expected from Silver failure")
        except RuntimeError as exc:
            assert "silver failed" in str(exc)

    mock_silver.assert_called_once()
    mock_processed_artifact.assert_not_called()
    mock_processing_state.assert_not_called()


def test_process_source_artifact_propagates_processed_artifact_write_failure() -> None:
    source_artifact = _source_artifact()
    spark = Mock()

    with patch("app.services.ingest.artifact_exists", return_value=False), \
        patch("app.services.ingest.run_bronze_ingestion", return_value={
            "status": "success",
            "ingestion_id": "ing-789",
            "bronze_table_path": "s3a://ai-data/bronze/tables/test_dataset/",
        }), \
        patch("app.services.ingest.run_silver_pipeline", return_value=Mock()), \
        patch("app.services.ingest.write_processed_artifact", side_effect=RuntimeError("processed artifact write failed")), \
        patch("app.services.ingest.write_processing_state") as mock_processing_state:
        try:
            process_source_artifact(
                source_artifact=source_artifact,
                dataset_name="test_dataset",
                source="minio",
                source_format="csv",
                source_object_path="s3a://ai-data/test/source/file.csv",
                file_size=42,
                file_hash="abc123",
                spark=spark,
                silver_table_path="s3a://ai-data/silver/tables/test_dataset/",
            )
            raise AssertionError("RuntimeError expected from ProcessedArtifact write failure")
        except RuntimeError as exc:
            assert "processed artifact write failed" in str(exc)

    mock_processing_state.assert_not_called()
