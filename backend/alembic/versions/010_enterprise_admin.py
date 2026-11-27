"""010_enterprise_admin

Revision ID: 010_enterprise_admin
Revises: 009_tools_mcp
Create Date: 2026-11-24 22:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '010_enterprise_admin'
down_revision: Union[str, None] = '009_tools_mcp'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tenant Brandings
    op.create_table(
        'tenant_brandings',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('logo_url', sa.String(length=512), nullable=True),
        sa.Column('primary_color', sa.String(length=32), server_default='#0B192C', nullable=False),
        sa.Column('accent_color', sa.String(length=32), server_default='#1E3E62', nullable=False),
        sa.Column('font_family', sa.String(length=64), server_default='Inter, sans-serif', nullable=False),
        sa.Column('email_footer_text', sa.Text(), nullable=True),
        sa.Column('custom_css_vars', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_tenant_brandings_tenant_id', 'tenant_brandings', ['tenant_id'])

    # 2. Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('actor_id', sa.String(length=64), nullable=False),
        sa.Column('actor_email', sa.String(length=255), nullable=False),
        sa.Column('actor_role', sa.String(length=32), server_default='agent', nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('target_resource', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('user_agent', sa.String(length=512), nullable=True),
        sa.Column('status', sa.String(length=32), server_default='SUCCESS', nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('event_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_audit_logs_tenant_id', 'audit_logs', ['tenant_id'])
    op.create_index('ix_audit_logs_actor_id', 'audit_logs', ['actor_id'])
    op.create_index('ix_audit_logs_event_type', 'audit_logs', ['event_type'])

    # 3. Tenant Security Policies
    op.create_table(
        'tenant_security_policies',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('mfa_enforced', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('session_timeout_minutes', sa.Integer(), server_default='60', nullable=False),
        sa.Column('password_rotation_days', sa.Integer(), server_default='90', nullable=False),
        sa.Column('data_retention_days', sa.Integer(), server_default='365', nullable=False),
        sa.Column('allowed_ip_ranges', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_security_policies_tenant_id', 'tenant_security_policies', ['tenant_id'])

    # 4. Model Routing Configs
    op.create_table(
        'model_routing_configs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('default_model', sa.String(length=64), server_default='gemini-2.5-flash', nullable=False),
        sa.Column('fallback_model', sa.String(length=64), server_default='gemini-2.5-pro', nullable=False),
        sa.Column('temperature', sa.Float(), server_default='0.2', nullable=False),
        sa.Column('max_tokens', sa.Integer(), server_default='2048', nullable=False),
        sa.Column('system_instructions_override', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_model_routing_tenant_id', 'model_routing_configs', ['tenant_id'])


def downgrade() -> None:
    op.drop_table('model_routing_configs')
    op.drop_table('tenant_security_policies')
    op.drop_table('audit_logs')
    op.drop_table('tenant_brandings')
