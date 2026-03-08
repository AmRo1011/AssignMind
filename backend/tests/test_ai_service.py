"""
AssignMind — AI Service Tests

Unit tests for AI service layer testing Language detect, validation parsing,
and JSON recovery.
"""

import json
from unittest.mock import AsyncMock, patch
import pytest

from app.services.ai_service import AIService, AIServiceError
from app.schemas.ai import AssignmentSummary
from app.prompts.validation import VALIDATION_FALLBACK

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def ai_service():
    with patch("app.services.ai_service.AsyncAnthropic") as mock_client:
        service = AIService("fake_key")
        service.client = mock_client.return_value
        return service


def test_language_detect(ai_service):
    # Valid arabic strings triggers Arabic
    assert ai_service._detect_language("هذا اختبار للنظام") == "ar"
    # English defaults
    assert ai_service._detect_language("This is a simple english text.") == "en"
    # Fallback default
    assert ai_service._detect_language("12345!@#$") == "en"

@pytest.mark.asyncio
async def test_valid_json_parsed_correctly(ai_service, mock_db):
    """Test standard json unmarshaling."""
    mock_reply = json.dumps({
        "requirements": ["Do X"],
        "constraints": ["No Y"],
        "deliverables": ["Z doc"],
        "deadlines": [],
        "tools": []
    })
    
    msg_obj = AsyncMock()
    msg_obj.text = mock_reply
    response_obj = AsyncMock()
    response_obj.content = [msg_obj]
    ai_service.client.messages.create = AsyncMock()
    ai_service.client.messages.create.return_value = response_obj
    
    with patch("app.services.ai_service.credit_service.reserve_credits", new_callable=AsyncMock), \
         patch("app.services.ai_service.credit_service.commit_credits", new_callable=AsyncMock):
             
        summary = await ai_service.analyze_assignment(mock_db, "f32d9bcd-e4c1-4b13-8a3c-1d92376f8b9e", "Assignment: Do X")
        assert summary.requirements[0] == "Do X"


@pytest.mark.asyncio
async def test_violation_triggers_retry_and_fallback(ai_service, mock_db):
    """Test 'The answer is X' causes retry, then fallback on double failure."""
    
    # Send violation both times
    msg_obj_bad = AsyncMock()
    msg_obj_bad.text = "The exact answer is 42."
    
    res_bad = AsyncMock()
    res_bad.content = [msg_obj_bad]
    
    # client returns bad payload twice
    ai_service.client.messages.create = AsyncMock()
    ai_service.client.messages.create.side_effect = [res_bad, res_bad]
    
    with patch("app.services.ai_service.credit_service.reserve_credits", new_callable=AsyncMock), \
         patch("app.services.ai_service.credit_service.commit_credits", new_callable=AsyncMock):
             
        with pytest.raises(AIServiceError, match="I'm sorry, but I cannot provide direct answers"):
            await ai_service.analyze_assignment(mock_db, "f32d9bcd-e4c1-4b13-8a3c-1d92376f8b9e", "Tell me the answer")
        
        # Verify it called the API exactly twice (1st attempt + 1 retry)
        assert ai_service.client.messages.create.call_count == 2
