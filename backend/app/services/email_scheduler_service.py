"""
AssignMind — Email Scheduler Service

Cron job running every 5 minutes scanning tasks for N-5, N-6, N-7 deadline rules.
"""

from typing import cast
import structlog
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, and_, or_, not_, func
from sqlalchemy.orm import selectinload

from app.database import async_session_factory
from app.models.task import Task
from app.models.scheduled_email import ScheduledEmail
from app.models.workspace_member import WorkspaceMember
from app.models.workspace import Workspace
from app.models.user import User
from app.services import email_service

logger = structlog.get_logger()

async def _get_users(db, t):
    a_email, l_email, l_id, ws = "", "", None, None
    if t.assigned_to:
        u = (await db.execute(select(User).where(User.id == t.assigned_to))).scalar_one_or_none()
        if u: a_email = u.email
    ws = (await db.execute(select(Workspace).where(Workspace.id == t.workspace_id))).scalar_one_or_none()
    if ws:
        l_id = ws.created_by
        lu = (await db.execute(select(User).where(User.id == l_id))).scalar_one_or_none()
        if lu: l_email = lu.email
    return a_email, l_email, l_id, ws

async def process_deadline_emails() -> None:
    """Cron entrypoint triggered every 5 minutes checking UTC task timelines."""
    logger.info("cron_deadline_checks_started")
    try:
        async with async_session_factory() as db:
            n, t72, t24 = datetime.now(timezone.utc), datetime.now(timezone.utc) + timedelta(hours=72), datetime.now(timezone.utc) + timedelta(hours=24)
            tasks = (await db.execute(select(Task).where(Task.deadline.is_not(None), Task.status != "done"))).scalars().all()
            for t in tasks:
                a_email, l_email, l_id, ws = await _get_users(db, t)
                sent = [e.email_type for e in (await db.execute(select(ScheduledEmail).where(ScheduledEmail.task_id == t.id))).scalars().all() if e.status == "sent"]
                
                if t.deadline <= t72 and t.deadline > n and "N-5" not in sent and a_email:
                    await _dispatch(db, t, ws, "N-5", a_email, 72)
                if t.deadline <= t24 and t.deadline > n and "N-6" not in sent and a_email:
                    await _dispatch(db, t, ws, "N-6", a_email, 24)
                if t.deadline <= n and "N-7" not in sent and l_email and l_id:
                    await _dispatch(db, t, ws, "N-7", l_email, 0, l_id)
    except Exception as e:
        logger.error("cron_failed", error=str(e))

async def _dispatch(db, task, ws, type_str, email_addr, hours, recipient_id=None) -> None:
    recip = recipient_id if recipient_id else task.assigned_to
    record = ScheduledEmail(
        workspace_id=task.workspace_id,
        task_id=task.id,
        recipient_id=recip,
        email_type=type_str,
        scheduled_for=datetime.now(timezone.utc),
        status="sent",
        attempts=1,
        sent_at=datetime.now(timezone.utc)
    )
    db.add(record)
    
    # Fire actual email
    try:
        if type_str == "N-7":
            # assignee_name needs to be resolved; for now just pass ID string or minimal
            await email_service.send_missed_deadline_alert(email_addr, task.title, "Assignee")
        else:
            await email_service.send_deadline_reminder(email_addr, task.title, hours)
        await db.commit()
    except Exception as e:
        record.status = "failed"
        record.last_error = str(e)
        await db.commit()

async def cancel_task_emails(db, task_id) -> None:
    """T7.4 logic: Cancel reminders when task updated/done."""
    stmt = select(ScheduledEmail).where(
        ScheduledEmail.task_id == task_id, 
        ScheduledEmail.status != "sent"
    )
    pending = (await db.execute(stmt)).scalars().all()
    for p in pending:
        p.status = "cancelled"
    await db.commit()

async def cancel_workspace_emails(db, workspace_id) -> None:
    """T7.4 logic: Cancel all workspace reminders."""
    stmt = select(ScheduledEmail).where(
        ScheduledEmail.workspace_id == workspace_id,
        ScheduledEmail.status != "sent"
    )
    pending = (await db.execute(stmt)).scalars().all()
    for p in pending:
        p.status = "cancelled"
    await db.commit()
