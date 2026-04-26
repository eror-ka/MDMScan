from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    web_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
