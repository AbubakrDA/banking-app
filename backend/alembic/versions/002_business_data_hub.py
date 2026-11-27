"""002_business_data_hub

Revision ID: 002_business_hub
Revises: 001_initial
Create Date: 2026-11-24 07:44:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_business_hub'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Products Table
    op.create_table(
        'business_products',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sku', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('brand', sa.String(length=100), nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('discount_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('stock_quantity', sa.Integer(), server_default='0', nullable=False),
        sa.Column('supplier', sa.String(length=255), nullable=True),
        sa.Column('image_url', sa.String(length=512), nullable=True),
        sa.Column('specifications', sa.JSON(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    )
    op.create_index('ix_products_tenant_sku', 'business_products', ['tenant_id', 'sku'])

    # 2. Services Table
    op.create_table(
        'business_services',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), server_default='60', nullable=False),
        sa.Column('staff_members', sa.JSON(), nullable=True),
        sa.Column('service_policies', sa.Text(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    )
    op.create_index('ix_services_tenant_category', 'business_services', ['tenant_id', 'category'])

    # 3. Orders Table
    op.create_table(
        'business_orders',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_id', sa.String(length=36), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('order_number', sa.String(length=64), nullable=False),
        sa.Column('total_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('status', sa.String(length=32), server_default='pending', nullable=False),
        sa.Column('items', sa.JSON(), nullable=True),
        sa.Column('delivery_address', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    )
    op.create_index('ix_orders_tenant_number', 'business_orders', ['tenant_id', 'order_number'])

    # 4. Appointments Table
    op.create_table(
        'business_appointments',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_id', sa.String(length=36), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('service_id', sa.String(length=36), sa.ForeignKey('business_services.id', ondelete='CASCADE'), nullable=False),
        sa.Column('staff_name', sa.String(length=255), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(length=32), server_default='scheduled', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    )
    op.create_index('ix_appts_tenant_service', 'business_appointments', ['tenant_id', 'service_id'])

    # 5. Data Sources Table
    op.create_table(
        'data_sources',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_type', sa.String(length=32), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('sync_status', sa.String(length=32), server_default='idle', nullable=False),
        sa.Column('sync_frequency', sa.String(length=32), server_default='hourly', nullable=False),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    )
    op.create_index('ix_datasources_tenant', 'data_sources', ['tenant_id'])

    # 6. Sync History Table
    op.create_table(
        'sync_history',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('data_source_id', sa.String(length=36), sa.ForeignKey('data_sources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('records_processed', sa.Integer(), server_default='0', nullable=False),
        sa.Column('records_created', sa.Integer(), server_default='0', nullable=False),
        sa.Column('records_updated', sa.Integer(), server_default='0', nullable=False),
        sa.Column('records_failed', sa.Integer(), server_default='0', nullable=False),
        sa.Column('quality_score', sa.Integer(), server_default='100', nullable=False),
        sa.Column('quality_issues', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    )
    op.create_index('ix_synchistory_tenant_ds', 'sync_history', ['tenant_id', 'data_source_id'])


def downgrade() -> None:
    op.drop_table('sync_history')
    op.drop_table('data_sources')
    op.drop_table('business_appointments')
    op.drop_table('business_orders')
    op.drop_table('business_services')
    op.drop_table('business_products')
