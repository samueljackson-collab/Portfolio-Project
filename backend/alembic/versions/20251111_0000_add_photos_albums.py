"""Add photos and albums tables

Revision ID: 002_photos_albums
Revises: 001_initial
Create Date: 2025-11-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_photos_albums'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create albums and photos tables."""
    # Create albums table first (photos references albums)
    op.create_table(
        'albums',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Album unique identifier'),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Album owner user ID'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Album name'),
        sa.Column('type', sa.String(length=50), nullable=False, server_default='custom', comment='Album type: location, date, or custom'),
        sa.Column('photo_count', sa.Integer(), nullable=False, server_default='0', comment='Cached count of photos in album'),
        sa.Column('cover_photo_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Cover photo ID'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Album creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Last update timestamp'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_albums_owner_id'), 'albums', ['owner_id'], unique=False)
    op.create_index('ix_albums_owner_type', 'albums', ['owner_id', 'type'], unique=False)
    op.create_index('ix_albums_owner_updated', 'albums', ['owner_id', 'updated_at'], unique=False)
    op.create_unique_constraint('uq_albums_owner_name', 'albums', ['owner_id', 'name'])

    # Create photos table
    op.create_table(
        'photos',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, comment='Photo unique identifier'),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False, comment='Photo owner user ID'),
        sa.Column('album_id', postgresql.UUID(as_uuid=True), nullable=True, comment='Album ID (auto-organized)'),
        sa.Column('filename', sa.String(length=255), nullable=False, comment='Original filename'),
        sa.Column('file_path', sa.String(length=512), nullable=False, comment='Storage path on server'),
        sa.Column('thumbnail_path', sa.String(length=512), nullable=True, comment='Thumbnail storage path'),
        sa.Column('file_size', sa.Integer(), nullable=False, comment='File size in bytes'),
        sa.Column('mime_type', sa.String(length=50), nullable=False, server_default='image/jpeg', comment='Image MIME type'),
        sa.Column('width', sa.Integer(), nullable=True, comment='Image width in pixels'),
        sa.Column('height', sa.Integer(), nullable=True, comment='Image height in pixels'),
        sa.Column('capture_date', sa.DateTime(timezone=True), nullable=True, comment='Date photo was taken (from EXIF)'),
        sa.Column('upload_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Date photo was uploaded'),
        sa.Column('latitude', sa.Float(), nullable=True, comment='GPS latitude'),
        sa.Column('longitude', sa.Float(), nullable=True, comment='GPS longitude'),
        sa.Column('city', sa.String(length=255), nullable=True, comment='City name (reverse geocoded)'),
        sa.Column('state', sa.String(length=255), nullable=True, comment='State/region name'),
        sa.Column('country', sa.String(length=255), nullable=True, comment='Country name'),
        sa.Column('camera_make', sa.String(length=100), nullable=True, comment='Camera manufacturer'),
        sa.Column('camera_model', sa.String(length=100), nullable=True, comment='Camera model'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Record creation timestamp'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Last update timestamp'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['album_id'], ['albums.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('file_path')
    )
    op.create_index(op.f('ix_photos_owner_id'), 'photos', ['owner_id'], unique=False)
    op.create_index(op.f('ix_photos_album_id'), 'photos', ['album_id'], unique=False)
    op.create_index(op.f('ix_photos_capture_date'), 'photos', ['capture_date'], unique=False)
    op.create_index(op.f('ix_photos_city'), 'photos', ['city'], unique=False)
    op.create_index(op.f('ix_photos_country'), 'photos', ['country'], unique=False)
    op.create_index('ix_photos_owner_capture', 'photos', ['owner_id', 'capture_date'], unique=False)
    op.create_index('ix_photos_owner_city', 'photos', ['owner_id', 'city'], unique=False)
    op.create_index('ix_photos_album_capture', 'photos', ['album_id', 'capture_date'], unique=False)
    op.create_index('ix_photos_location', 'photos', ['latitude', 'longitude'], unique=False)

    # Now add the cover_photo_id foreign key to albums (circular reference)
    op.create_foreign_key(
        'fk_albums_cover_photo_id',
        'albums', 'photos',
        ['cover_photo_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    """Drop photos and albums tables."""
    # Drop foreign key first
    op.drop_constraint('fk_albums_cover_photo_id', 'albums', type_='foreignkey')

    # Drop photos table
    op.drop_index('ix_photos_location', table_name='photos')
    op.drop_index('ix_photos_album_capture', table_name='photos')
    op.drop_index('ix_photos_owner_city', table_name='photos')
    op.drop_index('ix_photos_owner_capture', table_name='photos')
    op.drop_index(op.f('ix_photos_country'), table_name='photos')
    op.drop_index(op.f('ix_photos_city'), table_name='photos')
    op.drop_index(op.f('ix_photos_capture_date'), table_name='photos')
    op.drop_index(op.f('ix_photos_album_id'), table_name='photos')
    op.drop_index(op.f('ix_photos_owner_id'), table_name='photos')
    op.drop_table('photos')

    # Drop albums table
    op.drop_constraint('uq_albums_owner_name', 'albums', type_='unique')
    op.drop_index('ix_albums_owner_updated', table_name='albums')
    op.drop_index('ix_albums_owner_type', table_name='albums')
    op.drop_index(op.f('ix_albums_owner_id'), table_name='albums')
    op.drop_table('albums')
