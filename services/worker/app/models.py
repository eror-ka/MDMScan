from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ScanJob(Base):
    __tablename__ = "scan_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    image_ref: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="running")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    scanner_statuses: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    findings: Mapped[list[Finding]] = relationship(
        "Finding", back_populates="scan_job", cascade="all, delete-orphan"
    )
    artifacts: Mapped[list[ScanArtifact]] = relationship(
        "ScanArtifact", back_populates="scan_job", cascade="all, delete-orphan"
    )


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scan_job_id: Mapped[str] = mapped_column(String(36), ForeignKey("scan_jobs.id"), nullable=False, index=True)
    fingerprint: Mapped[str] = mapped_column(String(40), nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    severity: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    package: Mapped[str | None] = mapped_column(String(256), nullable=True)
    version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    fix_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    location: Mapped[str | None] = mapped_column(String(512), nullable=True)
    raw_ref: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    sources: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    fix_advice: Mapped[str | None] = mapped_column(Text, nullable=True)

    scan_job: Mapped[ScanJob] = relationship("ScanJob", back_populates="findings")

    __table_args__ = (UniqueConstraint("scan_job_id", "fingerprint", name="uq_finding_fingerprint"),)


class ScanArtifact(Base):
    __tablename__ = "scan_artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scan_job_id: Mapped[str] = mapped_column(String(36), ForeignKey("scan_jobs.id"), nullable=False, index=True)
    scanner: Mapped[str] = mapped_column(String(32), nullable=False)
    s3_bucket: Mapped[str] = mapped_column(String(128), nullable=False)
    s3_key: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)

    scan_job: Mapped[ScanJob] = relationship("ScanJob", back_populates="artifacts")
