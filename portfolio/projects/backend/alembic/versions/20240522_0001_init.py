"""Initial schema

Revision ID: 20240522_0001
Revises: 
Create Date: 2024-05-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20240522_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "contents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    )
    op.create_index("ix_contents_owner", "contents", ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_contents_owner", table_name="contents")
    op.drop_table("contents")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
