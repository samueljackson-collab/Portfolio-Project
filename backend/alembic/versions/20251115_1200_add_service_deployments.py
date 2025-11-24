"""add service deployments table

Revision ID: 20251115_1200
Revises: 20251111_0000_add_photos_albums
Create Date: 2025-11-15 12:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20251115_1200"
down_revision = "20251111_0000_add_photos_albums"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "service_deployments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("service_name", sa.String(length=100), nullable=False),
        sa.Column("region", sa.String(length=50), nullable=False),
        sa.Column("cluster", sa.String(length=120), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("git_commit", sa.String(length=64), nullable=True),
        sa.Column("desired_replicas", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("available_replicas", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("service_name", "region", "cluster", name="uq_service_region_cluster"),
    )
    op.create_index("ix_service_region", "service_deployments", ["region"])
    op.create_index("ix_service_status", "service_deployments", ["service_name", "status"])


def downgrade() -> None:
    op.drop_index("ix_service_status", table_name="service_deployments")
    op.drop_index("ix_service_region", table_name="service_deployments")
    op.drop_table("service_deployments")
