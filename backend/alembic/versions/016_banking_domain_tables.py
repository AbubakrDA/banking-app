"""016_banking_domain_tables

Revision ID: 016_banking_domain_tables
Revises: 015_drop_support_desk_tables
Create Date: 2026-11-27 15:31:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '016_banking_domain_tables'
down_revision: Union[str, None] = '015_drop_support_desk_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'bank_accounts',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), nullable=False, index=True),
        sa.Column('customer_id', sa.String(length=36), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('account_number_masked', sa.String(length=32), nullable=False),
        sa.Column('account_number_hash', sa.String(length=64), nullable=False),
        sa.Column('account_type', sa.String(length=32), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('balance_minor', sa.BigInteger(), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
    )
    op.create_table(
        'bank_transactions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), nullable=False, index=True),
        sa.Column('account_id', sa.String(length=36), sa.ForeignKey('bank_accounts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_id', sa.String(length=36), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tx_type', sa.String(length=32), nullable=False),
        sa.Column('amount_minor', sa.BigInteger(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('counterparty_masked', sa.String(length=64), nullable=True),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
    )
    op.create_table(
        'bank_transfers',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), nullable=False, index=True),
        sa.Column('from_account_id', sa.String(length=36), sa.ForeignKey('bank_accounts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('to_account_id', sa.String(length=36), sa.ForeignKey('bank_accounts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_id', sa.String(length=36), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('requested_by_user_id', sa.String(length=64), nullable=False),
        sa.Column('amount_minor', sa.BigInteger(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('reference', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('risk_score', sa.Integer(), nullable=False),
        sa.Column('approved_by_user_id', sa.String(length=64), nullable=True),
        sa.Column('rejection_reason', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
    )
    op.create_table(
        'bank_cards',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), nullable=False, index=True),
        sa.Column('account_id', sa.String(length=36), sa.ForeignKey('bank_accounts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_id', sa.String(length=36), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('card_last4', sa.String(length=4), nullable=False),
        sa.Column('card_type', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
    )
    op.create_table(
        'risk_alerts',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), nullable=False, index=True),
        sa.Column('customer_id', sa.String(length=36), nullable=False),
        sa.Column('account_id', sa.String(length=36), nullable=True),
        sa.Column('transfer_id', sa.String(length=36), nullable=True),
        sa.Column('severity', sa.String(length=16), nullable=False),
        sa.Column('risk_score', sa.Integer(), nullable=False),
        sa.Column('summary', sa.String(length=512), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
    )
    op.create_table(
        'policy_documents',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), nullable=False, index=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('storage_key', sa.String(length=512), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('uploaded_by_user_id', sa.String(length=64), nullable=False),
        sa.Column('reviewed_by_user_id', sa.String(length=64), nullable=True),
        sa.Column('review_reason', sa.String(length=255), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
    )
    op.create_table(
        'policy_chunks',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=64), nullable=False, index=True),
        sa.Column('policy_id', sa.String(length=36), sa.ForeignKey('policy_documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
    )


def downgrade() -> None:
    for tbl in (
        'policy_chunks',
        'policy_documents',
        'risk_alerts',
        'bank_cards',
        'bank_transfers',
        'bank_transactions',
        'bank_accounts',
    ):
        op.drop_table(tbl)
