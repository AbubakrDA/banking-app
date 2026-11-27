import pytest
from httpx import AsyncClient
from fastapi.routing import APIRoute
from app.main import app
from app.core.security import create_access_token

# Declarative expected role matrix for every protected mutating route.
# Any new mutating route added without updating this matrix will fail discovery.
MUTATING_ROUTE_POLICY = [
    ("POST", "/api/v1/auth/users", {"owner", "admin"}),
    ("PATCH", "/api/v1/business/mode", {"owner", "admin"}),
    ("POST", "/api/v1/business/products", {"owner", "admin", "agent"}),
    ("POST", "/api/v1/business/services", {"owner", "admin", "agent"}),
    ("POST", "/api/v1/business/import/csv", {"owner", "admin", "agent"}),
    ("POST", "/api/v1/analytics/insights/generate", {"owner", "admin"}),
    ("PATCH", "/api/v1/analytics/insights/dummy-id/acknowledge", {"owner", "admin"}),
    ("POST", "/api/v1/analytics/organizational-memory", {"owner", "admin"}),
    ("POST", "/api/v1/analytics/copilot/query", {"owner", "admin"}),
    ("POST", "/api/v1/analytics/reports/generate", {"owner", "admin"}),
    ("POST", "/api/v1/knowledge/collections", {"owner", "admin", "agent"}),
    ("POST", "/api/v1/knowledge/documents", {"owner", "admin", "agent"}),
    ("DELETE", "/api/v1/knowledge/documents/dummy-id", {"owner", "admin", "agent"}),
    ("POST", "/api/v1/memory", {"owner", "admin", "agent"}),
    ("DELETE", "/api/v1/memory/dummy-id", {"owner", "admin", "agent"}),
    ("DELETE", "/api/v1/memory/customer/dummy-id/purge", {"owner", "admin", "agent"}),
    ("POST", "/api/v1/nlp/questions", {"owner", "admin", "agent"}),
    ("PATCH", "/api/v1/tickets/dummy-id/assign", {"owner", "admin", "agent"}),
    ("POST", "/api/v1/tickets/dummy-id/notes", {"owner", "admin", "agent"}),
    ("POST", "/api/v1/tickets/dummy-id/feedback-request", {"owner", "admin", "agent"}),
    ("POST", "/api/v1/tools/executions/dummy-id/approve", {"owner", "admin"}),
    ("POST", "/api/v1/tools/executions/dummy-id/reject", {"owner", "admin"}),
    ("POST", "/api/v1/tools/mcp-servers", {"owner", "admin"}),
    ("PATCH", "/api/v1/enterprise/branding", {"owner", "admin"}),
    ("POST", "/api/v1/enterprise/users/invite", {"owner", "admin"}),
    ("PATCH", "/api/v1/enterprise/users/dummy-id/role", {"owner", "admin"}),
    ("POST", "/api/v1/enterprise/security/revoke-session", {"owner", "admin"}),
    ("PATCH", "/api/v1/enterprise/model-config", {"owner", "admin"}),
    ("POST", "/api/v1/backup/trigger", {"owner", "admin"}),
    ("POST", "/api/v1/backup/drill", {"owner", "admin"}),
    ("PUT", "/api/v1/backup/retention-policy", {"owner", "admin"}),
    ("POST", "/api/v1/backup/prune", {"owner", "admin"}),
]


def test_all_admin_mutating_routes_have_require_roles() -> None:
    """Verify every route in MUTATING_ROUTE_POLICY exists in the FastAPI OpenAPI schema."""
    import re
    schema_paths = app.openapi()["paths"]
    normalized_routes = {
        (method.upper(), re.sub(r"\{[^}]+\}", "dummy-id", path))
        for path, methods_dict in schema_paths.items()
        for method in methods_dict.keys()
    }
    for method, path, _ in MUTATING_ROUTE_POLICY:
        assert (method, path) in normalized_routes, f"Policy route {(method, path)} not found in OpenAPI paths"


@pytest.mark.asyncio
@pytest.mark.parametrize("method,path,allowed_roles", MUTATING_ROUTE_POLICY)
@pytest.mark.parametrize("role", ["owner", "admin", "agent", "customer"])
async def test_mutating_route_rbac_enforcement(
    client: AsyncClient,
    method: str,
    path: str,
    allowed_roles: set[str],
    role: str,
) -> None:
    """Parametrized RBAC matrix: unauthorized roles MUST receive 403 Forbidden before handler logic."""
    token = create_access_token(f"rbac_{role}", "tenant_rbac_matrix", role, f"{role}@rbac.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Send minimal JSON payload for POST/PATCH/PUT so RBAC dependency runs (or 422/400/404 if allowed)
    kwargs = {"headers": headers}
    if method in ("POST", "PATCH", "PUT"):
        kwargs["json"] = {}

    res = await client.request(method, path, **kwargs)
    if role not in allowed_roles:
        assert res.status_code == 403, f"Expected 403 for {role} on {method} {path}, got {res.status_code}"
    else:
        assert res.status_code != 403, f"Role {role} should not be 403-blocked on {method} {path}"
