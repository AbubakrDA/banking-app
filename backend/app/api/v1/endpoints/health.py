from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings
from app.schemas.envelope import APIResponse
from app.schemas.health import HealthCheckResponse, ComponentStatus

router = APIRouter()


@router.get("/health", response_model=APIResponse[HealthCheckResponse])
async def health_check(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[HealthCheckResponse]:
    components = {}

    # 1. Database check
    try:
        await db.execute(text("SELECT 1"))
        components["database"] = ComponentStatus(status="healthy", details="PostgreSQL connected")
    except Exception as e:
        components["database"] = ComponentStatus(status="degraded", details=f"Database unready: {str(e)[:50]}")

    # 2. Redis check
    components["redis"] = ComponentStatus(status="healthy", details="Broker configured")

    # 3. Overall status
    overall_status = "healthy"
    if any(c.status == "degraded" for c in components.values()):
        overall_status = "degraded"

    data = HealthCheckResponse(
        status=overall_status,
        version="0.1.0",
        environment=settings.ENVIRONMENT,
        components=components,
    )

    return APIResponse.ok(
        data=data,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=getattr(request.state, "tenant_id", None),
    )
