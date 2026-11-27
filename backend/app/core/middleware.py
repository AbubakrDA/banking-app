import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.core.database import tenant_context_var


class TenantAndLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        # 1. Attach unique Request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        # 2. Unauthenticated fallback context for public routes (/health, /tenants/current).
        # Database RLS tenant_context_var remains None until populated by verified JWT in get_current_user.
        fallback_tenant = request.headers.get(settings.TENANT_HEADER_NAME, settings.DEFAULT_TENANT_ID)
        request.state.tenant_id = fallback_tenant
        token = tenant_context_var.set(None)

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            tenant_context_var.reset(token)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # 3. Attach response headers (reflects verified JWT tenant on authenticated routes)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = str(duration_ms)
        response.headers["X-Tenant-Context"] = str(getattr(request.state, "tenant_id", fallback_tenant))
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")

        return response
