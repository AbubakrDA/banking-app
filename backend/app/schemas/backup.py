from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class BackupTriggerRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    backup_type: str = Field(default="FULL", description="FULL, INCREMENTAL, WAL, SNAPSHOT")
    target_type: str = Field(default="POSTGRESQL", description="POSTGRESQL, OBJECT_STORAGE, FULL_SYSTEM")
    retention_tier: str = Field(default="DAILY", description="DAILY, WEEKLY, MONTHLY, MANUAL")
    notes: Optional[str] = Field(default=None, description="Optional administrative notes for this backup")


class BackupRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: Optional[str] = None
    backup_type: str
    target_type: str
    status: str
    storage_path: str
    size_bytes: int
    sha256_checksum: str
    is_encrypted: bool
    encryption_algorithm: str
    retention_tier: str
    expires_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    meta_data: Optional[Dict[str, Any]] = None


class BackupListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    items: List[BackupRecordResponse]


class RestoreDrillRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    backup_id: str
    simulate_failure: bool = Field(default=False, description="Flag for chaos engineering / drill failure testing")
    notes: Optional[str] = Field(default=None, description="Optional drill hypothesis or audit notes")


class RestoreDrillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    backup_id: str
    tenant_id: Optional[str] = None
    status: str
    rto_seconds: int
    rpo_minutes: int
    tables_validated: int
    records_validated: int
    checksum_verified: bool
    drill_notes: Optional[str] = None
    executed_by: Optional[str] = None
    created_at: datetime


class DrillListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    items: List[RestoreDrillResponse]


class RetentionPolicyUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    daily_retention_days: Optional[int] = Field(default=None, ge=1, le=365)
    weekly_retention_weeks: Optional[int] = Field(default=None, ge=1, le=52)
    monthly_retention_months: Optional[int] = Field(default=None, ge=1, le=120)
    auto_drills_enabled: Optional[bool] = None
    drill_frequency_days: Optional[int] = Field(default=None, ge=1, le=90)


class RetentionPolicyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: Optional[str] = None
    daily_retention_days: int
    weekly_retention_weeks: int
    monthly_retention_months: int
    auto_drills_enabled: bool
    drill_frequency_days: int
    created_at: datetime
    updated_at: datetime


class BackupStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    overall_status: str
    rpo_target: str = "< 1 Hour"
    rto_target: str = "< 4 Hours"
    current_rpo_minutes: int
    current_rto_seconds: int
    rpo_compliant: bool
    rto_compliant: bool
    last_backup_timestamp: Optional[str] = None
    last_backup_status: str
    next_scheduled_backup: str
    total_backups_count: int
    last_drill_status: Optional[str] = None
    last_drill_timestamp: Optional[str] = None
    replication_status: str = "ACTIVE_CROSS_REGION_REPLICATION"
    encryption_status: str = "AES_256_GCM_ENCRYPTED"


class PruneBackupsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pruned_count: int
    freed_bytes: int
    message: str
