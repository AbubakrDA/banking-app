import pytest
from fastapi.routing import APIRoute
from httpx import AsyncClient

from app.core.security import create_access_token
from app.models.tenant import Tenant


def _auth(user_id: str, role: str, tenant_id: str) -> dict:
    token = create_access_token(
        subject=user_id,
        tenant_id=tenant_id,
        role=role,
        email=f"{user_id}@bank.local",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_tenants_current_requires_auth_and_loads_from_db(client: AsyncClient) -> None:
    from app.main import app
    from app.core.database import get_db

    # 1. Unauthenticated -> 401
    r_unauth = await client.get("/api/v1/tenants/current")
    assert r_unauth.status_code == 401

    # 2. Unauthorized roles (customer, hr, marketing) -> 403
    for role in ("customer", "hr", "marketing"):
        r_denied = await client.get(
            "/api/v1/tenants/current",
            headers=_auth(f"{role}_1", role, "tenant_real_01"),
        )
        assert r_denied.status_code == 403

    # 3. Seed real tenant in DB and verify response comes from DB, not hard-coded Acme Global Ltd
    async for db in app.dependency_overrides[get_db]():
        db.add(
            Tenant(
                id="tenant_real_01",
                name="Khartoum National Bank",
                slug="khartoum-national",
                business_mode="banking",
                status="active",
            )
        )
        await db.commit()
        break

    r_ok = await client.get(
        "/api/v1/tenants/current",
        headers=_auth("admin_1", "admin", "tenant_real_01"),
    )
    assert r_ok.status_code == 200
    data = r_ok.json()["data"]
    assert data["tenant_id"] == "tenant_real_01"
    assert data["name"] == "Khartoum National Bank"
    assert data["name"] != "Acme Global Ltd"


def test_every_api_route_declares_surface_and_roles() -> None:
    from app.main import app

    public_allowlist = {
        "/api/v1/health",
        "/api/v1/health/live",
        "/api/v1/health/ready",
        "/api/v1/auth/login",
    }

    missing = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        if not route.path.startswith("/api/v1"):
            continue
        if route.path in public_allowlist:
            continue

        surface = getattr(route.endpoint, "__surface__", None)
        roles = getattr(route.endpoint, "__roles__", None)
        if not surface or not roles:
            missing.append(f"{','.join(sorted(route.methods or []))} {route.path} (surface={surface}, roles={roles})")

    assert missing == [], f"Routes missing declared surface or roles: {missing}"
