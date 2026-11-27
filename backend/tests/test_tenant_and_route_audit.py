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
    from fastapi.routing import _IncludedRouter
    from app.main import app

    public_allowlist = {
        "/api/v1/health",
        "/api/v1/auth/login",
    }

    def iter_api_routes(routes, prefix=""):
        for rt in routes:
            if isinstance(rt, APIRoute):
                yield prefix + rt.path, rt
            elif isinstance(rt, _IncludedRouter):
                p = prefix + (rt.include_context.prefix or "")
                yield from iter_api_routes(rt.original_router.routes, p)

    def collect_surface_and_roles(dep):
        s = getattr(dep.call, "__surface__", None)
        r = getattr(dep.call, "__roles__", None)
        for sub in dep.dependencies:
            ss, rr = collect_surface_and_roles(sub)
            s = s or ss
            r = r or rr
        return s, r

    inspected = 0
    missing = []
    for path, route in iter_api_routes(app.routes):
        if not path.startswith("/api/v1"):
            continue
        inspected += 1
        if path in public_allowlist:
            continue

        surface, roles = collect_surface_and_roles(route.dependant)
        if not surface or not roles:
            missing.append(
                f"{','.join(sorted(route.methods or []))} {path} (surface={surface}, roles={roles})"
            )

    assert inspected >= 30
    assert missing == [], f"Routes missing declared surface or roles: {missing}"
