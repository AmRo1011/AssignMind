"""
AssignMind — Chat Service
"""

import structlog
from typing import List
from uuid import UUID
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_message import ChatMessage
from app.models.workspace_member import WorkspaceMember
from app.models.user import User
from app.schemas.chat import ChatMessageCreate
from app.utils.sanitize import sanitize_and_trim

logger = structlog.get_logger()

async def get_workspace_messages(db: AsyncSession, workspace_id: UUID, limit: int = 50, offset: int = 0) -> List[dict]:
    """Retrieve paginated chat messages reversed chronological."""
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.workspace_id == workspace_id)
        .order_by(desc(ChatMessage.created_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    messages = result.scalars().all()

    # Format output for deleted/removed users
    out = []
    for m in messages:
        sender_name = m.sender_name
        if m.sender_type == "human":
            # Check if user still in workspace
            if m.sender_id is None:
                sender_name = "[Deleted User]"
            else:
                user_stmt = select(WorkspaceMember).where(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == m.sender_id
                )
                member = (await db.execute(user_stmt)).scalar_one_or_none()
                if not member:
                    sender_name = "[Removed Member]"

        out.append({
            "id": m.id,
            "workspace_id": m.workspace_id,
            "sender_id": m.sender_id,
            "sender_type": m.sender_type,
            "sender_name": sender_name,
            "content": m.content,
            "created_at": m.created_at
        })
    return out

async def send_human_message(db: AsyncSession, workspace_id: UUID, sender: User, req: ChatMessageCreate) -> ChatMessage:
    """Send a human message into the chat, XSS sanitized."""
    clean_content = sanitize_and_trim(req.content, max_length=5000)
    if not clean_content:
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    msg = ChatMessage(
        workspace_id=workspace_id,
        sender_id=sender.id,
        sender_type="human",
        sender_name=sender.full_name,
        content=clean_content
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg

async def _publish_task_completion(db: AsyncSession, workspace_id: UUID, task_title: str) -> None:
    """Publish a supervisor message, batching if 3+ tasks completed within 5 mins."""
    now = datetime.now(timezone.utc)
    stmt = (
        select(ChatMessage)
        .where(
            ChatMessage.workspace_id == workspace_id, ChatMessage.sender_type == "supervisor",
            ChatMessage.created_at >= now - timedelta(minutes=5),
            ChatMessage.content.like("Task%completed:%")
        ).order_by(desc(ChatMessage.created_at))
    )
    msgs = (await db.execute(stmt)).scalars().all()

    if msgs and ("Tasks completed:" in msgs[0].content or len(msgs) >= 2):
        if "Tasks completed:" in msgs[0].content:
            msgs[0].content += f"\n- {task_title}"
            msgs[0].created_at = now
        else:
            c = ["Tasks completed:", f"- {task_title}"]
            for m in msgs:
                if m.content.startswith("Task completed: "):
                    c.insert(1, f"- {m.content.replace('Task completed: ', '')}")
                await db.delete(m)
            db.add(ChatMessage(
                workspace_id=workspace_id, sender_type="supervisor", 
                sender_name="Supervisor Agent", content="\n".join(c)
            ))
    else:
        db.add(ChatMessage(
            workspace_id=workspace_id, sender_type="supervisor", 
            sender_name="Supervisor Agent", content=f"Task completed: {task_title}"
        ))
    
    await db.commit()
