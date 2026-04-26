from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.celery_client import celery_app
from app.db import get_db
from app.models import Finding, ScanJob
from app.schemas import (
    FindingsListOut,
    FindingOut,
    ScanJobOut,
    ScanSubmitRequest,
    ScanSubmitResponse,
)

router = APIRouter(prefix="/scans", tags=["scans"])

DbDep = Annotated[Session, Depends(get_db)]


@router.post("", status_code=202, response_model=ScanSubmitResponse)
def submit_scan(body: ScanSubmitRequest, db: DbDep) -> ScanSubmitResponse:
    scan_id = str(uuid.uuid4())
    celery_app.send_task(
        "mdmscan.scan_image",
        args=[body.image],
        kwargs={"scan_id": scan_id},
    )
    return ScanSubmitResponse(scan_id=scan_id, status="pending")


@router.get("/{scan_id}", response_model=ScanJobOut)
def get_scan(scan_id: str, db: DbDep) -> ScanJobOut:
    job = db.get(ScanJob, scan_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Scan not found")

    findings_count = db.scalar(
        select(func.count()).where(Finding.scan_job_id == scan_id)
    )
    return ScanJobOut(
        scan_id=job.id,
        image_ref=job.image_ref,
        status=job.status,
        created_at=job.created_at,
        finished_at=job.finished_at,
        scanner_statuses=job.scanner_statuses,
        findings_count=findings_count or 0,
    )


@router.get("/{scan_id}/findings", response_model=FindingsListOut)
def get_findings(
    scan_id: str,
    db: DbDep,
    severity: Annotated[str | None, Query()] = None,
    category: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> FindingsListOut:
    if db.get(ScanJob, scan_id) is None:
        raise HTTPException(status_code=404, detail="Scan not found")

    stmt = select(Finding).where(Finding.scan_job_id == scan_id)
    if severity:
        stmt = stmt.where(Finding.severity == severity.upper())
    if category:
        stmt = stmt.where(Finding.category == category.lower())

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = db.scalars(stmt.offset(offset).limit(limit)).all()

    items = [
        FindingOut(
            id=f.id,
            fingerprint=f.fingerprint,
            category=f.category,
            severity=f.severity,
            title=f.title,
            description=f.description,
            package=f.package,
            version=f.version,
            fix_version=f.fix_version,
            location=f.location,
            raw_ref=f.raw_ref,
            sources=f.sources,
            fix_advice=f.fix_advice,
        )
        for f in rows
    ]
    return FindingsListOut(scan_id=scan_id, total=total or 0, items=items)
