from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    app_name: str = "SIH 26120 Digital Twin API"
    app_version: str = "1.0.0"
    environment: str = "local"
    database_url: str = f"sqlite:///{(ROOT_DIR / 'backend' / 'sih26120.db').as_posix()}"
    jwt_secret: str = "CHANGE_ME_BEFORE_DEPLOYMENT_SIH26120"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 480
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    data_path: str = str(ROOT_DIR / "ml" / "data" / "processed" / "cleaned.csv")
    artifact_dir: str = str(ROOT_DIR / "ml" / "artifacts")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()


def cors_list() -> list[str]:
    return [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
