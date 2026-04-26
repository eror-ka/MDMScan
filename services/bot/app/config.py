from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    api_url: str = "http://api:8000"

    class Config:
        env_file = ".env"


settings = Settings()
