from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str

    minio_host: str
    minio_port: int
    minio_username: str
    minio_password: str
    workspace_records_bucket: str

    database_url: str

    max_upload_file_size_bytes: int = Field(
        default=50 * 1024 * 1024,
        gt=0,
    )


settings = Settings()
