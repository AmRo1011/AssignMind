"""
AssignMind — Tasks Router

Distribution logic explicitly bound to Team Leader scopes and AI credits.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.workspace_member import WorkspaceMember
from app.dependencies import require_team_leader, require_workspace_member
from app.schemas.task import (
    TaskDistributionRequest, TaskFinalizeRequest, TaskResponse, GeneratedTaskResponse,
    TaskCreate, TaskUpdate
)
from app.schemas.ai import GeneratedTask
from app.services import task_service
from app.utils.rate_limit import rate_limiter, RateLimitExceeded
from app.config import get_settings, Settings
from app.services.ai_service import AIService, AIServiceError

router = APIRouter(prefix="/api/workspaces/{workspace_id}/tasks", tags=["tasks"])

def get_ai_service(settings: Settings = Depends(get_settings)) -> AIService:
    return AIService(api_key=settings.openrouter_api_key)

@router.post("/distribute", response_model=list[GeneratedTaskResponse])
async def distribute_tasks(
    workspace_id: UUID,
    data: TaskDistributionRequest,
    membership: WorkspaceMember = Depends(require_team_leader),
    db: AsyncSession = Depends(get_db),
    ai: AIService = Depends(get_ai_service)
) -> list[GeneratedTask]:
    """Reserve credits, fetch Workspace summary/members context, generate tasks array."""
    user_id = membership.user_id
    rate_key = f"distribute_{user_id}"
    
    try:
        rate_limiter.check(rate_key, "distribute", max_calls=3, window_seconds=3600)
    except RateLimitExceeded as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=e.message
        )

    try:
        tasks = await task_service.generate_task_plan(
            db, ai, workspace_id, user_id, data.manual_constraints
        )
    except AIServiceError as e:
        raise HTTPException(status_code=422, detail=str(e))
        
    return tasks

@router.post("/finalize", response_model=list[TaskResponse])
async def finalize_tasks(
    workspace_id: UUID,
    data: TaskFinalizeRequest,
    membership: WorkspaceMember = Depends(require_team_leader),
    db: AsyncSession = Depends(get_db)
) -> list[TaskResponse]:
    """Save explicit verified task data directly to PostgreSQL boards."""
    db_tasks = await task_service.finalize_tasks(
        db, workspace_id, membership.user_id, data.tasks
    )
    return [TaskResponse.model_validate(t) for t in db_tasks]

@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    workspace_id: UUID,
    membership: WorkspaceMember = Depends(require_workspace_member),
    db: AsyncSession = Depends(get_db)
) -> list[TaskResponse]:
    """Retrieve all tasks within a workspace (any member)."""
    tasks = await task_service.list_tasks(db, workspace_id)
    return [TaskResponse.model_validate(t) for t in tasks]

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    workspace_id: UUID,
    req: TaskCreate,
    membership: WorkspaceMember = Depends(require_team_leader),
    db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    """Create ad-hoc manual tasks (Team Leader only)."""
    task = await task_service.create_task(db, workspace_id, membership.user_id, req)
    return TaskResponse.model_validate(task)

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    workspace_id: UUID,
    task_id: UUID,
    req: TaskUpdate,
    membership: WorkspaceMember = Depends(require_workspace_member),
    db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    """Update task details. Regular members can only update their assigned tasks."""
    task = await task_service.update_task(db, task_id, req.model_dump(exclude_unset=True), membership)
    return TaskResponse.model_validate(task)

@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    workspace_id: UUID,
    task_id: UUID,
    membership: WorkspaceMember = Depends(require_team_leader),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Delete explicit tasks manually (Team Leader only)."""
    await task_service.delete_task(db, task_id, workspace_id)
    return {"message": "Task deleted."}
