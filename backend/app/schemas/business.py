from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field, ConfigDict


class BusinessModeUpdate(BaseModel):
    mode: Literal["products", "services", "hybrid"] = Field(
        description="Business configuration mode per Specification §3"
    )


class BusinessModeResponse(BaseModel):
    tenant_id: str
    business_mode: str
    active_capabilities: List[str]


class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    price: float = Field(ge=0)
    stock_quantity: int = Field(default=0, ge=0)
    supplier: Optional[str] = None


class ProductRead(ProductCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    is_active: bool


class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: float = Field(ge=0)
    duration_minutes: int = Field(default=60, gt=0)
    staff_members: Optional[List[str]] = None


class ServiceRead(ServiceCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    is_active: bool


class CSVImportRequest(BaseModel):
    csv_content: str
    column_mapping: Dict[str, str] = Field(
        description="Mapping from CSV column headers to schema fields (e.g. {'Item Number': 'sku', 'Cost': 'price'})"
    )


class SyncSummary(BaseModel):
    data_source_id: str
    records_processed: int
    records_created: int
    quality_score: int
    issues_detected: List[Dict[str, Any]]
