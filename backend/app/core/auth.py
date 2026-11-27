from typing import Callable, Union, Sequence
from fastapi import Depends, Header, HTTPException, status, Request
from app.core.database import tenant_context_var
from app.core.security import verify_access_token


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

    user = AuthenticatedUser(
        user_id=payload.get("sub", ""),
        email=payload.get("email", ""),
        role=payload.get("role", "agent"),
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
        if current_user.role not in flat_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: User role '{current_user.role}' lacks required permissions ({', '.join(sorted(flat_roles))})",
            )
        return current_user

    return role_checker
