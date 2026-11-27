"""009_tools_and_mcp_gateway

Revision ID: 009_tools_mcp
Revises: 008_admin_intel
Create Date: 2026-11-24 20:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '009_tools_mcp'
down_revision: Union[str, None] = '008_admin_intel'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tool Executions Table
    op.create_table(
        'tool_executions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tool_name', sa.String(length=128), nullable=False),
        sa.Column('caller_agent', sa.String(length=64), server_default='customer_support_agent', nullable=False),
        sa.Column('caller_id', sa.String(length=64), nullable=False),
        sa.Column('risk_level', sa.String(length=32), server_default='LOW', nullable=False),
        sa.Column('status', sa.String(length=32), server_default='pending', nullable=False),
        sa.Column('input_parameters', sa.JSON(), nullable=False),
        sa.Column('raw_result', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('duration_ms', sa.Float(), server_default='0.0', nullable=False),
        sa.Column('approved_by', sa.String(length=64), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_tool_executions_tenant_id', 'tool_executions', ['tenant_id'])
    op.create_index('ix_tool_executions_tool_name', 'tool_executions', ['tool_name'])
    op.create_index('ix_tool_executions_caller_id', 'tool_executions', ['caller_id'])
    op.create_index('ix_tool_executions_status', 'tool_executions', ['status'])

    # 2. MCP Server Configs Table
    op.create_table(
        'mcp_server_configs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('transport_type', sa.String(length=32), server_default='http', nullable=False),
        sa.Column('endpoint_url', sa.String(length=512), nullable=False),
        sa.Column('auth_token', sa.String(length=512), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('discovered_tools', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_mcp_servers_tenant_id', 'mcp_server_configs', ['tenant_id'])


def downgrade() -> None:
    op.drop_table('mcp_server_configs')
    op.drop_table('tool_executions')
