import pytest
from fastapi import APIRouter
from httpx import AsyncClient, ASGITransport
from app.main import create_application
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_standard_api_error_envelopes(client: AsyncClient) -> None:
    """Verify 404 and 422 responses use the standard APIResponse error envelope."""
    token = create_access_token("u_err", "tenant_err", "agent", "err@test.com")
    headers = {"Authorization": f"Bearer {token}"}

    res_404 = await client.get("/api/v1/nonexistent-endpoint-xyz", headers=headers)
    assert res_404.status_code == 404
    body_404 = res_404.json()
    assert body_404["success"] is False
    assert body_404["error"]["code"] == "HTTP_404"
    assert body_404["meta"]["request_id"] is not None

    res_422 = await client.post("/api/v1/auth/login", json={"email": "not-an-email"})
    assert res_422.status_code == 422
    body_422 = res_422.json()
    assert body_422["success"] is False
    assert body_422["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(body_422["error"]["details"]["errors"], list)


@pytest.mark.asyncio
async def test_value_error_specific_4xx_and_sanitized_500() -> None:
    """Verify ValueError maps to specific 4xx codes and unhandled 500 hides internals."""
    app = create_application()
    test_router = APIRouter()

    @test_router.get("/__test_val_404")
    async def _val_404() -> None:
        raise ValueError("Resource not found")

    @test_router.get("/__test_val_403")
    async def _val_403() -> None:
        raise ValueError("Action forbidden for this actor")

    @test_router.get("/__test_val_409")
    async def _val_409() -> None:
        raise ValueError("Record already exists")

    @test_router.get("/__test_val_400")
    async def _val_400() -> None:
        raise ValueError("Invalid domain parameter")

    @test_router.get("/__test_unhandled_500")
    async def _raise_500() -> None:
        raise RuntimeError("sensitive internal connection string")

    app.include_router(test_router)
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        for path, exp_status, exp_code in (
            ("/__test_val_404", 404, "NOT_FOUND"),
            ("/__test_val_403", 403, "FORBIDDEN"),
            ("/__test_val_409", 409, "CONFLICT"),
            ("/__test_val_400", 400, "BAD_REQUEST"),
        ):
            r = await ac.get(path)
            assert r.status_code == exp_status
            b = r.json()
            assert b["success"] is False
            assert b["error"]["code"] == exp_code

        r_500 = await ac.get("/__test_unhandled_500")
        assert r_500.status_code == 500
        b_500 = r_500.json()
        assert b_500["success"] is False
        assert b_500["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert "sensitive internal connection string" not in r_500.text
