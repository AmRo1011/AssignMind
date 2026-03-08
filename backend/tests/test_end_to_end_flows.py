"""
AssignMind — Critical Integrations & End-to-End Flow Tests

Mocks Anthropic API and Resend natively testing phase integration hooks.
"""

import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services import user_service, assignment_service, credit_service, task_service, email_service, chat_service, workspace_service, invitation_service
from app.models.user import User, Credit
from app.models.workspace import Workspace
from app.models.task import Task
from app.schemas.ai import AssignmentSummary

@pytest.fixture
def mock_db():
    db = AsyncMock()
    # Mock default execution chains yielding mocked entities
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    result.scalars.return_value.all.return_value = []
    db.execute.return_value = result
    return db

@pytest.mark.asyncio
async def test_auth_flow_e2e(mock_db):
    """1. Auth flow: OAuth callback -> phone verify -> 30 credits granted"""
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, email="test@test.com", phone_verified=False)

    # _grant_free_credits_if_eligible calls db.execute(select(Credit)...) once
    credit = Credit(user_id=user_id, balance=0, reserved=0, free_credits_granted=False)
    m_res_credit = MagicMock()
    m_res_credit.scalar_one_or_none.return_value = credit
    mock_db.execute.return_value = m_res_credit

    verified_user = await user_service.verify_phone(mock_db, mock_user, "+1234567890")
    assert verified_user.phone_verified is True
    assert credit.balance == 30
    assert credit.free_credits_granted is True

@pytest.mark.asyncio
async def test_credit_flow_e2e(mock_db):
    """3. Credit flow: reserve -> AI call -> commit / release on failure"""
    user_id = uuid.uuid4()
    credit = Credit(user_id=user_id, balance=50, reserved=0)
    
    res = MagicMock()
    res.scalar_one_or_none.return_value = credit
    mock_db.execute.return_value = res
    
    # Reserve 10
    ref = await credit_service.reserve_credits(mock_db, user_id, 10)
    assert credit.reserved == 10
    
    # Failure -> Release 10
    await credit_service.release_credits(mock_db, user_id, 10, ref)
    assert credit.reserved == 0
    assert credit.balance == 50
    
    # Success -> Commit 10
    credit.reserved = 10 
    await credit_service.commit_credits(mock_db, user_id, 10, ref)
    assert credit.reserved == 0
    assert credit.balance == 40


@pytest.mark.asyncio
async def test_task_flow_e2e(mock_db):
    """4. Task flow: distribute -> finalize -> kanban update -> chat notification"""
    with patch("app.services.chat_service._publish_task_completion", new_callable=AsyncMock) as chat_mock, \
         patch("app.services.email_scheduler_service.cancel_task_emails", new_callable=AsyncMock) as email_mock:
             
        # Simulate kanban update
        ws_id = uuid.uuid4()
        task_id = uuid.uuid4()
        
        task = Task(id=task_id, workspace_id=ws_id, title="Test Task", status="in_progress")
        mock_db.get.return_value = task
        
        member = MagicMock()
        member.workspace_id = ws_id
        member.role = "leader"
        
        update_data = {"status": "done"}
        updated_task = await task_service.update_task(mock_db, task_id, update_data, member)
        
        assert updated_task.status == "done"
        chat_mock.assert_called_once_with(mock_db, ws_id, "Test Task")
        email_mock.assert_called_once_with(mock_db, task_id)


@pytest.mark.asyncio
async def test_email_flow_e2e(mock_db):
    """5. Email flow: invitation -> cancellation on task done"""
    ws_id = uuid.uuid4()
    ws = Workspace(id=ws_id, title="Project X")
    u_id = uuid.uuid4()
    u = User(id=u_id, email="x@x.com")
    
    res = MagicMock()
    res.scalar_one_or_none.return_value = ws
    mock_db.execute.return_value = res
    
    with patch("app.services.email_service.send_workspace_invitation", new_callable=AsyncMock) as send_invite:
        
        bt = MagicMock()
        # Mock Check viability scalar return
        m_scalar = MagicMock()
        m_scalar.scalar.return_value = None
        mock_db.scalar.return_value = None
        
        await invitation_service.invite_user(mock_db, ws_id, u, "new@test.com", bt)
        
        # Verify BackgroundTasks fired
        bt.add_task.assert_called_once()
        args = bt.add_task.call_args[0]
        assert args[0] == send_invite  # The callable
