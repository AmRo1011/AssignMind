"""
AssignMind — Task Service Layer

Logic governing task distribution and persistence within a Workspace matching rules.
"""

from uuid import UUID
import json
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.task import Task
from app.models.workspace_member import WorkspaceMember
from app.models.user import User
from app.schemas.ai import GeneratedTask
from app.schemas.task import TaskCreate
from app.services.ai_service import AIService
from app.services import assignment_service
from app.utils.sanitize import sanitize_and_trim

logger = structlog.get_logger()

async def get_workspace_member_list(db: AsyncSession, workspace_id: UUID) -> str:
    """Format members list for AI context."""
    stmt = (
        select(WorkspaceMember)
        .options(selectinload(WorkspaceMember.user))
        .where(WorkspaceMember.workspace_id == workspace_id)
    )
    res = await db.execute(stmt)
    members = res.scalars().all()
    out = []
    for m in members:
        out.append(f"{m.user.full_name} ({m.user.email}) - Role: {m.role}")
    return "\n".join(out)

async def generate_task_plan(
    db: AsyncSession, ai: AIService, workspace_id: UUID, user_id: UUID, req_constraints: str | None
) -> list[GeneratedTask]:
    """Extract Assignment config, fetch team state, format prompt, call AI distribute."""
    assignment = await assignment_service.get_latest_assignment(db, workspace_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Document uploaded to generate tasks from."
        )

    out = assignment.structured_summary
    if req_constraints:
        safe_req = sanitize_and_trim(req_constraints)
        if "constraints" not in out:
            out["constraints"] = []
        out["constraints"].append(f"TEAM_LEADER_INPUT:\n{safe_req}")

    members = await get_workspace_member_list(db, workspace_id)
    return await ai.generate_task_distribution(
        db, user_id, outline=json.dumps(out), members=members
    )

async def finalize_tasks(
    db: AsyncSession,
    workspace_id: UUID,
    user_id: UUID,
    tasks_req: list[TaskCreate]
) -> list[Task]:
    """Take explicit task objects and persist them collectively bounded by positions."""
    stmt = select(func.max(Task.position)).where(Task.workspace_id == workspace_id)
    result = await db.execute(stmt)
    current_max = result.scalar() or 0

    created = []
    for idx, t in enumerate(tasks_req):
        raw_db_task = Task(
            workspace_id=workspace_id,
            title=sanitize_and_trim(t.title),
            description=sanitize_and_trim(t.description) if t.description else None,
            status=t.status,
            assigned_to=t.assigned_to,
            deadline=t.deadline,
            position=current_max + idx + 1,
            is_ai_generated=t.is_ai_generated,
            created_by=user_id
        )
        db.add(raw_db_task)
        created.append(raw_db_task)
        
    await db.commit()
    for task in created:
        await db.refresh(task)
        
    logger.info("tasks_finalized", total=len(created), workspace=str(workspace_id))
    return created

async def list_tasks(db: AsyncSession, workspace_id: UUID) -> list[Task]:
    """Retrieve all tasks within a specific workspace."""
    stmt = select(Task).where(Task.workspace_id == workspace_id).order_by(Task.position.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def create_task(db: AsyncSession, workspace_id: UUID, user_id: UUID, req: TaskCreate) -> Task:
    """Manual ad-hoc task creation."""
    stmt = select(func.max(Task.position)).where(Task.workspace_id == workspace_id)
    current_max = (await db.execute(stmt)).scalar() or 0
    
    t = Task(
        workspace_id=workspace_id,
        title=sanitize_and_trim(req.title),
        description=sanitize_and_trim(req.description) if req.description else None,
        status=req.status,
        assigned_to=req.assigned_to,
        deadline=req.deadline,
        position=current_max + 1,
        created_by=user_id
    )
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return t

async def update_task(db: AsyncSession, task_id: UUID, update_data: dict, member: WorkspaceMember) -> Task:
    """Modify task payload correctly tracking status transitions to AI triggers."""
    task = await db.get(Task, task_id)
    if not task or task.workspace_id != member.workspace_id:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if member.role != "leader" and task.assigned_to != member.user_id:
        raise HTTPException(status_code=403, detail="Not allowed to update this task")
        
    was_not_done = task.status != "done"
    old_deadline = task.deadline
    
    if "title" in update_data: task.title = sanitize_and_trim(update_data["title"])
    if "description" in update_data: 
        val = update_data["description"]
        task.description = sanitize_and_trim(val) if val else None
    if "assigned_to" in update_data: task.assigned_to = update_data["assigned_to"]
    if "deadline" in update_data: task.deadline = update_data["deadline"]
    if "status" in update_data: task.status = update_data["status"]
        
    if "deadline" in update_data and old_deadline != update_data["deadline"]:
        from app.services.email_scheduler_service import cancel_task_emails
        await cancel_task_emails(db, task.id)
        
    if "status" in update_data and update_data["status"] == "done" and was_not_done:
        from app.services.chat_service import _publish_task_completion
        from app.services.email_scheduler_service import cancel_task_emails
        await _publish_task_completion(db, task.workspace_id, task.title)
        await cancel_task_emails(db, task.id)
        
    await db.commit()
    await db.refresh(task)
    return task

async def delete_task(db: AsyncSession, task_id: UUID, workspace_id: UUID) -> None:
    """Drop task row explicitly."""
    task = await db.get(Task, task_id)
    if not task or task.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()
