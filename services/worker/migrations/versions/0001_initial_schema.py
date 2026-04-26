"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-26

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scan_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("image_ref", sa.String(512), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="running"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("scanner_statuses", postgresql.JSONB(), nullable=True),
    )
    op.create_index("ix_scan_jobs_image_ref", "scan_jobs", ["image_ref"])

    op.create_table(
        "findings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("scan_job_id", sa.String(36), sa.ForeignKey("scan_jobs.id"), nullable=False),
        sa.Column("fingerprint", sa.String(40), nullable=False),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("severity", sa.String(10), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("package", sa.String(256), nullable=True),
        sa.Column("version", sa.String(128), nullable=True),
        sa.Column("fix_version", sa.String(128), nullable=True),
        sa.Column("location", sa.String(512), nullable=True),
        sa.Column("raw_ref", sa.String(128), nullable=True),
        sa.Column("sources", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("fix_advice", sa.Text(), nullable=True),
        sa.UniqueConstraint("scan_job_id", "fingerprint", name="uq_finding_fingerprint"),
    )
    op.create_index("ix_findings_scan_job_id", "findings", ["scan_job_id"])
    op.create_index("ix_findings_severity", "findings", ["severity"])
    op.create_index("ix_findings_raw_ref", "findings", ["raw_ref"])

    op.create_table(
        "scan_artifacts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("scan_job_id", sa.String(36), sa.ForeignKey("scan_jobs.id"), nullable=False),
        sa.Column("scanner", sa.String(32), nullable=False),
        sa.Column("s3_bucket", sa.String(128), nullable=False),
        sa.Column("s3_key", sa.String(512), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
    )
    op.create_index("ix_scan_artifacts_scan_job_id", "scan_artifacts", ["scan_job_id"])


def downgrade() -> None:
    op.drop_table("scan_artifacts")
    op.drop_table("findings")
    op.drop_table("scan_jobs")
