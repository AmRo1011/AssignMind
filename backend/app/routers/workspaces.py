"""
AssignMind — Workspaces Router

Endpoints for Workspace CRUD and member management logic per Constitution rules 
requiring Team Leader auth bounds on structural endpoints.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.workspace_member import WorkspaceMember
from app.dependencies import get_current_user, require_team_leader, require_workspace_member
from app.schemas.workspace import (
    WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse, TransferLeadershipRequest
)
from app.services import workspace_service

router = APIRouter(prefix="/api/workspaces", tags=["workspaces"])

@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    data: WorkspaceCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> WorkspaceResponse:
    """Create a new workspace and assign the creator as Team Leader."""
    workspace = await workspace_service.create_workspace(db, user.id, data)
    # Assign default response structure Role since they are auto-appointed
    res = WorkspaceResponse.model_validate(workspace)
    res.role = "leader"
    return res

@router.get("", response_model=list[WorkspaceResponse])
async def list_workspaces(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> list[WorkspaceResponse]:
    """Retrieve all non-archived workspaces the user belongs to."""
    workspaces = await workspace_service.list_active_workspaces(db, user.id)
    # Fast proxy appending role contexts matching db
    out = []
    for w in workspaces:
        dto = WorkspaceResponse.model_validate(w)
        # Note: In a larger app we query roles together, this is fine for MVP memory size.
        out.append(dto)
    return out

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: UUID,
    membership: WorkspaceMember = Depends(require_workspace_member),
    db: AsyncSession = Depends(get_db)
) -> WorkspaceResponse:
    """Get single workspace populated with its member listing."""
    workspace = await workspace_service.get_workspace_with_details(db, workspace_id)
    if not workspace or workspace.is_archived:
        raise HTTPException(status_code=404, detail="Workspace not found.")
        
    res = WorkspaceResponse.model_validate(workspace)
    res.role = membership.role
    return res

@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: UUID,
    data: WorkspaceUpdate,
    membership: WorkspaceMember = Depends(require_team_leader),
    db: AsyncSession = Depends(get_db)
) -> WorkspaceResponse:
    """Change workspace meta tags (Team Leader only)."""
    workspace = await workspace_service.get_workspace_with_details(db, workspace_id)
    if not workspace or workspace.is_archived:
        raise HTTPException(status_code=404, detail="Workspace not found.")
        
    updated = await workspace_service.update_workspace(db, workspace, data)
    res = WorkspaceResponse.model_validate(updated)
    res.role = "leader"
    return res

@router.post("/{workspace_id}/archive", response_model=WorkspaceResponse)
async def archive_workspace(
    workspace_id: UUID,
    membership: WorkspaceMember = Depends(require_team_leader),
    db: AsyncSession = Depends(get_db)
) -> WorkspaceResponse:
    """Archive workspace gracefully (Team Leader only)."""
    workspace = await workspace_service.get_workspace_with_details(db, workspace_id)
    if not workspace or workspace.is_archived:
        raise HTTPException(status_code=404, detail="Workspace not found.")
        
    archived = await workspace_service.archive_workspace(db, workspace)
    return WorkspaceResponse.model_validate(archived)

@router.post("/{workspace_id}/transfer-leadership", status_code=status.HTTP_200_OK)
async def transfer_leadership(
    workspace_id: UUID,
    data: TransferLeadershipRequest,
    membership: WorkspaceMember = Depends(require_team_leader),
    db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """Pass Leader role to another valid member within the space."""
    await workspace_service.transfer_leadership(db, workspace_id, membership.user_id, data.new_leader_id)
    return {"message": "Leadership transferred successfully."}
