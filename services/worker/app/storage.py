"""Обёртка над boto3 для работы с MinIO."""

from __future__ import annotations

from pathlib import Path

import boto3
from botocore.client import Config

from app.config import settings


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4"),
    )


def upload_file(local_path: Path, bucket: str, key: str) -> None:
    s3_client().upload_file(str(local_path), bucket, key)


def upload_bytes(
    data: bytes, bucket: str, key: str, content_type: str = "application/json"
) -> None:
    s3_client().put_object(Bucket=bucket, Key=key, Body=data, ContentType=content_type)
