from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ScanSubmitRequest(BaseModel):
    image: str


class ScanSubmitResponse(BaseModel):
    scan_id: str
    status: str


class ScanListItem(BaseModel):
    scan_id: str
    image_ref: str
    status: str
    created_at: datetime
    finished_at: datetime | None
    findings_count: int
    security_score: int | None = None


class ScanJobOut(BaseModel):
    scan_id: str
    image_ref: str
    status: str
    created_at: datetime
    finished_at: datetime | None
    scanner_statuses: dict | None
    findings_count: int
    security_score: int | None = None


class FindingOut(BaseModel):
    id: int
    fingerprint: str
    category: str
    severity: str
    title: str
    description: str | None
    package: str | None
    version: str | None
    fix_version: str | None
    location: str | None
    raw_ref: str | None
    sources: list[str]
    fix_advice: str | None


class FindingsListOut(BaseModel):
    scan_id: str
    total: int
    items: list[FindingOut]
