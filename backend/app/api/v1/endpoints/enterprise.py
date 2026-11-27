import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.auth import get_current_user, require_roles, AuthenticatedUser
from app.core.security import hash_password
from app.models.enterprise import AuditLog
from app.models.user import User
from app.schemas.envelope import APIResponse
from app.schemas.enterprise import (
    TenantBrandingUpdate,
    TenantBrandingRead,
    StaffUserInviteRequest,
    StaffUserRoleUpdateRequest,
    StaffUserRead,
    SecurityPostureResponse,
    SessionRevokeRequest,
    SessionRevokeResponse,
    AuditLogRead,
    AuditLogExportResponse,
    AuditLogVerifyResponse,
    ModelRoutingConfigUpdate,
    ModelRoutingConfigRead,
)
from app.services.enterprise.admin import EnterpriseAdminService

router = APIRouter()


# ---------------------------------------------------------
# Corporate Branding
# ---------------------------------------------------------
@router.get("/branding", response_model=APIResponse[TenantBrandingRead])
async def get_branding(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TenantBrandingRead]:
    """Retrieve tenant corporate branding and theme configuration."""
    branding = await EnterpriseAdminService.get_or_create_branding(current_user.tenant_id, db)
    await db.commit()
    return APIResponse.ok(
        data=TenantBrandingRead.model_validate(branding),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.patch("/branding", response_model=APIResponse[TenantBrandingRead])
async def update_branding(
    branding_in: TenantBrandingUpdate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TenantBrandingRead]:
    """Update tenant corporate branding settings (Admin/Owner only)."""
    branding = await EnterpriseAdminService.update_branding(current_user.tenant_id, branding_in, db)

    # Record audit trail
    await EnterpriseAdminService.record_audit_event(
        tenant_id=current_user.tenant_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        event_type="SETTINGS_UPDATE",
        target_resource="branding",
        status="SUCCESS",
        details={"primary_color": branding_in.primary_color, "accent_color": branding_in.accent_color},
        db=db,
    )
    await db.commit()

    return APIResponse.ok(
        data=TenantBrandingRead.model_validate(branding),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


# ---------------------------------------------------------
# Staff User Management (RBAC)
# ---------------------------------------------------------
@router.get("/users", response_model=APIResponse[List[StaffUserRead]])
async def list_staff_users(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[StaffUserRead]]:
    """List staff members in the tenant."""
    res = await db.execute(select(User).where(User.tenant_id == current_user.tenant_id))
    users = res.scalars().all()
    return APIResponse.ok(
        data=[StaffUserRead.model_validate(u) for u in users],
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/users/invite", response_model=APIResponse[StaffUserRead])
async def invite_staff_user(
    invite_in: StaffUserInviteRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[StaffUserRead]:
    """Invite a new staff user and allocate initial RBAC role (Admin/Owner only)."""
    # Check duplicate email in tenant
    dup_res = await db.execute(
        select(User).where(User.tenant_id == current_user.tenant_id, User.email == invite_in.email)
    )
    if dup_res.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "USER_EXISTS", "message": f"User with email '{invite_in.email}' already exists."},
        )

    hashed_pw = hash_password(invite_in.temp_password)
    user = User(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        email=invite_in.email,
        full_name=invite_in.full_name,
        role=invite_in.role,
        hashed_password=hashed_pw,
    )
    db.add(user)

    # Record audit log
    await EnterpriseAdminService.record_audit_event(
        tenant_id=current_user.tenant_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        event_type="USER_INVITED",
        target_resource=f"user:{user.id}",
        status="SUCCESS",
        details={"invited_email": invite_in.email, "role": invite_in.role},
        db=db,
    )
    await db.commit()

    return APIResponse.ok(
        data=StaffUserRead.model_validate(user),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.patch("/users/{user_id}/role", response_model=APIResponse[StaffUserRead])
async def update_staff_role(
    user_id: str,
    role_in: StaffUserRoleUpdateRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[StaffUserRead]:
    """Update a staff member's RBAC role (Admin/Owner only)."""
    res = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == current_user.tenant_id)
    )
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": f"Staff user '{user_id}' not found."},
        )

    old_role = user.role
    user.role = role_in.role

    # Audit role change
    await EnterpriseAdminService.record_audit_event(
        tenant_id=current_user.tenant_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        event_type="ROLE_CHANGE",
        target_resource=f"user:{user_id}",
        status="SUCCESS",
        details={"old_role": old_role, "new_role": role_in.role},
        db=db,
    )
    await db.commit()

    return APIResponse.ok(
        data=StaffUserRead.model_validate(user),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


# ---------------------------------------------------------
# Security Center & Audit Trail
# ---------------------------------------------------------
@router.get("/security/posture", response_model=APIResponse[SecurityPostureResponse])
async def get_security_posture(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[SecurityPostureResponse]:
    """Get Security Center posture metrics and compliance health score."""
    posture = await EnterpriseAdminService.get_security_posture(current_user.tenant_id, db)
    await db.commit()
    return APIResponse.ok(
        data=posture,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/security/revoke-session", response_model=APIResponse[SessionRevokeResponse])
async def revoke_user_session(
    revoke_in: SessionRevokeRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[SessionRevokeResponse]:
    """Revoke active authentication sessions for a staff member."""
    resp = await EnterpriseAdminService.revoke_user_sessions(
        tenant_id=current_user.tenant_id,
        user_id=revoke_in.user_id,
        admin_user=current_user,
        reason=revoke_in.reason,
        db=db,
    )
    await db.commit()
    return APIResponse.ok(
        data=resp,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/audit-logs", response_model=APIResponse[List[AuditLogRead]])
async def list_audit_logs(
    request: Request,
    event_type: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[AuditLogRead]]:
    """List immutable security audit log events."""
    query = select(AuditLog).where(AuditLog.tenant_id == current_user.tenant_id)
    if event_type:
        query = query.where(AuditLog.event_type == event_type)
    query = query.order_by(AuditLog.hash_timestamp.desc(), AuditLog.created_at.desc())
    res = await db.execute(query)
    logs = res.scalars().all()

    return APIResponse.ok(
        data=[AuditLogRead.model_validate(log) for log in logs],
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/audit-logs/verify", response_model=APIResponse[AuditLogVerifyResponse])
async def verify_audit_logs(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[AuditLogVerifyResponse]:
    """Verify cryptographic hash chain integrity of tenant audit logs."""
    result = await EnterpriseAdminService.verify_audit_chain(current_user.tenant_id, db)
    return APIResponse.ok(
        data=AuditLogVerifyResponse(**result),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/audit-logs/export", response_model=APIResponse[AuditLogExportResponse])
async def export_audit_logs(
    request: Request,
    export_format: str = Query("csv", alias="format", pattern="^(csv|json)$"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[AuditLogExportResponse]:
    """Export security audit trail in compliant CSV format."""
    query = select(AuditLog).where(AuditLog.tenant_id == current_user.tenant_id).order_by(AuditLog.created_at.desc())
    res = await db.execute(query)
    logs = res.scalars().all()

    content = EnterpriseAdminService.export_audit_logs_to_csv(logs)
    filename = f"banking_ai_audit_trail_{current_user.tenant_id}.csv"

    # Record export in audit trail
    await EnterpriseAdminService.record_audit_event(
        tenant_id=current_user.tenant_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        event_type="DATA_EXPORT",
        target_resource="audit_logs",
        status="SUCCESS",
        details={"record_count": len(logs), "format": export_format},
        db=db,
    )
    await db.commit()

    return APIResponse.ok(
        data=AuditLogExportResponse(
            format=export_format,
            filename=filename,
            total_records=len(logs),
            content=content,
        ),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


# ---------------------------------------------------------
# Model Routing Configuration
# ---------------------------------------------------------
@router.get("/model-config", response_model=APIResponse[ModelRoutingConfigRead])
async def get_model_config(
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ModelRoutingConfigRead]:
    """Retrieve tenant LLM model routing and temperature parameters."""
    cfg = await EnterpriseAdminService.get_or_create_model_config(current_user.tenant_id, db)
    await db.commit()
    return APIResponse.ok(
        data=ModelRoutingConfigRead.model_validate(cfg),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.patch("/model-config", response_model=APIResponse[ModelRoutingConfigRead])
async def update_model_config(
    config_in: ModelRoutingConfigUpdate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ModelRoutingConfigRead]:
    """Update tenant LLM model routing parameters (Admin/Owner only)."""
    cfg = await EnterpriseAdminService.update_model_config(current_user.tenant_id, config_in, db)

    # Record audit trail
    await EnterpriseAdminService.record_audit_event(
        tenant_id=current_user.tenant_id,
        actor_id=current_user.id,
        actor_email=current_user.email,
        actor_role=current_user.role,
        event_type="SETTINGS_UPDATE",
        target_resource="model_routing_config",
        status="SUCCESS",
        details={"default_model": config_in.default_model, "temperature": config_in.temperature},
        db=db,
    )
    await db.commit()

    return APIResponse.ok(
        data=ModelRoutingConfigRead.model_validate(cfg),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
