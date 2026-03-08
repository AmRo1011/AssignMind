"""
AssignMind — Workspace Service Layer

Business logic for managing workspaces and membership relationships.
"""

from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate
from app.utils.sanitize import sanitize_and_trim

async def create_workspace(
    db: AsyncSession, user_id: UUID, data: WorkspaceCreate
) -> Workspace:
    """Create a new workspace and assign the creator as the Team Leader."""
    title = sanitize_and_trim(data.title)
    desc = sanitize_and_trim(data.description) if data.description else None
    
    workspace = Workspace(
        title=title,
        description=desc,
        deadline=data.deadline,
        created_by=user_id,
    )
    db.add(workspace)
    await db.flush()  # To get workspace.id
    
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user_id,
        role="leader"
    )
    db.add(member)
    await db.commit()
    await db.refresh(workspace)
    
    return workspace

async def list_active_workspaces(
    db: AsyncSession, user_id: UUID
) -> list[Workspace]:
    """Retrieve all non-archived workspaces the user is a member of."""
    stmt = (
        select(Workspace)
        .join(WorkspaceMember, Workspace.id == WorkspaceMember.workspace_id)
        .where(
            WorkspaceMember.user_id == user_id,
            Workspace.is_archived == False
        )
        .order_by(Workspace.updated_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def get_workspace_with_details(
    db: AsyncSession, workspace_id: UUID
) -> Workspace | None:
    """Get workspace including its members, mostly for leaders/viewers."""
    stmt = (
        select(Workspace)
        .options(selectinload(Workspace.members).selectinload(WorkspaceMember.user))
        .where(Workspace.id == workspace_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def update_workspace(
    db: AsyncSession, workspace: Workspace, data: WorkspaceUpdate
) -> Workspace:
    """Update general fields."""
    if data.title is not None:
        workspace.title = sanitize_and_trim(data.title)
    if data.description is not None:
        workspace.description = sanitize_and_trim(data.description)
    if data.deadline is not None:
        workspace.deadline = data.deadline
        
    await db.commit()
    await db.refresh(workspace)
    return workspace

async def archive_workspace(
    db: AsyncSession, workspace: Workspace
) -> Workspace:
    """Soft delete workspace globally."""
    workspace.is_archived = True
    workspace.archived_at = func.now()
    
    from app.services.email_scheduler_service import cancel_workspace_emails
    await cancel_workspace_emails(db, workspace.id)
    
    await db.commit()
    await db.refresh(workspace)
    return workspace

async def transfer_leadership(
    db: AsyncSession, workspace_id: UUID, current_leader_id: UUID, new_leader_id: UUID
) -> None:
    """Change current leader to member, make new member leader."""
    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id.in_([current_leader_id, new_leader_id])
        )
    )
    members = result.scalars().all()
    
    mapping = {m.user_id: m for m in members}
    if new_leader_id not in mapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New leader MUST be an existing Workspace Member."
        )

    # Shift roles
    mapping[current_leader_id].role = "member"
    mapping[new_leader_id].role = "leader"
    
    await db.commit()
