"""
AssignMind — AI Service Layer

Core engine mediating all OpenRouter API calls.
Enforces Guided Learning (Constitution §I), Credit accounting (§IV),
and Language detection.
"""

import json
from uuid import UUID
from typing import Any

from openai import AsyncOpenAI
import langdetect
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ai import AssignmentSummary, GeneratedTask
from app.prompts.validation import contains_violation, VALIDATION_FALLBACK
from app.prompts.assignment_analysis import get_analysis_system_prompt, ANALYSIS_USER_TEMPLATE
from app.prompts.task_distribution import TASK_DISTRIBUTION_SYSTEM, TASK_DISTRIBUTION_USER
from app.services import credit_service

logger = structlog.get_logger()

# Credit table (Constitution §IV)
COST_ANALYSIS = 10
COST_TASK_DISTRIBUTION = 5

class AIServiceError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class AIService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = "anthropic/claude-3-haiku"

    def _detect_language(self, text: str) -> str:
        """Detect language, defaulting to 'en'."""
        try:
            lang = langdetect.detect(text)
            return "ar" if lang == "ar" else "en"
        except Exception:
            return "en"

    async def _execute_with_credits(
        self, db: AsyncSession, user_id: UUID, cost: int, prompt_fn, *args
    ) -> str:
        """Reserve credits, execute AI call with retry loop, then commit."""
        await credit_service.reserve_credits(db, user_id, cost)
        try:
            response = await prompt_fn(*args)
            await credit_service.commit_credits(db, user_id, cost)
            return response
        except Exception as e:
            await credit_service.release_credits(db, user_id, cost)
            raise e

    async def _call_claude(
        self, system_prompt: str, user_content: str, is_retry: bool = False
    ) -> str:
        """Invoke Claude via OpenRouter, validate against violations, optionally retry."""
        if is_retry:
            user_content += "\n\nERROR: Do not provide a direct answer. Follow guided learning constraints strictly. Retry."
            
        res = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            max_tokens=2000,
        )
        
        reply = res.choices[0].message.content
        if not reply:
             raise AIServiceError("Empty response from AI")
        
        if contains_violation(reply):
            if is_retry:
                logger.warning("ai_violation_fallback", text=reply[:100])
                return json.dumps({"fallback": VALIDATION_FALLBACK})
            logger.warning("ai_violation_retry", text=reply[:100])
            return await self._call_claude(system_prompt, user_content, is_retry=True)
            
        return reply

    async def analyze_assignment(
        self, db: AsyncSession, user_id: UUID, content: str
    ) -> AssignmentSummary:
        """Process assignment raw text into structured JSON metadata."""
        lang = self._detect_language(content)
        system_prompt = get_analysis_system_prompt(lang)
        user_prompt = ANALYSIS_USER_TEMPLATE.format(content=content)
        
        async def call_ai():
            return await self._call_claude(system_prompt, user_prompt)

        raw_json = await self._execute_with_credits(
            db, user_id, COST_ANALYSIS, call_ai
        )
        
        try:
            data = json.loads(raw_json)
            if "fallback" in data:
                raise AIServiceError(data["fallback"])
            return AssignmentSummary(**data)
        except json.JSONDecodeError as exc:
            logger.error("json_decode_failed", error=str(exc))
            raise AIServiceError("Failed to parse document analysis.")

    async def generate_task_distribution(
        self, db: AsyncSession, user_id: UUID, outline: str, members: str
    ) -> list[GeneratedTask]:
        """Convert an assignment summary into actionable tasks."""
        system_prompt = TASK_DISTRIBUTION_SYSTEM
        user_prompt = TASK_DISTRIBUTION_USER.format(
            summary=outline, members=members
        )
        
        async def call_ai():
            return await self._call_claude(system_prompt, user_prompt)

        raw_json = await self._execute_with_credits(
            db, user_id, COST_TASK_DISTRIBUTION, call_ai
        )
        
        try:
            data = json.loads(raw_json)
            if isinstance(data, dict) and "fallback" in data:
                raise AIServiceError(data["fallback"])
            return [GeneratedTask(**task) for task in data]
        except (json.JSONDecodeError, TypeError) as exc:
            logger.error("json_decode_failed", error=str(exc))
            raise AIServiceError("Failed to parse task generation.")
