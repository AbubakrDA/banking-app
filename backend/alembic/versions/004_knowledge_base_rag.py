"""004_knowledge_base_rag

Revision ID: 004_kb_rag
Revises: 003_doc_intel
Create Date: 2026-11-24 11:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '004_kb_rag'
down_revision: Union[str, None] = '003_doc_intel'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Collections Table
    op.create_table(
        'kb_collections',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_kb_collections_tenant_id', 'kb_collections', ['tenant_id'])

    # 2. Documents Table
    op.create_table(
        'kb_documents',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('collection_id', sa.String(length=36), sa.ForeignKey('kb_collections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('source_type', sa.String(length=32), server_default='manual_entry', nullable=False),
        sa.Column('source_url', sa.String(length=512), nullable=True),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('status', sa.String(length=32), server_default='indexed', nullable=False),
        sa.Column('chunk_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('doc_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_kb_documents_tenant_id', 'kb_documents', ['tenant_id'])
    op.create_index('ix_kb_documents_collection_id', 'kb_documents', ['collection_id'])

    # 3. Chunks Table
    op.create_table(
        'kb_chunks',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_id', sa.String(length=36), sa.ForeignKey('kb_documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('collection_id', sa.String(length=36), sa.ForeignKey('kb_collections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.Column('token_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('chunk_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_kb_chunks_tenant_id', 'kb_chunks', ['tenant_id'])
    op.create_index('ix_kb_chunks_document_id', 'kb_chunks', ['document_id'])
    op.create_index('ix_kb_chunks_collection_id', 'kb_chunks', ['collection_id'])


def downgrade() -> None:
    op.drop_table('kb_chunks')
    op.drop_table('kb_documents')
    op.drop_table('kb_collections')
