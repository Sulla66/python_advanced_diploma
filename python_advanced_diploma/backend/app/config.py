from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@db:5432/db"
    MEDIA_DIR: str = "media"

    class Config:
        env_file = ".env"


settings = Settings()