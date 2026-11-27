from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import TenantAndLoggingMiddleware
from app.schemas.envelope import APIResponse
from app.api.v1.api import api_router
from app.services.banking.service import (
    AccessDeniedError,
    ResourceNotFoundError,
    ValidationRuleError,
    ConflictRuleError,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    yield


def create_application() -> FastAPI:
    is_prod = settings.ENVIRONMENT == "production"
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="BankingAIPlatform Enterprise AI Customer Support & Business Intelligence Platform",
        openapi_url=None if is_prod else f"{settings.API_V1_STR}/openapi.json",
        docs_url=None if is_prod else f"{settings.API_V1_STR}/docs",
        redoc_url=None if is_prod else f"{settings.API_V1_STR}/redoc",
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    # 1. Custom Tenant & Correlation Logging Middleware
    app.add_middleware(TenantAndLoggingMiddleware)

    # 2. CORS Middleware
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # 3. Include API Router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # 4. Standard Exception Handlers with Typed Envelope
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        error_resp = APIResponse.fail(
            code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
            request_id=getattr(request.state, "request_id", None),
            tenant_id=getattr(request.state, "tenant_id", None),
        )
        return JSONResponse(status_code=exc.status_code, content=error_resp.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        safe_errors = [
            {"loc": list(e.get("loc", [])), "msg": str(e.get("msg", "")), "type": e.get("type", "")}
            for e in exc.errors()
        ]
        error_resp = APIResponse.fail(
            code="VALIDATION_ERROR",
            message="Request body or query parameter validation failed",
            details={"errors": safe_errors},
            request_id=getattr(request.state, "request_id", None),
            tenant_id=getattr(request.state, "tenant_id", None),
        )
        return JSONResponse(status_code=422, content=error_resp.model_dump())

    @app.exception_handler(AccessDeniedError)
    async def access_denied_handler(request: Request, exc: AccessDeniedError) -> JSONResponse:
        error_resp = APIResponse.fail(
            code="FORBIDDEN",
            message=str(exc),
            request_id=getattr(request.state, "request_id", None),
            tenant_id=getattr(request.state, "tenant_id", None),
        )
        return JSONResponse(status_code=403, content=error_resp.model_dump())

    @app.exception_handler(ResourceNotFoundError)
    async def not_found_handler(request: Request, exc: ResourceNotFoundError) -> JSONResponse:
        error_resp = APIResponse.fail(
            code="NOT_FOUND",
            message=str(exc),
            request_id=getattr(request.state, "request_id", None),
            tenant_id=getattr(request.state, "tenant_id", None),
        )
        return JSONResponse(status_code=404, content=error_resp.model_dump())

    @app.exception_handler(ValidationRuleError)
    async def validation_rule_handler(request: Request, exc: ValidationRuleError) -> JSONResponse:
        error_resp = APIResponse.fail(
            code="BAD_REQUEST",
            message=str(exc),
            request_id=getattr(request.state, "request_id", None),
            tenant_id=getattr(request.state, "tenant_id", None),
        )
        return JSONResponse(status_code=400, content=error_resp.model_dump())

    @app.exception_handler(ConflictRuleError)
    async def conflict_rule_handler(request: Request, exc: ConflictRuleError) -> JSONResponse:
        error_resp = APIResponse.fail(
            code="CONFLICT",
            message=str(exc),
            request_id=getattr(request.state, "request_id", None),
            tenant_id=getattr(request.state, "tenant_id", None),
        )
        return JSONResponse(status_code=409, content=error_resp.model_dump())

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        msg = str(exc)
        lowered = msg.lower()
        if "not found" in lowered:
            status_code, code = 404, "NOT_FOUND"
        elif any(k in lowered for k in ("forbidden", "denied", "unauthorized", "cannot approve", "cannot reject")):
            status_code, code = 403, "FORBIDDEN"
        elif any(k in lowered for k in ("already exists", "duplicate", "conflict", "not pending")):
            status_code, code = 409, "CONFLICT"
        else:
            status_code, code = 400, "BAD_REQUEST"

        error_resp = APIResponse.fail(
            code=code,
            message=msg,
            request_id=getattr(request.state, "request_id", None),
            tenant_id=getattr(request.state, "tenant_id", None),
        )
        return JSONResponse(status_code=status_code, content=error_resp.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        error_resp = APIResponse.fail(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected internal error occurred.",
            request_id=getattr(request.state, "request_id", None),
            tenant_id=getattr(request.state, "tenant_id", None),
        )
        return JSONResponse(status_code=500, content=error_resp.model_dump())

    return app


app = create_application()
