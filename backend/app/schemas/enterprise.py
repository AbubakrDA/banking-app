from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class TenantBrandingUpdate(BaseModel):
    logo_url: Optional[str] = Field(None, max_length=512)
    primary_color: str = Field("#0B192C", max_length=32)
    accent_color: str = Field("#1E3E62", max_length=32)
    font_family: str = Field("Inter, sans-serif", max_length=64)
    email_footer_text: Optional[str] = None
    custom_css_vars: Optional[Dict[str, str]] = None


class TenantBrandingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    logo_url: Optional[str] = None
    primary_color: str
    accent_color: str
    font_family: str
    email_footer_text: Optional[str] = None
    custom_css_vars: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class StaffUserInviteRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    role: str = Field("agent", description="owner | admin | agent | viewer")
    temp_password: str = Field("BankingAIPlatform2026!", min_length=8)


class StaffUserRoleUpdateRequest(BaseModel):
    role: str = Field(..., description="owner | admin | agent | viewer")


class StaffUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    email: str
    full_name: str
    role: str
    created_at: datetime
    updated_at: datetime


class SecurityPostureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    security_health_score: int = Field(..., description="Calculated 0-100 security score")
    total_staff_users: int
    mfa_enforced_users_pct: float
    active_sessions_count: int
    neutralized_threats_count: int
    data_retention_days: int
    last_audit_event_timestamp: Optional[str] = None
    status: str = "SECURE"


class SecurityPolicyUpdate(BaseModel):
    mfa_enforced: bool = False
    session_timeout_minutes: int = Field(60, ge=15, le=1440)
    password_rotation_days: int = Field(90, ge=30, le=365)
    data_retention_days: int = Field(365, ge=30, le=3650)
    allowed_ip_ranges: Optional[List[str]] = None


class SecurityPolicyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    mfa_enforced: bool
    session_timeout_minutes: int
    password_rotation_days: int
    data_retention_days: int
    allowed_ip_ranges: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime


class SessionRevokeRequest(BaseModel):
    user_id: str
    reason: Optional[str] = Field(None, max_length=255)


class SessionRevokeResponse(BaseModel):
    user_id: str
    revoked_sessions_count: int
    revoked_at: str
    message: str


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    actor_id: str
    actor_email: str
    actor_role: str
    event_type: str
    target_resource: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str
    details: Optional[Dict[str, Any]] = None
    prev_hash: Optional[str] = None
    event_hash: str
    created_at: datetime


class AuditLogVerifyResponse(BaseModel):
    valid: bool
    total_records: int
    broken_index: Optional[int] = None
    broken_id: Optional[str] = None
    reason: Optional[str] = None


class AuditLogExportResponse(BaseModel):
    format: str
    filename: str
    total_records: int
    content: str


class ModelRoutingConfigUpdate(BaseModel):
    default_model: str = Field("gemini-2.5-flash", max_length=64)
    fallback_model: str = Field("gemini-2.5-pro", max_length=64)
    temperature: float = Field(0.2, ge=0.0, le=1.0)
    max_tokens: int = Field(2048, ge=256, le=8192)
    system_instructions_override: Optional[str] = None


class ModelRoutingConfigRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    default_model: str
    fallback_model: str
    temperature: float
    max_tokens: int
    system_instructions_override: Optional[str] = None
    created_at: datetime
    updated_at: datetime
