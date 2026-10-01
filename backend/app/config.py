from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "EcoVision AI"
    ENV: str = "dev"
    CORS_ORIGINS: str = "http://localhost:5173"
    DATABASE_URL: str = "postgresql+psycopg://localhost:5432/ecovision"
    MAX_UPLOAD_MB: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
