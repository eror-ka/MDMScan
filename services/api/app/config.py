from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_dsn: str = "postgresql://mdmscan:mdmscan@postgres:5432/mdmscan"
    redis_url: str = "redis://redis:6379/0"
    miniapp_bot_token: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
