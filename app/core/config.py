from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Organizations Directory API"
    version: str = "1.0.0"
    database_url: str = "postgresql+asyncpg://postgres:password@db:5432/organizations_db"
    api_key: str = "default_api_key"
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    max_activity_depth: int = 3

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()