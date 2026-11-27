from typing import Generic, TypeVar, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime, timezone

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error explanation")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Validation field errors or context")


class ResponseMeta(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    request_id: Optional[str] = None
    tenant_id: Optional[str] = None
    version: str = "v1"


class PaginationMeta(BaseModel):
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None
    meta: ResponseMeta = Field(default_factory=ResponseMeta)
    pagination: Optional[PaginationMeta] = None

    @classmethod
    def ok(
        cls,
        data: T,
        request_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        pagination: Optional[PaginationMeta] = None,
    ) -> "APIResponse[T]":
        return cls(
            success=True,
            data=data,
            meta=ResponseMeta(request_id=request_id, tenant_id=tenant_id),
            pagination=pagination,
        )

    @classmethod
    def fail(
        cls,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> "APIResponse[None]":
        return cls(
            success=False,
            data=None,
            error=ErrorDetail(code=code, message=message, details=details),
            meta=ResponseMeta(request_id=request_id, tenant_id=tenant_id),
        )
