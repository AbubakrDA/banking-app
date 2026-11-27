from typing import Callable, Union, Sequence, Optional
from fastapi import Depends, Header, HTTPException, status, Request, Query
from app.core.database import tenant_context_var
from app.core.security import verify_access_token

# Single source of truth for banking RBAC roles (default deny for anything else)
BANKING_ROLES = frozenset({"customer", "employee", "risk_officer", "admin"})
STAFF_ROLES = frozenset({"employee", "risk_officer", "admin"})


class AuthenticatedUser:
    def __init__(self, user_id: str, email: str, role: str, tenant_id: str):
        self.id = user_id
        self.user_id = user_id
        self.email = email
        self.role = role
        self.tenant_id = tenant_id


async def get_current_user(
    request: Request,
    authorization: str | None = Header(default=None),
) -> AuthenticatedUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Bearer authorization token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ", 1)[1].strip()
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, signature-tampered, or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = payload.get("role", "")
    if role not in BANKING_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Unknown or unauthorized role '{role}'",
        )

    user = AuthenticatedUser(
        user_id=payload.get("sub", ""),
        email=payload.get("email", ""),
        role=role,
        tenant_id=payload.get("tenant_id", ""),
    )

    # Attach to request state and DB RLS ContextVar from verified JWT only
    request.state.current_user = user
    request.state.tenant_id = user.tenant_id
    tenant_context_var.set(user.tenant_id)

    return user


def require_roles(*allowed_roles: Union[str, Sequence[str]]) -> Callable[..., AuthenticatedUser]:
    flat_roles: set[str] = set()
    for item in allowed_roles:
        if isinstance(item, str):
            flat_roles.add(item)
        else:
            flat_roles.update(item)

    def role_checker(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.role not in flat_roles or current_user.role not in BANKING_ROLES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: User role '{current_user.role}' lacks required permissions ({', '.join(sorted(flat_roles))})",
            )
        return current_user

    return role_checker


def get_staff_access_reason(
    x_access_reason: Optional[str] = Header(default=None, alias="X-Access-Reason"),
    reason: Optional[str] = Query(default=None),
) -> Optional[str]:
    """Extracts written access reason from X-Access-Reason header or ?reason= query param."""
    val = (x_access_reason or reason or "").strip()
    return val or None
