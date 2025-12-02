"""Add unique constraint on album owner/name pairs

Revision ID: 003_album_owner_name_unique
Revises: 002_photos_albums
Create Date: 2025-11-15 01:01:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003_album_owner_name_unique'
down_revision: Union[str, None] = '002_photos_albums'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the unique constraint so two albums can't share the same name per user."""
    op.create_unique_constraint(
        'uq_albums_owner_name',
        'albums',
        ['owner_id', 'name']
    )


def downgrade() -> None:
    """Drop the unique constraint."""
    op.drop_constraint('uq_albums_owner_name', 'albums', type_='unique')
