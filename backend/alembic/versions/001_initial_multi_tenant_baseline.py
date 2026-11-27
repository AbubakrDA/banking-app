"""001_initial_multi_tenant_baseline

Revision ID: 001_initial
Revises: 
Create Date: 2026-11-24 07:37:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # 2. Tenants table
    op.create_table(
        'tenants',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('business_mode', sa.String(length=32), server_default='hybrid', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    )
    op.create_index('ix_tenants_slug', 'tenants', ['slug'], unique=True)

    # 3. Organization Settings
    op.create_table(
        'organization_settings',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('support_email', sa.String(length=255), nullable=True),
        sa.Column('support_phone', sa.String(length=64), nullable=True),
        sa.Column('primary_domain', sa.String(length=255), nullable=True),
        sa.Column('logo_url', sa.String(length=512), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    )
    op.create_index('ix_org_settings_tenant_id', 'organization_settings', ['tenant_id'])

    # 4. Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=32), server_default='agent', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    )
    op.create_index('ix_users_tenant_email', 'users', ['tenant_id', 'email'])

    # 5. Customers
    op.create_table(
        'customers',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('external_id', sa.String(length=128), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=64), nullable=True),
        sa.Column('tier', sa.String(length=32), server_default='standard', nullable=False),
        sa.Column('profile_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    )
    op.create_index('ix_customers_tenant_email', 'customers', ['tenant_id', 'email'])

    # 6. Conversations
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_id', sa.String(length=36), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assigned_user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('channel', sa.String(length=32), server_default='web', nullable=False),
        sa.Column('status', sa.String(length=32), server_default='active', nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    )
    op.create_index('ix_conversations_tenant_status', 'conversations', ['tenant_id', 'status'])

    # 7. Messages
    op.create_table(
        'messages',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('conversation_id', sa.String(length=36), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sender_type', sa.String(length=32), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sources', sa.JSON(), nullable=True),
        sa.Column('is_flagged', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    )
    op.create_index('ix_messages_tenant_conversation', 'messages', ['tenant_id', 'conversation_id'])


def downgrade() -> None:
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('customers')
    op.drop_table('users')
    op.drop_table('organization_settings')
    op.drop_table('tenants')
    op.execute("DROP EXTENSION IF EXISTS vector")
