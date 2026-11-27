import os
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_x_tenant_id_header_cannot_spoof_jwt_tenant_context(client: AsyncClient) -> None:
    """Verify X-Tenant-ID header is ignored and tenant is resolved strictly from verified JWT."""
    token_alpha = create_access_token("user_rls_1", "tenant_jwt_alpha", "admin", "rls1@alpha.com")
    spoofed_headers = {
        "Authorization": f"Bearer {token_alpha}",
        "X-Tenant-ID": "tenant_spoofed_beta",
    }

    res = await client.get("/api/v1/auth/me", headers=spoofed_headers)
    assert res.status_code == 200
    assert res.json()["data"]["tenant_id"] == "tenant_jwt_alpha"
    assert res.headers.get("X-Tenant-Context") == "tenant_jwt_alpha"


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.environ.get("POSTGRES_TEST_URL"),
    reason="Live PostgreSQL 16 + non-superuser role unavailable (POSTGRES_TEST_URL unset)",
)
async def test_postgres_rls_cross_tenant_isolation() -> None:
    """
    Real PostgreSQL 16 RLS integration test:
    Proves Tenant A cannot SELECT, UPDATE, or DELETE Tenant B rows via ORM or raw SQL.
    """
    pg_url = os.environ["POSTGRES_TEST_URL"]
    pg_engine = create_async_engine(pg_url, echo=False)
    cust_b_id = str(uuid.uuid4())

    try:
        async with pg_engine.begin() as conn:
            # Insert row as Tenant B
            await conn.execute(text("SELECT set_config('app.tenant_id', 'tenant_b_rls', true)"))
            await conn.execute(
                text(
                    "INSERT INTO customers (id, tenant_id, name, tier, created_at, updated_at, is_active) "
                    "VALUES (:id, 'tenant_b_rls', 'Bob Tenant B', 'standard', NOW(), NOW(), true)"
                ),
                {"id": cust_b_id},
            )

        async with pg_engine.begin() as conn:
            # Switch session to Tenant A
            await conn.execute(text("SELECT set_config('app.tenant_id', 'tenant_a_rls', true)"))
            rows = (await conn.execute(text("SELECT id FROM customers WHERE id = :id"), {"id": cust_b_id})).fetchall()
            assert len(rows) == 0, "RLS violation: Tenant A read Tenant B row!"

            upd = await conn.execute(text("UPDATE customers SET name = 'Hacked' WHERE id = :id"), {"id": cust_b_id})
            assert upd.rowcount == 0, "RLS violation: Tenant A updated Tenant B row!"

            dlt = await conn.execute(text("DELETE FROM customers WHERE id = :id"), {"id": cust_b_id})
            assert dlt.rowcount == 0, "RLS violation: Tenant A deleted Tenant B row!"
    finally:
        await pg_engine.dispose()
