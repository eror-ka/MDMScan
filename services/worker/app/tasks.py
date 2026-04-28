from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import structlog
from celery import Celery
from celery.schedules import crontab
from celery.signals import beat_init
from sqlalchemy import select

from app.config import settings
from app.db import get_session
from app.logging_config import configure_logging
from app.models import Finding as FindingModel
from app.models import ScanArtifact, ScanJob
from app.parsers import base as parser_base
from app.parsers import cosign, dive, dockle, osv, syft, trivy, trufflehog
from app.scanners import run_all
from app.storage import s3_client, upload_bytes, upload_file

configure_logging()
log = structlog.get_logger()

# ── Celery app ────────────────────────────────────────────────────────────────

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

celery_app.conf.beat_schedule = {
    "cleanup-orphan-temp": {
        "task": "mdmscan.cleanup_orphan_temp",
        "schedule": crontab(minute=0),       # каждый час в :00
    },
    "cleanup-old-scans": {
        "task": "mdmscan.cleanup_old_scans",
        "schedule": crontab(hour=3, minute=0),  # ежедневно в 03:00 UTC
    },
    "prune-docker-images": {
        "task": "mdmscan.prune_docker_images",
        "schedule": crontab(minute=30),      # каждый час в :30
    },
}

# ── Prometheus: beat-процесс запускает HTTP-сервер метрик ─────────────────────

@beat_init.connect
def on_beat_init(sender, **kwargs):
    if os.getenv("METRICS_SERVER", "false").lower() == "true":
        os.makedirs(settings.prometheus_multiproc_dir, exist_ok=True)
        from app.metrics import start_metrics_server
        start_metrics_server()
        log.info("metrics.server.started", port=settings.metrics_port)


# ── Импорт метрик (после env-настройки prometheus_multiproc_dir) ──────────────

from app.metrics import (  # noqa: E402
    cleanup_runs_total,
    findings_total,
    scan_duration_seconds,
    scanner_duration_seconds,
    scans_total,
)

# ── Security score ────────────────────────────────────────────────────────────

_SEVERITY_WEIGHT = {"CRITICAL": 5.0, "HIGH": 1.0, "MEDIUM": 0.1}


def _compute_security_score(findings: list[parser_base.Finding]) -> int:
    cats: dict[str, list[parser_base.Finding]] = {}
    for f in findings:
        cats.setdefault(f.category, []).append(f)

    total_penalty = 0.0

    # Vulnerabilities (max -65): tiered, non-additive — worst tier applies
    vuln = cats.get("vuln", [])
    n_crit = sum(1 for f in vuln if f.severity == "CRITICAL")
    n_high = sum(1 for f in vuln if f.severity == "HIGH")
    if n_crit > 1:
        total_penalty += 65
    elif n_crit == 1:
        total_penalty += 50
    elif n_high >= 5:
        total_penalty += 10
    elif n_high >= 1:
        total_penalty += 5

    # Misconfigurations (max -20): additive by severity presence
    misconfig = cats.get("misconfig", [])
    mc_penalty = 0.0
    if any(f.severity == "CRITICAL" for f in misconfig):
        mc_penalty += 12.5
    if any(f.severity == "HIGH" for f in misconfig):
        mc_penalty += 5.0
    if any(f.severity == "MEDIUM" for f in misconfig):
        mc_penalty += 2.5
    total_penalty += min(20.0, mc_penalty)

    # Secrets (max -10): badness-based, threshold = 5 HIGH-equiv
    secret = cats.get("secret", [])
    s_badness = sum(_SEVERITY_WEIGHT.get(f.severity, 0.0) for f in secret)
    if s_badness > 0:
        total_penalty += min(10.0, s_badness / 5.0 * 10.0)

    # Hygiene / image efficiency (max -5): badness-based, threshold = 10 HIGH-equiv
    hygiene = cats.get("hygiene", [])
    h_badness = sum(_SEVERITY_WEIGHT.get(f.severity, 0.0) for f in hygiene)
    if h_badness > 0:
        total_penalty += min(5.0, h_badness / 10.0 * 5.0)

    # Minimum 1-point penalty for any findings (accounts for LOW/UNKNOWN)
    if findings and total_penalty < 1.0:
        total_penalty = 1.0

    score = max(0, round(100 - total_penalty))

    # Floor at 75 when no CRITICAL vulnerabilities
    if not any(f.severity == "CRITICAL" and f.category == "vuln" for f in findings):
        score = max(75, score)

    return score


_PARSERS: dict[str, tuple] = {
    "trivy": (trivy.parse, "trivy.json"),
    "syft": (syft.parse, "syft.spdx.json"),
    "dockle": (dockle.parse, "dockle.json"),
    "osv-scanner": (osv.parse, "osv.json"),
    "dive": (dive.parse, "dive.json"),
    "trufflehog": (trufflehog.parse, "trufflehog.ndjson"),
    "cosign": (cosign.parse, "cosign.txt"),
}

# ── Основная задача ───────────────────────────────────────────────────────────


