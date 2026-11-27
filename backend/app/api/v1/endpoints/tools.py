import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.auth import get_current_user, require_roles, AuthenticatedUser
from app.models.tool import ToolExecution, MCPServerConfig
from app.schemas.envelope import APIResponse
from app.schemas.tool import (
    ToolDefinitionRead,
    ToolExecuteRequest,
    ToolExecuteResponse,
    ToolApprovalDecisionRequest,
    ToolExecutionRead,
    MCPServerConfigCreate,
    MCPServerConfigRead,
)
from app.services.tools.gateway import ToolGatewayService

router = APIRouter()


@router.get("", response_model=APIResponse[List[ToolDefinitionRead]])
async def list_registered_tools(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
) -> APIResponse[List[ToolDefinitionRead]]:
    """List all registered tools in the Tool Gateway with schemas and risk classifications."""
    tools = ToolGatewayService.list_tools()
    return APIResponse.ok(
        data=tools,
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/execute", response_model=APIResponse[ToolExecuteResponse])
async def execute_tool(
    exec_in: ToolExecuteRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ToolExecuteResponse]:
    """
    Execute tool through Governed Tool Gateway.
    - Low/Medium risk tools execute and return sanitized results.
    - High-risk tools are intercepted into `requires_approval` awaiting supervisor action.
    """
    try:
        caller_id = exec_in.caller_id or current_user.id
        resp = await ToolGatewayService.execute_tool(
            tenant_id=current_user.tenant_id,
            tool_name=exec_in.tool_name,
            caller_agent=exec_in.caller_agent,
            caller_id=caller_id,
            parameters=exec_in.parameters,
            db=db,
            requested_by_user_id=current_user.id,
            requested_by_role=current_user.role,
        )
        await db.commit()
        return APIResponse.ok(
            data=resp,
            request_id=getattr(request.state, "request_id", None),
            tenant_id=current_user.tenant_id,
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "TOOL_VALIDATION_ERROR", "message": str(ve)},
        )


@router.get("/executions", response_model=APIResponse[List[ToolExecutionRead]])
async def list_executions(
    request: Request,
    status_filter: Optional[str] = Query(None, alias="status"),
    tool_name: Optional[str] = None,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[ToolExecutionRead]]:
    """List tool execution audit log entries."""
    query = select(ToolExecution).where(ToolExecution.tenant_id == current_user.tenant_id)
    if status_filter:
        query = query.where(ToolExecution.status == status_filter)
    if tool_name:
        query = query.where(ToolExecution.tool_name == tool_name)

    query = query.order_by(ToolExecution.created_at.desc())
    res = await db.execute(query)
    executions = res.scalars().all()

    return APIResponse.ok(
        data=[ToolExecutionRead.model_validate(e) for e in executions],
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.get("/executions/{execution_id}", response_model=APIResponse[ToolExecutionRead])
async def get_execution_detail(
    execution_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ToolExecutionRead]:
    """Retrieve full audit detail for a specific tool execution."""
    res = await db.execute(
        select(ToolExecution).where(
            ToolExecution.id == execution_id,
            ToolExecution.tenant_id == current_user.tenant_id,
        )
    )
    execution = res.scalar_one_or_none()
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "EXECUTION_NOT_FOUND", "message": f"Tool execution '{execution_id}' not found."},
        )

    return APIResponse.ok(
        data=ToolExecutionRead.model_validate(execution),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/executions/{execution_id}/approve", response_model=APIResponse[ToolExecuteResponse])
async def approve_tool_execution(
    execution_id: str,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles(["owner", "admin"])),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ToolExecuteResponse]:
    """Supervisor approval gate: approves and executes a pending high-risk tool call."""
    try:
        resp = await ToolGatewayService.approve_and_execute(
            execution_id=execution_id,
            tenant_id=current_user.tenant_id,
            approver_id=current_user.id,
            db=db,
        )
        await db.commit()
        return APIResponse.ok(
            data=resp,
            request_id=getattr(request.state, "request_id", None),
            tenant_id=current_user.tenant_id,
        )
    except PermissionError as pe:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "SELF_APPROVAL_FORBIDDEN", "message": str(pe)},
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "APPROVAL_ERROR", "message": str(ve)},
        )


@router.post("/executions/{execution_id}/reject", response_model=APIResponse[ToolExecuteResponse])
async def reject_tool_execution(
    execution_id: str,
    decision_in: ToolApprovalDecisionRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles(["owner", "admin"])),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[ToolExecuteResponse]:
    """Supervisor rejection gate: rejects a pending high-risk tool call."""
    try:
        resp = await ToolGatewayService.reject_execution(
            execution_id=execution_id,
            tenant_id=current_user.tenant_id,
            approver_id=current_user.id,
            reason=decision_in.reason,
            db=db,
        )
        await db.commit()
        return APIResponse.ok(
            data=resp,
            request_id=getattr(request.state, "request_id", None),
            tenant_id=current_user.tenant_id,
        )
    except PermissionError as pe:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "SELF_APPROVAL_FORBIDDEN", "message": str(pe)},
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "REJECTION_ERROR", "message": str(ve)},
        )


@router.get("/mcp-servers", response_model=APIResponse[List[MCPServerConfigRead]])
async def list_mcp_servers(
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin", "agent")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[List[MCPServerConfigRead]]:
    """List registered Model Context Protocol (MCP) servers."""
    res = await db.execute(
        select(MCPServerConfig).where(MCPServerConfig.tenant_id == current_user.tenant_id)
    )
    servers = res.scalars().all()
    return APIResponse.ok(
        data=[MCPServerConfigRead.model_validate(s) for s in servers],
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )


@router.post("/mcp-servers", response_model=APIResponse[MCPServerConfigRead])
async def register_mcp_server(
    server_in: MCPServerConfigCreate,
    request: Request,
    current_user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[MCPServerConfigRead]:
    """Register a new external MCP server and mock initial tool discovery."""
    discovered = [
        {
            "name": f"{server_in.name.lower().replace(' ', '_')}_query",
            "description": f"External MCP action from {server_in.name}",
            "risk_level": "LOW",
        }
    ]
    server = MCPServerConfig(
        id=str(uuid.uuid4()),
        tenant_id=current_user.tenant_id,
        name=server_in.name,
        transport_type=server_in.transport_type,
        endpoint_url=server_in.endpoint_url,
        auth_token=server_in.auth_token,
        is_enabled=server_in.is_enabled,
        discovered_tools=discovered,
    )
    db.add(server)
    await db.commit()

    return APIResponse.ok(
        data=MCPServerConfigRead.model_validate(server),
        request_id=getattr(request.state, "request_id", None),
        tenant_id=current_user.tenant_id,
    )
