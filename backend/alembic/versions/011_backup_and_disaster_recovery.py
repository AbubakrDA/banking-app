"""011_backup_and_disaster_recovery

Revision ID: 011_backup_and_disaster_recovery
Revises: 010_enterprise_admin
Create Date: 2026-11-24 23:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '011_backup_and_disaster_recovery'
down_revision: Union[str, None] = '010_enterprise_admin'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Backup Records
    op.create_table(
        'backup_records',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=True),
        sa.Column('backup_type', sa.String(length=32), server_default='FULL', nullable=False),
        sa.Column('target_type', sa.String(length=32), server_default='POSTGRESQL', nullable=False),
        sa.Column('status', sa.String(length=32), server_default='COMPLETED', nullable=False),
        sa.Column('storage_path', sa.String(length=512), nullable=False),
        sa.Column('size_bytes', sa.BigInteger(), server_default='0', nullable=False),
        sa.Column('sha256_checksum', sa.String(length=64), nullable=False),
        sa.Column('is_encrypted', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('encryption_algorithm', sa.String(length=32), server_default='AES-256-GCM', nullable=False),
        sa.Column('retention_tier', sa.String(length=32), server_default='DAILY', nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('meta_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    )
    op.create_index('ix_backup_records_tenant_id', 'backup_records', ['tenant_id'])
    op.create_index('ix_backup_records_status', 'backup_records', ['status'])

    # 2. Restore Drills
    op.create_table(
        'restore_drills',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('backup_id', sa.String(length=36), sa.ForeignKey('backup_records.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=True),
        sa.Column('status', sa.String(length=32), server_default='SUCCESS', nullable=False),
        sa.Column('rto_seconds', sa.Integer(), server_default='0', nullable=False),
        sa.Column('rpo_minutes', sa.Integer(), server_default='0', nullable=False),
        sa.Column('tables_validated', sa.Integer(), server_default='0', nullable=False),
        sa.Column('records_validated', sa.Integer(), server_default='0', nullable=False),
        sa.Column('checksum_verified', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('drill_notes', sa.Text(), nullable=True),
        sa.Column('executed_by', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    )
    op.create_index('ix_restore_drills_backup_id', 'restore_drills', ['backup_id'])
    op.create_index('ix_restore_drills_tenant_id', 'restore_drills', ['tenant_id'])

    # 3. Backup Retention Policies
    op.create_table(
        'backup_retention_policies',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=True),
        sa.Column('daily_retention_days', sa.Integer(), server_default='7', nullable=False),
        sa.Column('weekly_retention_weeks', sa.Integer(), server_default='4', nullable=False),
        sa.Column('monthly_retention_months', sa.Integer(), server_default='12', nullable=False),
        sa.Column('auto_drills_enabled', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('drill_frequency_days', sa.Integer(), server_default='7', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    )
    op.create_index('ix_backup_retention_policies_tenant_id', 'backup_retention_policies', ['tenant_id'])


def downgrade() -> None:
    op.drop_table('backup_retention_policies')
    op.drop_table('restore_drills')
    op.drop_table('backup_records')
