from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3] #were moving 3 folder higher so that .env is visible (parents(3))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env"
    )

    app_name: str
    minio_host: str
    minio_port: int
    minio_username: str
    minio_password: str


settings = Settings()

