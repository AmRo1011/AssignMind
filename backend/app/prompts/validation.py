"""
AssignMind — Prompt Validation and Keywords

Contains regex patterns for detecting direct answers, 
fallback responses, and standard system prompts.
"""

import re

# Regex patterns to catch "The answer is..." or direct code/solutions
VIOLATION_PATTERNS = [
    re.compile(r"(?i)\bthe (exact )?answer is\b"),
    re.compile(r"(?i)\bhere is the solution\b"),
    re.compile(r"(?i)\bthe solution is\b"),
    re.compile(r"(?i)\bjust copy this\b"),
]

# Fallback response for when AI refuses to stop giving direct answers
VALIDATION_FALLBACK = (
    "I'm sorry, but I cannot provide direct answers or solutions to "
    "this assignment due to AssignMind's guided learning policy. "
    "However, I can help you understand the core concepts. "
    "Which part are you struggling with?"
)

SYSTEM_GUARDRAILS = """
<guided_learning_policy>
You are an AI assistant designed strictly for guided learning.
NON-NEGOTIABLE RULES:
1. You must NEVER give direct answers, complete code solutions, or finalize written essays.
2. If the user asks for a direct answer, pivot the response into a guiding question.
3. Help the user break down the problem structurally.
4. Your goal is to scaffold the user's thinking process, not perform the work.
</guided_learning_policy>
"""

def contains_violation(text: str) -> bool:
    """Check text against violation heuristics."""
    for pattern in VIOLATION_PATTERNS:
        if pattern.search(text):
            return True
    return False
