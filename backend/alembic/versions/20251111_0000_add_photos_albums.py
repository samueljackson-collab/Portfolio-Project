"""Add photo and album tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20251111_0000_add_photos_albums"
down_revision = "20251110_1800_initial_migration"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "albums",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type", sa.String(length=32), nullable=False, server_default="custom"),
        sa.Column("cover_photo_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("photo_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "photos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("album_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=64), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("capture_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("camera_make", sa.String(length=128), nullable=True),
        sa.Column("camera_model", sa.String(length=128), nullable=True),
        sa.Column("focal_length", sa.String(length=64), nullable=True),
        sa.Column("aperture", sa.String(length=32), nullable=True),
        sa.Column("iso", sa.Integer(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("location_name", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=128), nullable=True),
        sa.Column("state", sa.String(length=128), nullable=True),
        sa.Column("country", sa.String(length=128), nullable=True),
        sa.Column("storage_path", sa.String(length=512), nullable=False),
        sa.Column("thumbnail_path", sa.String(length=512), nullable=True),
        sa.Column("checksum", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["album_id"], ["albums.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_albums_owner_type", "albums", ["owner_id", "type"])
    op.create_index("ix_albums_owner_updated", "albums", ["owner_id", "updated_at"])
    op.create_unique_constraint("uq_albums_owner_name", "albums", ["owner_id", "name"])
    op.create_index("ix_photos_owner_capture", "photos", ["owner_id", "capture_date"])
    op.create_index("ix_photos_owner_created", "photos", ["owner_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_photos_owner_created", table_name="photos")
    op.drop_index("ix_photos_owner_capture", table_name="photos")
    op.drop_table("photos")
    op.drop_constraint("uq_albums_owner_name", "albums", type_="unique")
    op.drop_index("ix_albums_owner_updated", table_name="albums")
    op.drop_index("ix_albums_owner_type", table_name="albums")
    op.drop_table("albums")
