from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user, require_roles, AuthenticatedUser
from app.schemas.envelope import APIResponse
from app.schemas.backup import (
    BackupTriggerRequest,
    BackupRecordResponse,
    BackupListResponse,
    RestoreDrillRequest,
    RestoreDrillResponse,
    DrillListResponse,
    RetentionPolicyUpdate,
    RetentionPolicyResponse,
    BackupStatusResponse,
    PruneBackupsResponse,
)
from app.services.backup.engine import BackupEngineService
from app.services.enterprise.admin import EnterpriseAdminService

router = APIRouter()


@router.get("/status", response_model=APIResponse[BackupStatusResponse])
async def get_backup_status(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[BackupStatusResponse]:
    """Retrieve live backup health, RPO/RTO compliance metrics, and next scheduled backup window."""
    status_data = await BackupEngineService.get_backup_status(db, current_user.tenant_id)
    return APIResponse.ok(
        data=status_data,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/trigger", response_model=APIResponse[BackupRecordResponse])
async def trigger_backup(
    backup_in: BackupTriggerRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[BackupRecordResponse]:
    """Manually trigger an encrypted database or system backup (Admin/Owner only)."""
    record = await BackupEngineService.create_backup(
        db=db,
        tenant_id=current_user.tenant_id,
        request=backup_in,
        actor_id=current_user.id,
    )

    # Record tamper-evident audit trail
    await EnterpriseAdminService.record_audit_event(
        tenant_id=current_user.tenant_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        event_type="BACKUP_TRIGGERED",
        target_resource=f"backup:{record.id}",
        status="SUCCESS",
        details={
            "backup_id": record.id,
            "backup_type": record.backup_type,
            "target_type": record.target_type,
            "retention_tier": record.retention_tier,
            "storage_path": record.storage_path,
        },
        db=db,
    )

    return APIResponse.ok(
        data=BackupRecordResponse.model_validate(record),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/history", response_model=APIResponse[BackupListResponse])
async def get_backup_history(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[BackupListResponse]:
    """Retrieve historical backup catalog with checksum verification and retention metadata."""
    history = await BackupEngineService.get_backup_history(
        db=db,
        tenant_id=current_user.tenant_id,
        limit=limit,
        offset=offset,
    )
    return APIResponse.ok(
        data=history,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/drill", response_model=APIResponse[RestoreDrillResponse])
async def execute_restore_drill(
    drill_in: RestoreDrillRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[RestoreDrillResponse]:
    """Execute automated non-destructive restore verification drill in isolated sandbox (Admin/Owner only)."""
    drill = await BackupEngineService.execute_restore_drill(
        db=db,
        tenant_id=current_user.tenant_id,
        request=drill_in,
        actor_id=current_user.id,
    )

    # Record tamper-evident audit trail
    await EnterpriseAdminService.record_audit_event(
        tenant_id=current_user.tenant_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        event_type="RESTORE_DRILL_EXECUTED",
        target_resource=f"drill:{drill.id}",
        status=drill.status,
        details={
            "drill_id": drill.id,
            "backup_id": drill.backup_id,
            "rto_seconds": drill.rto_seconds,
            "rpo_minutes": drill.rpo_minutes,
            "checksum_verified": drill.checksum_verified,
        },
        db=db,
    )

    return APIResponse.ok(
        data=RestoreDrillResponse.model_validate(drill),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/drills", response_model=APIResponse[DrillListResponse])
async def get_drill_history(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[DrillListResponse]:
    """Retrieve historical automated restore drill validation logs."""
    history = await BackupEngineService.get_drill_history(
        db=db,
        tenant_id=current_user.tenant_id,
        limit=limit,
        offset=offset,
    )
    return APIResponse.ok(
        data=history,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/retention-policy", response_model=APIResponse[RetentionPolicyResponse])
async def get_retention_policy(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[RetentionPolicyResponse]:
    """Retrieve Grandfather-Father-Son (GFS) backup retention schedule."""
    policy = await BackupEngineService.get_or_create_retention_policy(db, current_user.tenant_id)
    return APIResponse.ok(
        data=RetentionPolicyResponse.model_validate(policy),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.put("/retention-policy", response_model=APIResponse[RetentionPolicyResponse])
async def update_retention_policy(
    policy_in: RetentionPolicyUpdate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[RetentionPolicyResponse]:
    """Update GFS backup retention parameters (Admin/Owner only)."""
    policy = await BackupEngineService.update_retention_policy(db, current_user.tenant_id, policy_in)

    # Record audit trail
    await EnterpriseAdminService.record_audit_event(
        tenant_id=current_user.tenant_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        event_type="SETTINGS_UPDATE",
        target_resource="backup_retention_policy",
        status="SUCCESS",
        details=policy_in.model_dump(exclude_unset=True),
        db=db,
    )

    return APIResponse.ok(
        data=RetentionPolicyResponse.model_validate(policy),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/prune", response_model=APIResponse[PruneBackupsResponse])
async def prune_expired_backups(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[PruneBackupsResponse]:
    """Prune expired backup archives past retention date (Admin/Owner only)."""
    res = await BackupEngineService.prune_expired_backups(db)
    return APIResponse.ok(
        data=res,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
