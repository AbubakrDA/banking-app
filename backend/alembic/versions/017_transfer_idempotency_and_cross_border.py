"""Add idempotency_key and is_cross_border to bank_transfers

Revision ID: 017_transfer_idempotency_and_cross_border
Revises: 016_banking_domain_tables
Create Date: 2026-11-27
"""
from alembic import op
import sqlalchemy as sa

revision = "017_transfer_idempotency_and_cross_border"
down_revision = "016_banking_domain_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("bank_transfers", sa.Column("idempotency_key", sa.String(128), nullable=True))
    op.add_column(
        "bank_transfers",
        sa.Column("is_cross_border", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index("ix_bank_transfers_idempotency_key", "bank_transfers", ["idempotency_key"])


def downgrade() -> None:
    op.drop_index("ix_bank_transfers_idempotency_key", table_name="bank_transfers")
    op.drop_column("bank_transfers", "is_cross_border")
    op.drop_column("bank_transfers", "idempotency_key")
