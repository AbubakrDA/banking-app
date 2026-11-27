"""012_tool_requester_tracking

Revision ID: 012_tool_requester_tracking
Revises: 011_backup_and_disaster_recovery
Create Date: 2026-11-25 13:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '012_tool_requester_tracking'
down_revision: Union[str, None] = '011_backup_and_disaster_recovery'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tool_executions', sa.Column('requested_by_user_id', sa.String(length=64), nullable=True))
    op.add_column('tool_executions', sa.Column('requested_by_role', sa.String(length=32), nullable=True))
    op.create_index('ix_tool_executions_requested_by_user_id', 'tool_executions', ['requested_by_user_id'])


def downgrade() -> None:
    op.drop_index('ix_tool_executions_requested_by_user_id', table_name='tool_executions')
    op.drop_column('tool_executions', 'requested_by_role')
    op.drop_column('tool_executions', 'requested_by_user_id')
