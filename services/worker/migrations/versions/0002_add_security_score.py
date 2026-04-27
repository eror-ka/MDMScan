"""add security_score to scan_jobs

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-27

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("scan_jobs", sa.Column("security_score", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("scan_jobs", "security_score")
