"""003_document_intelligence

Revision ID: 003_doc_intel
Revises: 002_business_hub
Create Date: 2026-11-24 11:18:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_doc_intel'
down_revision: Union[str, None] = '002_business_hub'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'documents',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('conversation_id', sa.String(length=36), sa.ForeignKey('conversations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('customer_id', sa.String(length=36), sa.ForeignKey('customers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('mime_type', sa.String(length=128), nullable=False),
        sa.Column('storage_path', sa.String(length=512), nullable=False),
        sa.Column('file_hash', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), server_default='uploaded', nullable=False),
        sa.Column('is_quarantined', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('quarantine_reason', sa.String(length=255), nullable=True),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('doc_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_documents_tenant_id', 'documents', ['tenant_id'])
    op.create_index('ix_documents_file_hash', 'documents', ['file_hash'])
    op.create_index('ix_documents_conversation_id', 'documents', ['conversation_id'])


def downgrade() -> None:
    op.drop_table('documents')
