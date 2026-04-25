"""Celery-приложение и единственная пока таска scan_image."""

from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path

import structlog
from celery import Celery

from app.config import settings
from app.scanners import run_all
from app.storage import upload_bytes, upload_file

log = structlog.get_logger()

celery_app = Celery(
    "mdmscan",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(name="mdmscan.scan_image", bind=True)
def scan_image(self, image_ref: str) -> dict:
    """Сканирует Docker-образ и заливает все артефакты в MinIO.

    Возвращает: {scan_id, image, results: [{scanner, status, key, ...}, ...]}
    """
    scan_id = str(uuid.uuid4())
    workdir = Path(settings.scan_workdir) / scan_id
    log.info("scan.start", scan_id=scan_id, image=image_ref)

    try:
        results = run_all(image_ref, workdir)

        # Загружаем каждый успешный артефакт в MinIO
        manifest = {
            "scan_id": scan_id,
            "image": image_ref,
            "results": [],
        }
        for r in results:
            entry = {
                "scanner": r.name,
                "status": r.status,
                "exit_code": r.exit_code,
                "duration_s": round(r.duration_s, 2),
                "stderr_tail": r.stderr_tail,
            }
            if r.output_path is not None:
                key = f"{scan_id}/{r.output_path.name}"
                upload_file(r.output_path, settings.s3_bucket_raw, key)
                entry["s3_key"] = key
            manifest["results"].append(entry)

        # Манифест — общий индекс скана, удобен для отладки и Этапа 4
        upload_bytes(
            json.dumps(manifest, indent=2, ensure_ascii=False).encode("utf-8"),
            bucket=settings.s3_bucket_raw,
            key=f"{scan_id}/manifest.json",
        )
        log.info("scan.done", scan_id=scan_id)
        return manifest

    finally:
        # cleanup рабочей директории — обязательно
        if workdir.exists():
            shutil.rmtree(workdir, ignore_errors=True)
            log.info("scan.cleanup", scan_id=scan_id)
