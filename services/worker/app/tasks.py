from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path

import structlog
from celery import Celery

from app.config import settings
from app.db import get_session
from app.models import Finding as FindingModel
from app.models import ScanArtifact, ScanJob
from app.parsers import base as parser_base
from app.parsers import cosign, dockle, dive, osv, syft, trivy, trufflehog
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
    broker_connection_retry_on_startup=True,
)

_PARSERS: dict[str, tuple] = {
    "trivy": (trivy.parse, "trivy.json"),
    "syft": (syft.parse, "syft.spdx.json"),
    "dockle": (dockle.parse, "dockle.json"),
    "osv-scanner": (osv.parse, "osv.json"),
    "dive": (dive.parse, "dive.json"),
    "trufflehog": (trufflehog.parse, "trufflehog.ndjson"),
    "cosign": (cosign.parse, "cosign.txt"),
}


@celery_app.task(name="mdmscan.scan_image", bind=True)
def scan_image(self, image_ref: str) -> dict:
    scan_id = str(uuid.uuid4())
    workdir = Path(settings.scan_workdir) / scan_id
    log.info("scan.start", scan_id=scan_id, image=image_ref)

    with get_session() as session:
        session.add(ScanJob(id=scan_id, image_ref=image_ref, status="running"))

    try:
        results = run_all(image_ref, workdir)
        scanner_statuses = {r.name: r.status for r in results}

        all_findings: list[parser_base.Finding] = []

        with get_session() as session:
            for scanner_name, (parse_fn, filename) in _PARSERS.items():
                artifact_path = workdir / filename
                if not artifact_path.exists():
                    continue

                s3_key = f"{scan_id}/{filename}"
                try:
                    file_size = artifact_path.stat().st_size
                    upload_file(artifact_path, settings.s3_bucket_raw, s3_key)
                    session.add(
                        ScanArtifact(
                            scan_job_id=scan_id,
                            scanner=scanner_name,
                            s3_bucket=settings.s3_bucket_raw,
                            s3_key=s3_key,
                            file_size=file_size,
                        )
                    )
                except Exception as exc:
                    log.warning("upload.error", scanner=scanner_name, err=str(exc))

                try:
                    findings = parse_fn(artifact_path)
                    all_findings.extend(findings)
                except Exception as exc:
                    log.warning("parser.error", scanner=scanner_name, err=str(exc))

            deduped = parser_base.deduplicate(all_findings)
            for f in deduped:
                session.add(
                    FindingModel(
                        scan_job_id=scan_id,
                        fingerprint=f.fingerprint,
                        category=f.category,
                        severity=f.severity,
                        title=f.title,
                        description=f.description or None,
                        package=f.package,
                        version=f.version,
                        fix_version=f.fix_version,
                        location=f.location,
                        raw_ref=f.raw_ref,
                        sources=f.sources,
                        fix_advice=f.fix_advice,
                    )
                )

            job = session.get(ScanJob, scan_id)
            job.status = "done"
            job.finished_at = datetime.utcnow()
            job.scanner_statuses = scanner_statuses

        severity_counts: dict[str, int] = {}
        for f in deduped:
            severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1

        manifest = {
            "scan_id": scan_id,
            "image": image_ref,
            "findings_count": len(deduped),
            "severity_counts": severity_counts,
            "scanner_statuses": scanner_statuses,
        }
        upload_bytes(
            json.dumps(manifest, indent=2, ensure_ascii=False).encode(),
            bucket=settings.s3_bucket_raw,
            key=f"{scan_id}/manifest.json",
        )
        log.info("scan.done", scan_id=scan_id, findings=len(deduped))
        return manifest

    except Exception as exc:
        with get_session() as session:
            job = session.get(ScanJob, scan_id)
            if job:
                job.status = "failed"
                job.finished_at = datetime.utcnow()
        log.error("scan.failed", scan_id=scan_id, err=str(exc))
        raise

    finally:
        if workdir.exists():
            shutil.rmtree(workdir, ignore_errors=True)
            log.info("scan.cleanup", scan_id=scan_id)