@celery_app.task(name="mdmscan.scan_image", bind=True)
def scan_image(self, image_ref: str, scan_id: str | None = None) -> dict:
    if scan_id is None:
        scan_id = str(uuid.uuid4())
    workdir = Path(settings.scan_workdir) / scan_id
    t0 = time.monotonic()
    log.info("scan.start", scan_id=scan_id, image=image_ref)

    with get_session() as session:
        job = session.get(ScanJob, scan_id)
        if job is None:
            session.add(ScanJob(id=scan_id, image_ref=image_ref, status="running"))
        else:
            job.status = "running"

    try:
        results = run_all(image_ref, workdir)
        scanner_statuses = {r.name: r.status for r in results}

        for r in results:
            scanner_duration_seconds.labels(scanner=r.name, status=r.status).observe(
                r.duration_s
            )

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
                findings_total.labels(category=f.category, severity=f.severity).inc()

            job = session.get(ScanJob, scan_id)
            job.status = "done"
            job.finished_at = datetime.utcnow()
            job.scanner_statuses = scanner_statuses
            job.security_score = _compute_security_score(deduped)

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

        elapsed = time.monotonic() - t0
        scans_total.labels(status="done").inc()
        scan_duration_seconds.labels(status="done").observe(elapsed)
        log.info("scan.done", scan_id=scan_id, findings=len(deduped), duration_s=round(elapsed, 2))
        return manifest

    except Exception as exc:
        elapsed = time.monotonic() - t0
        scans_total.labels(status="failed").inc()
        scan_duration_seconds.labels(status="failed").observe(elapsed)
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


# ── Периодические задачи ──────────────────────────────────────────────────────


@celery_app.task(name="mdmscan.cleanup_orphan_temp")
def cleanup_orphan_temp() -> dict:
    """Удаляет зависшие рабочие директории сканов и помечает их как failed в БД."""
    workdir = Path(settings.scan_workdir)
    if not workdir.exists():
        return {"removed": 0}

    # Директория, которой больше 2× таймаута, считается зависшей
    threshold = datetime.now(tz=timezone.utc) - timedelta(
        seconds=settings.scan_timeout_seconds * 2
    )
    removed = 0
    stuck_marked = 0

    for scan_dir in workdir.iterdir():
        if not scan_dir.is_dir():
            continue
        try:
            uuid.UUID(scan_dir.name)
        except ValueError:
            continue  # не scan_id — пропускаем

        mtime = datetime.fromtimestamp(scan_dir.stat().st_mtime, tz=timezone.utc)
        if mtime >= threshold:
            continue

        scan_id = scan_dir.name
        with get_session() as session:
            job = session.get(ScanJob, scan_id)
            if job and job.status == "running":
                job.status = "failed"
                job.finished_at = datetime.utcnow()
                stuck_marked += 1
                log.warning("cleanup.stuck_scan", scan_id=scan_id)

        shutil.rmtree(scan_dir, ignore_errors=True)
        removed += 1

    cleanup_runs_total.labels(task="cleanup_orphan_temp", status="ok").inc()
    log.info("cleanup.orphan_temp.done", removed=removed, stuck_marked=stuck_marked)
    return {"removed": removed, "stuck_marked": stuck_marked}


@celery_app.task(name="mdmscan.cleanup_old_scans")
def cleanup_old_scans() -> dict:
    """Удаляет из MinIO и БД сканы старше SCAN_RETENTION_DAYS дней."""
    cutoff = datetime.utcnow() - timedelta(days=settings.scan_retention_days)
    deleted_db = 0
    deleted_s3_objects = 0
    errors = 0

    with get_session() as session:
        old_jobs = session.scalars(
            select(ScanJob).where(
                ScanJob.created_at < cutoff,
                ScanJob.status.in_(["done", "failed"]),
            )
        ).all()

        client = s3_client()
        for job in old_jobs:
            # Удаляем объекты из MinIO с префиксом {scan_id}/
            try:
                paginator = client.get_paginator("list_objects_v2")
                objects_to_delete = []
                for page in paginator.paginate(
                    Bucket=settings.s3_bucket_raw, Prefix=f"{job.id}/"
                ):
                    for obj in page.get("Contents", []):
                        objects_to_delete.append({"Key": obj["Key"]})

                if objects_to_delete:
                    client.delete_objects(
                        Bucket=settings.s3_bucket_raw,
                        Delete={"Objects": objects_to_delete},
                    )
                    deleted_s3_objects += len(objects_to_delete)
            except Exception as exc:
                log.warning("cleanup.s3.error", scan_id=job.id, err=str(exc))
                errors += 1

            session.delete(job)
            deleted_db += 1

    cleanup_runs_total.labels(task="cleanup_old_scans", status="ok").inc()
    log.info(
        "cleanup.old_scans.done",
        deleted_db=deleted_db,
        deleted_s3_objects=deleted_s3_objects,
        errors=errors,
        retention_days=settings.scan_retention_days,
    )
    return {
        "deleted_db": deleted_db,
        "deleted_s3_objects": deleted_s3_objects,
        "errors": errors,
    }


@celery_app.task(name="mdmscan.prune_docker_images")
def prune_docker_images() -> dict:
    """Запускает docker image prune для освобождения дискового пространства."""
    try:
        result = subprocess.run(
            ["docker", "image", "prune", "-f"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        status = "ok" if result.returncode == 0 else "error"
        reclaimed = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
        log.info("prune.docker.done", status=status, reclaimed=reclaimed)
    except subprocess.TimeoutExpired:
        status = "timeout"
        reclaimed = ""
        log.warning("prune.docker.timeout")
    except Exception as exc:
        status = "error"
        reclaimed = ""
        log.error("prune.docker.error", err=str(exc))

    cleanup_runs_total.labels(task="prune_docker_images", status=status).inc()
    return {"status": status, "reclaimed": reclaimed}
