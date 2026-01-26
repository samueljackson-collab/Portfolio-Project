"""Initial migration with User and Content models

Revision ID: 001_initial
Revises:
Create Date: 2025-11-10 18:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create users and content tables."""
    # Create users table
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="User unique identifier",
        ),
        sa.Column(
            "email", sa.String(length=255), nullable=False, comment="User email address"
        ),
        sa.Column(
            "hashed_password",
            sa.String(length=255),
            nullable=False,
            comment="Bcrypt hashed password",
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
            comment="Account active status",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Account creation timestamp",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Last update timestamp",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # Create content table
    op.create_table(
        "content",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="Content unique identifier",
        ),
        sa.Column(
            "title", sa.String(length=255), nullable=False, comment="Content title"
        ),
        sa.Column("body", sa.Text(), nullable=True, comment="Content body text"),
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment="Content owner user ID",
        ),
        sa.Column(
            "is_published",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
            comment="Publication status",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Content creation timestamp",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Last update timestamp",
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_content_owner_id"), "content", ["owner_id"], unique=False)
    op.create_index(
        op.f("ix_content_created_at"), "content", ["created_at"], unique=False
    )
    op.create_index(
        "ix_content_owner_created", "content", ["owner_id", "created_at"], unique=False
    )


def downgrade() -> None:
    """Drop content and users tables."""
    op.drop_index("ix_content_owner_created", table_name="content")
    op.drop_index(op.f("ix_content_created_at"), table_name="content")
    op.drop_index(op.f("ix_content_owner_id"), table_name="content")
    op.drop_table("content")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
