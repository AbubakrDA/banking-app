"""007_question_intelligence

Revision ID: 007_nlp_qi
Revises: 006_tickets
Create Date: 2026-11-24 16:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '007_nlp_qi'
down_revision: Union[str, None] = '006_tickets'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Question Clusters Table
    op.create_table(
        'question_clusters',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('canonical_question', sa.String(length=255), nullable=False),
        sa.Column('intent', sa.String(length=64), server_default='general', nullable=False),
        sa.Column('category', sa.String(length=64), server_default='general', nullable=False),
        sa.Column('frequency', sa.Integer(), server_default='1', nullable=False),
        sa.Column('unique_customer_count', sa.Integer(), server_default='1', nullable=False),
        sa.Column('average_sentiment', sa.String(length=32), server_default='neutral', nullable=False),
        sa.Column('trend_direction', sa.String(length=32), server_default='stable', nullable=False),
        sa.Column('is_knowledge_gap', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('suggested_faq_answer', sa.Text(), nullable=True),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_question_clusters_tenant_id', 'question_clusters', ['tenant_id'])
    op.create_index('ix_question_clusters_canonical', 'question_clusters', ['canonical_question'])
    op.create_index('ix_question_clusters_knowledge_gap', 'question_clusters', ['is_knowledge_gap'])

    # 2. Logged Questions Table
    op.create_table(
        'logged_questions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cluster_id', sa.String(length=36), sa.ForeignKey('question_clusters.id', ondelete='SET NULL'), nullable=True),
        sa.Column('conversation_id', sa.String(length=36), sa.ForeignKey('conversations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('customer_id', sa.String(length=36), sa.ForeignKey('customers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=False),
        sa.Column('detected_language', sa.String(length=16), server_default='en', nullable=False),
        sa.Column('detected_intent', sa.String(length=64), server_default='general', nullable=False),
        sa.Column('sentiment', sa.String(length=32), server_default='neutral', nullable=False),
        sa.Column('was_rag_matched', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('rag_confidence_score', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_logged_questions_tenant_id', 'logged_questions', ['tenant_id'])
    op.create_index('ix_logged_questions_cluster_id', 'logged_questions', ['cluster_id'])


def downgrade() -> None:
    op.drop_table('logged_questions')
    op.drop_table('question_clusters')
