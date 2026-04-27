from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    web_url: str = "http://localhost:3000"
    proxy_url: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
