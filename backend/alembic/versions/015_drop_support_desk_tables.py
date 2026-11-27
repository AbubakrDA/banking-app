"""015_drop_support_desk_tables

Revision ID: 015_drop_support_desk_tables
Revises: 014_audit_log_hash_chain
Create Date: 2026-11-27 15:28:30.000000

"""
from typing import Sequence, Union
from alembic import op

revision: str = '015_drop_support_desk_tables'
down_revision: Union[str, None] = '014_audit_log_hash_chain'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES_TO_DROP = [
    "customer_feedback",
    "ticket_notes",
    "tickets",
    "logged_questions",
    "question_clusters",
    "sync_history",
    "data_sources",
    "business_appointments",
    "business_orders",
    "business_services",
    "business_products",
    "mcp_server_configs",
]


def upgrade() -> None:
    for table in TABLES_TO_DROP:
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")


def downgrade() -> None:
    # Removed support-desk tables are intentionally not recreated in banking platform
    pass
