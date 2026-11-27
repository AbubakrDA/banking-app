"""013_enable_postgresql_rls

Revision ID: 013_enable_postgresql_rls
Revises: 012_tool_requester_tracking
Create Date: 2026-11-25 13:15:00.000000

"""
from typing import Sequence, Union
from alembic import op

revision: str = '013_enable_postgresql_rls'
down_revision: Union[str, None] = '012_tool_requester_tracking'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

STRICT_TENANT_TABLES = [
    "ai_insights",
    "audit_logs",
    "business_appointments",
    "business_orders",
    "business_products",
    "business_services",
    "conversations",
    "customer_feedback",
    "customer_memories",
    "customers",
    "data_sources",
    "documents",
    "executive_reports",
    "kb_chunks",
    "kb_collections",
    "kb_documents",
    "logged_questions",
    "mcp_server_configs",
    "messages",
    "model_routing_configs",
    "organization_settings",
    "organizational_memory",
    "question_clusters",
    "sync_history",
    "tenant_brandings",
    "tenant_security_policies",
    "ticket_notes",
    "tickets",
    "tool_executions",
    "users",
]

NULLABLE_TENANT_TABLES = [
    "backup_records",
    "backup_retention_policies",
    "restore_drills",
]


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return

    for tbl in STRICT_TENANT_TABLES:
        op.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"ALTER TABLE {tbl} FORCE ROW LEVEL SECURITY;")
        op.execute(f"DROP POLICY IF EXISTS tenant_rls_policy ON {tbl};")
        op.execute(
            f"CREATE POLICY tenant_rls_policy ON {tbl} "
            f"USING (tenant_id = current_setting('app.tenant_id', true)) "
            f"WITH CHECK (tenant_id = current_setting('app.tenant_id', true));"
        )

    for tbl in NULLABLE_TENANT_TABLES:
        op.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"ALTER TABLE {tbl} FORCE ROW LEVEL SECURITY;")
        op.execute(f"DROP POLICY IF EXISTS tenant_rls_policy ON {tbl};")
        op.execute(
            f"CREATE POLICY tenant_rls_policy ON {tbl} "
            f"USING (tenant_id = current_setting('app.tenant_id', true) OR tenant_id IS NULL) "
            f"WITH CHECK (tenant_id = current_setting('app.tenant_id', true) OR tenant_id IS NULL);"
        )


def downgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return

    for tbl in STRICT_TENANT_TABLES + NULLABLE_TENANT_TABLES:
        op.execute(f"DROP POLICY IF EXISTS tenant_rls_policy ON {tbl};")
        op.execute(f"ALTER TABLE {tbl} NO FORCE ROW LEVEL SECURITY;")
        op.execute(f"ALTER TABLE {tbl} DISABLE ROW LEVEL SECURITY;")
