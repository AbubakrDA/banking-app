"""008_admin_intelligence

Revision ID: 008_admin_intel
Revises: 007_nlp_qi
Create Date: 2026-11-24 18:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '008_admin_intel'
down_revision: Union[str, None] = '007_nlp_qi'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. AI Insights Table
    op.create_table(
        'ai_insights',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('domain', sa.String(length=64), server_default='operations', nullable=False),
        sa.Column('evidence_tier', sa.String(length=32), server_default='PROBABLE', nullable=False),
        sa.Column('confidence_score', sa.Float(), server_default='0.85', nullable=False),
        sa.Column('supporting_metrics', sa.JSON(), nullable=True),
        sa.Column('actionable_recommendation', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(length=32), server_default='MEDIUM', nullable=False),
        sa.Column('is_acknowledged', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('acknowledged_by', sa.String(length=64), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_ai_insights_tenant_id', 'ai_insights', ['tenant_id'])
    op.create_index('ix_ai_insights_evidence_tier', 'ai_insights', ['evidence_tier'])
    op.create_index('ix_ai_insights_acknowledged', 'ai_insights', ['is_acknowledged'])

    # 2. Organizational Memory Table
    op.create_table(
        'organizational_memory',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.String(length=64), server_default='operations', nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('key_findings', sa.JSON(), nullable=True),
        sa.Column('playbook_steps', sa.JSON(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=32), server_default='active', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_org_memory_tenant_id', 'organizational_memory', ['tenant_id'])
    op.create_index('ix_org_memory_title', 'organizational_memory', ['title'])
    op.create_index('ix_org_memory_category', 'organizational_memory', ['category'])

    # 3. Executive Reports Table
    op.create_table(
        'executive_reports',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('period_type', sa.String(length=32), server_default='weekly', nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('kpis', sa.JSON(), nullable=False),
        sa.Column('insights_summary', sa.JSON(), nullable=True),
        sa.Column('top_issues', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('generated_by', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_executive_reports_tenant_id', 'executive_reports', ['tenant_id'])
    op.create_index('ix_executive_reports_period', 'executive_reports', ['period_type'])


def downgrade() -> None:
    op.drop_table('executive_reports')
    op.drop_table('organizational_memory')
    op.drop_table('ai_insights')
