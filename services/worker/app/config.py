"""Конфигурация воркера, читается из переменных окружения."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    # Redis (Celery broker + result backend)
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    # MinIO / S3
    s3_endpoint: str = os.getenv("S3_ENDPOINT", "http://minio:9000")
    s3_access_key: str = os.getenv("S3_ACCESS_KEY", "")
    s3_secret_key: str = os.getenv("S3_SECRET_KEY", "")
    s3_region: str = os.getenv("S3_REGION", "us-east-1")
    s3_bucket_raw: str = os.getenv("S3_BUCKET_RAW", "raw-scans")

    # Сканирование
    scan_timeout_seconds: int = int(os.getenv("SCAN_TIMEOUT_SECONDS", "600"))
    scan_workdir: str = os.getenv("SCAN_WORKDIR", "/tmp/scans")


settings = Settings()
