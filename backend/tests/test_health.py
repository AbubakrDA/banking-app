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
    custom_tenant = "tenant_custom_acme_99"
    response = await client.get(
        "/api/v1/tenants/current",
        headers={"X-Tenant-ID": custom_tenant},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["data"]["tenant_id"] == custom_tenant
    assert data["data"]["business_mode"] == "hybrid"
    assert response.headers["x-tenant-context"] == custom_tenant


@pytest.mark.asyncio
async def test_404_error_envelope(client: AsyncClient) -> None:
    response = await client.get("/api/v1/nonexistent-route")
    assert response.status_code == 404

    data = response.json()
    assert data["success"] is False
    assert data["data"] is None
    assert data["error"]["code"] == "HTTP_404"
    assert "Not Found" in data["error"]["message"]
