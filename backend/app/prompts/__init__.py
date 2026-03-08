"""
AssignMind — Prompts Module

Stores all static prompt strings and generation functions.
"""

from .assignment_analysis import get_analysis_system_prompt, ANALYSIS_USER_TEMPLATE
from .task_distribution import TASK_DISTRIBUTION_SYSTEM, TASK_DISTRIBUTION_USER
from .validation import contains_violation, VALIDATION_FALLBACK

__all__ = [
    "get_analysis_system_prompt",
    "ANALYSIS_USER_TEMPLATE",
    "TASK_DISTRIBUTION_SYSTEM", 
    "TASK_DISTRIBUTION_USER",
    "contains_violation",
    "VALIDATION_FALLBACK"
]
