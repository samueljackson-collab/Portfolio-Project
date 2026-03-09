"""Initial tasks table

Revision ID: 0001
Revises:
Create Date: 2024-01-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the tasks table."""
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True, default='medium'),
        sa.Column('status', sa.String(length=20), nullable=True, default='pending'),
        sa.Column('assignee', sa.String(length=100), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for common queries
    op.create_index('ix_tasks_status', 'tasks', ['status'])
    op.create_index('ix_tasks_priority', 'tasks', ['priority'])
    op.create_index('ix_tasks_assignee', 'tasks', ['assignee'])
    op.create_index('ix_tasks_created_at', 'tasks', ['created_at'])


def downgrade() -> None:
    """Drop the tasks table."""
    op.drop_index('ix_tasks_created_at', table_name='tasks')
    op.drop_index('ix_tasks_assignee', table_name='tasks')
    op.drop_index('ix_tasks_priority', table_name='tasks')
    op.drop_index('ix_tasks_status', table_name='tasks')
    op.drop_table('tasks')
