from typing import Dict
from pydantic import BaseModel, Field


class ComponentStatus(BaseModel):
    status: str = Field(description="healthy | degraded | unhealthy")
    details: str | None = None


class HealthCheckResponse(BaseModel):
    status: str = Field(default="healthy", description="healthy | degraded | unhealthy")
    service: str = "BankingAIPlatform Backend Core"
    version: str = "0.1.0"
    environment: str = "development"
    components: Dict[str, ComponentStatus] = Field(default_factory=dict)
