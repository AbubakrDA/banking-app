import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.database import get_db
from app.core.auth import get_current_user, require_roles, AuthenticatedUser
from app.models.tenant import Tenant
from app.models.business import Product, Service, DataSource, SyncHistory
from app.schemas.envelope import APIResponse
from app.schemas.business import (
    BusinessModeUpdate,
    BusinessModeResponse,
    ProductCreate,
    ProductRead,
    ServiceCreate,
    ServiceRead,
    CSVImportRequest,
    SyncSummary,
)
from app.services.connectors.csv_parser import CSVConnector
from app.services.data_quality import DataQualityEngine

router = APIRouter()


@router.get("/mode", response_model=APIResponse[BusinessModeResponse])
async def get_business_mode(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[BusinessModeResponse]:
    result = await db.execute(select(Tenant).where(Tenant.id == current_user.tenant_id))
    tenant = result.scalars().first()
    mode = tenant.business_mode if tenant else "hybrid"

    caps = ["analytics", "chat", "knowledge_base"]
    if mode in ("products", "hybrid"):
        caps.extend(["inventory", "suppliers", "physical_orders"])
    if mode in ("services", "hybrid"):
        caps.extend(["appointments", "service_catalog", "staff_providers"])

    data = BusinessModeResponse(tenant_id=current_user.tenant_id, business_mode=mode, active_capabilities=caps)
    return APIResponse.ok(data=data, request_id=getattr(request.state, "request_id", None), tenant_id=current_user.tenant_id)


@router.patch("/mode", response_model=APIResponse[BusinessModeResponse])
async def update_business_mode(
    update_data: BusinessModeUpdate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("admin", "owner")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[BusinessModeResponse]:
    result = await db.execute(select(Tenant).where(Tenant.id == current_user.tenant_id))
    tenant = result.scalars().first()
    if tenant:
        tenant.business_mode = update_data.mode
    else:
        tenant = Tenant(
            id=current_user.tenant_id,
            name=f"Tenant {current_user.tenant_id}",
            slug=current_user.tenant_id,
            business_mode=update_data.mode,
        )
        db.add(tenant)
    await db.commit()

    return await get_business_mode(request=request, current_user=current_user, db=db)


@router.post("/products", response_model=APIResponse[ProductRead])
async def create_product(
    product_in: ProductCreate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ProductRead]:
    # Check for duplicate SKU in tenant
    existing = await db.execute(
        select(Product).where(Product.sku == product_in.sku, Product.tenant_id == current_user.tenant_id)
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU '{product_in.sku}' already exists",
        )

    db_product = Product(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        **product_in.model_dump(),
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)

    return APIResponse.ok(
        data=ProductRead.model_validate(db_product),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/products", response_model=APIResponse[List[ProductRead]])
async def list_products(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[ProductRead]]:
    result = await db.execute(select(Product).where(Product.tenant_id == current_user.tenant_id))
    products = result.scalars().all()
    data = [ProductRead.model_validate(p) for p in products]
    return APIResponse.ok(data=data, request_id=getattr(request.state, "request_id", None), tenant_id=current_user.tenant_id)


@router.post("/services", response_model=APIResponse[ServiceRead])
async def create_service(
    service_in: ServiceCreate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ServiceRead]:
    db_service = Service(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        **service_in.model_dump(),
    )
    db.add(db_service)
    await db.commit()
    await db.refresh(db_service)

    return APIResponse.ok(
        data=ServiceRead.model_validate(db_service),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/services", response_model=APIResponse[List[ServiceRead]])
async def list_services(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[ServiceRead]]:
    result = await db.execute(select(Service).where(Service.tenant_id == current_user.tenant_id))
    services = result.scalars().all()
    data = [ServiceRead.model_validate(s) for s in services]
    return APIResponse.ok(data=data, request_id=getattr(request.state, "request_id", None), tenant_id=current_user.tenant_id)


@router.post("/import/csv", response_model=APIResponse[SyncSummary])
async def import_csv_data(
    import_req: CSVImportRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[SyncSummary]:
    headers, rows = CSVConnector.parse_csv_content(import_req.csv_content)
    normalized = CSVConnector.apply_column_mapping(rows, import_req.column_mapping)

    # 1. Run Data Quality & Hygiene Engine
    quality_score, issues = DataQualityEngine.validate_products(normalized)

    # 2. Ingest clean records into database
    created_count = 0
    if quality_score >= 50:  # Ingestion threshold
        for item in normalized:
            if item.get("sku") and item.get("name") and float(item.get("price", 0)) >= 0:
                prod = Product(
                    id=str(uuid.uuid4()),
                    tenant_id=current_user.tenant_id,
                    sku=item["sku"],
                    name=item["name"],
                    price=float(item.get("price", 0)),
                    stock_quantity=int(item.get("stock_quantity", 0)),
                )
                db.add(prod)
                created_count += 1
        await db.commit()

    summary = SyncSummary(
        data_source_id="csv_import_session",
        records_processed=len(normalized),
        records_created=created_count,
        quality_score=quality_score,
        issues_detected=issues,
    )

    return APIResponse.ok(
        data=summary,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
