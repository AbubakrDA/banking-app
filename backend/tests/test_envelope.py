from app.schemas.envelope import APIResponse, PaginationMeta


def test_api_response_ok() -> None:
    resp = APIResponse.ok(
        data={"items": [1, 2, 3]},
        request_id="req-123",
        tenant_id="tenant-456",
        pagination=PaginationMeta(
            total_count=3,
            page=1,
            page_size=10,
            total_pages=1,
            has_next=False,
            has_prev=False,
        ),
    )
    assert resp.success is True
    assert resp.data == {"items": [1, 2, 3]}
    assert resp.error is None
    assert resp.meta.request_id == "req-123"
    assert resp.meta.tenant_id == "tenant-456"
    assert resp.pagination is not None
    assert resp.pagination.total_count == 3


def test_api_response_fail() -> None:
    resp = APIResponse.fail(
        code="UNAUTHORIZED",
        message="Invalid credentials provided",
        details={"field": "password"},
        request_id="req-999",
        tenant_id="tenant-888",
    )
    assert resp.success is False
    assert resp.data is None
    assert resp.error is not None
    assert resp.error.code == "UNAUTHORIZED"
    assert resp.error.message == "Invalid credentials provided"
    assert resp.error.details == {"field": "password"}
    assert resp.meta.request_id == "req-999"
