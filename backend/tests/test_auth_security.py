import pytest
from datetime import timedelta
from httpx import AsyncClient
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "alex@banking-ai-platform.internal",
            "password": "validpassword123",
            "tenant_id": "tenant_enterprise_01",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["tenant_id"] == "tenant_enterprise_01"
    assert data["data"]["role"] == "admin"


@pytest.mark.asyncio
async def test_unauthenticated_request_rejected(client: AsyncClient) -> None:
    # Attempting to access /api/v1/auth/me without Bearer token must return 401
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "HTTP_401"
    assert "Missing or malformed" in data["error"]["message"]


@pytest.mark.asyncio
async def test_tampered_token_rejected(client: AsyncClient) -> None:
    valid_token = create_access_token(
        subject="user_123",
        tenant_id="tenant_01",
        role="employee",
        email="employee@test.com",
    )
    # Tamper with the payload signature
    tampered_token = valid_token[:-4] + "XXXX"

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tampered_token}"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert "Invalid, signature-tampered" in data["error"]["message"]


@pytest.mark.asyncio
async def test_expired_token_rejected(client: AsyncClient) -> None:
    expired_token = create_access_token(
        subject="user_123",
        tenant_id="tenant_01",
        role="employee",
        email="employee@test.com",
        expires_delta=timedelta(seconds=-10),  # Expired in past
    )
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_rbac_admin_vs_agent_permissions(client: AsyncClient) -> None:
    # 1. Employee token attempting admin action
    agent_token = create_access_token(
        subject="emp_001",
        tenant_id="tenant_alpha",
        role="employee",
        email="emp@alpha.com",
    )
    response = await client.post(
        "/api/v1/auth/users",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={
            "email": "newbie@alpha.com",
            "password": "securepassword123",
            "full_name": "New Staff Member",
            "role": "employee",
        },
    )
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert "lacks required permissions" in data["error"]["message"]

    # 2. Admin token attempting same action
    admin_token = create_access_token(
        subject="admin_001",
        tenant_id="tenant_alpha",
        role="admin",
        email="admin@alpha.com",
    )
    response_admin = await client.post(
        "/api/v1/auth/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "newbie@alpha.com",
            "password": "securepassword123",
            "full_name": "New Staff Member",
            "role": "employee",
        },
    )
    assert response_admin.status_code == 200
    assert response_admin.json()["success"] is True
    assert response_admin.json()["data"]["email"] == "newbie@alpha.com"


@pytest.mark.asyncio
async def test_strict_multi_tenant_isolation(client: AsyncClient) -> None:
    admin_alpha = create_access_token(
        subject="admin_alpha",
        tenant_id="tenant_company_a",
        role="admin",
        email="admin@company-a.com",
    )
    admin_beta = create_access_token(
        subject="admin_beta",
        tenant_id="tenant_company_b",
        role="admin",
        email="admin@company-b.com",
    )

    # 1. Company A admin creates a user in Company A
    await client.post(
        "/api/v1/auth/users",
        headers={"Authorization": f"Bearer {admin_alpha}"},
        json={
            "email": "secret_agent@company-a.com",
            "password": "password12345",
            "full_name": "Company A Staff",
            "role": "employee",
        },
    )

    # 2. Company B queries /users with their token
    res_b = await client.get(
        "/api/v1/auth/users",
        headers={"Authorization": f"Bearer {admin_beta}"},
    )
    assert res_b.status_code == 200
    users_in_b = res_b.json()["data"]

    # CRITICAL INVARIANT: Zero Company A users visible to Company B
    emails_in_b = [u["email"] for u in users_in_b]
    assert "secret_agent@company-a.com" not in emails_in_b

    # 3. Company A queries /users with their token
    res_a = await client.get(
        "/api/v1/auth/users",
        headers={"Authorization": f"Bearer {admin_alpha}"},
    )
    assert res_a.status_code == 200
    users_in_a = res_a.json()["data"]
    emails_in_a = [u["email"] for u in users_in_a]
    assert "secret_agent@company-a.com" in emails_in_a


def _craft_raw_jwt(header: dict, payload: dict, sign: bool = True) -> str:
    import json
    import hmac
    import hashlib
    from app.core.security import _base64url_encode
    from app.core.config import settings

    h = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    p = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    if not sign:
        return f"{h}.{p}."
    sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), f"{h}.{p}".encode("utf-8"), hashlib.sha256).digest()
    return f"{h}.{p}.{_base64url_encode(sig)}"


def test_jwt_validation_edge_cases() -> None:
    """Verify alg:none, wrong alg, unsigned, wrong iss, wrong aud, and prod static-secret rejection."""
    import time
    from app.core.security import verify_access_token
    from app.core.config import Settings, settings

    now = int(time.time())
    base_payload = {
        "sub": "u1",
        "tenant_id": "t1",
        "role": "employee",
        "email": "u1@test.com",
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": now,
        "exp": now + 300,
    }

    # 1. Valid token
    valid = create_access_token("u1", "t1", "employee", "u1@test.com")
    assert verify_access_token(valid) is not None

    # 2. alg: none (signed and unsigned)
    assert verify_access_token(_craft_raw_jwt({"alg": "none", "typ": "JWT"}, base_payload, sign=False)) is None
    assert verify_access_token(_craft_raw_jwt({"alg": "none", "typ": "JWT"}, base_payload, sign=True)) is None

    # 3. Wrong algorithm (e.g. HS512 / RS256)
    assert verify_access_token(_craft_raw_jwt({"alg": "HS512", "typ": "JWT"}, base_payload, sign=True)) is None
    assert verify_access_token(_craft_raw_jwt({"alg": "RS256", "typ": "JWT"}, base_payload, sign=True)) is None

    # 4. Unsigned HS256 token
    assert verify_access_token(_craft_raw_jwt({"alg": "HS256", "typ": "JWT"}, base_payload, sign=False)) is None

    # 5. Wrong issuer
    assert verify_access_token(_craft_raw_jwt({"alg": "HS256", "typ": "JWT"}, {**base_payload, "iss": "evil"}, sign=True)) is None

    # 6. Wrong audience
    assert verify_access_token(_craft_raw_jwt({"alg": "HS256", "typ": "JWT"}, {**base_payload, "aud": "wrong"}, sign=True)) is None

    # 7. Production rejects static JWT secret flag or missing Keycloak JWKS URL
    with pytest.raises(ValueError, match="ALLOW_DEV_STATIC_JWT_SECRET"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="x" * 32,
            ALLOW_DEV_STATIC_JWT_SECRET=True,
            KEYCLOAK_JWKS_URL="https://keycloak.example.com/certs",
        )
    with pytest.raises(ValueError, match="KEYCLOAK_JWKS_URL"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="x" * 32,
            ALLOW_DEV_STATIC_JWT_SECRET=False,
            KEYCLOAK_JWKS_URL=None,
        )
