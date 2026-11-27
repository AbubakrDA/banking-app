"""005_customer_memory

Revision ID: 005_memory
Revises: 004_kb_rag
Create Date: 2026-11-24 12:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '005_memory'
down_revision: Union[str, None] = '004_kb_rag'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'customer_memories',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_id', sa.String(length=36), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('conversation_id', sa.String(length=36), sa.ForeignKey('conversations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('memory_type', sa.String(length=32), nullable=False),
        sa.Column('key', sa.String(length=128), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('provenance', sa.JSON(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_flagged', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('flag_reason', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_customer_memories_tenant_id', 'customer_memories', ['tenant_id'])
    op.create_index('ix_customer_memories_customer_id', 'customer_memories', ['customer_id'])
    op.create_index('ix_customer_memories_key', 'customer_memories', ['key'])
    op.create_index('ix_customer_memories_memory_type', 'customer_memories', ['memory_type'])


def downgrade() -> None:
    op.drop_table('customer_memories')
