"""
AssignMind — Assignment Service Tests
"""

import uuid
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.assignment_service import upload_and_analyze_assignment, _store_new_assignment_version
from app.schemas.ai import AssignmentSummary

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def mock_upload_file():
    upload = AsyncMock()
    upload.read.return_value = b"Fake Document Content That is long enough to bypass limits over 50 chars for testing."
    upload.filename = "test.txt"
    return upload

@pytest.mark.asyncio
async def test_store_new_assignment_version_increments(mock_db):
    """Test that versions increment properly when saving."""
    workspace_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    # Mock finding max version = 2
    mock_result = MagicMock()
    mock_result.scalar.return_value = 2
    mock_db.execute.return_value = mock_result
    
    summary = AssignmentSummary(
        requirements=["R1"], constraints=[], deliverables=[], deadlines=[], tools=[]
    )
    
    assignment = await _store_new_assignment_version(
        db=mock_db,
        workspace_id=workspace_id,
        user_id=user_id,
        filename="test.txt",
        raw_text="Test",
        summary=summary,
        lang="en"
    )
    
    assert assignment.version == 3
    assert assignment.original_filename == "test.txt"
    assert assignment.detected_language == "en"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
