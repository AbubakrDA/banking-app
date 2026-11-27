"""014_audit_log_hash_chain

Revision ID: 014_audit_log_hash_chain
Revises: 013_enable_postgresql_rls
Create Date: 2026-11-25 14:02:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '014_audit_log_hash_chain'
down_revision: Union[str, None] = '013_enable_postgresql_rls'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('audit_logs', sa.Column('prev_hash', sa.String(length=64), nullable=True))
    op.add_column('audit_logs', sa.Column('hash_timestamp', sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column('audit_logs', 'hash_timestamp')
    op.drop_column('audit_logs', 'prev_hash')
