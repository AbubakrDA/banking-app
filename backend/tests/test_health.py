import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["service"] == "BankingAIPlatform Backend Core"
    assert data["data"]["status"] in ("healthy", "degraded")
    assert "components" in data["data"]
    assert "meta" in data
    assert data["meta"]["version"] == "v1"

    # Verify Response Headers
    assert "x-request-id" in response.headers
    assert "x-response-time-ms" in response.headers
    assert "x-tenant-context" in response.headers


@pytest.mark.asyncio
async def test_tenant_context_endpoint(client: AsyncClient) -> None:
    from app.core.security import create_access_token
    from app.core.database import get_db
    from app.main import app
    from app.models.tenant import Tenant

    # Unauthenticated request with X-Tenant-ID header must be rejected (401)
    r_unauth = await client.get(
        "/api/v1/tenants/current",
        headers={"X-Tenant-ID": "tenant_spoofed_99"},
    )
    assert r_unauth.status_code == 401

    async for db in app.dependency_overrides[get_db]():
        db.add(
            Tenant(
                id="tenant_health_01",
                name="Health Check Bank",
                slug="health-check-bank",
                business_mode="hybrid",
            )
        )
        await db.commit()
        break

    token = create_access_token("admin_h1", "tenant_health_01", "admin", "admin@h.local")
    response = await client.get(
        "/api/v1/tenants/current",
        headers={"Authorization": f"Bearer {token}", "X-Tenant-ID": "tenant_spoofed_99"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["tenant_id"] == "tenant_health_01"
    assert data["data"]["name"] == "Health Check Bank"
    assert response.headers["x-tenant-context"] == "tenant_health_01"


@pytest.mark.asyncio
async def test_404_error_envelope(client: AsyncClient) -> None:
    response = await client.get("/api/v1/nonexistent-route")
    assert response.status_code == 404

    data = response.json()
    assert data["success"] is False
    assert data["data"] is None
    assert data["error"]["code"] == "HTTP_404"
    assert "Not Found" in data["error"]["message"]
