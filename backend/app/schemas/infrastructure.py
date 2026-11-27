from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ServiceTelemetryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    type: str
    status: str
    latency: str
    details: Optional[Dict[str, Any]] = None


class InfrastructureDashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    overall_status: str
    services: List[ServiceTelemetryItem]
    rpo_benchmark: str
    rto_benchmark: str
    last_backup_status: str
    timestamp: str


class ScalingPolicyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    min_capacity: int = 2
    max_capacity: int = 20
    target_cpu_utilization_pct: int = 70
    current_instances: int = 2
    scaling_status: str = "STEADY"


class TenantQuotaUsageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tenant_id: str
    storage_used_bytes: int
    storage_limit_bytes: int
    storage_used_percentage: float
    monthly_request_count: int
    monthly_request_limit: int
    quota_status: str = "NORMAL"
