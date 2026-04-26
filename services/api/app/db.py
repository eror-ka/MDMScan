from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings

engine = create_engine(
    settings.postgres_dsn,
    pool_pre_ping=True,
    pool_size=2,
    max_overflow=4,
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
