"""
AssignMind — Task Distribution Prompt

Template for generating a kanban-style task breakdown for an assignment.
"""

from app.prompts.validation import SYSTEM_GUARDRAILS

TASK_DISTRIBUTION_SYSTEM = (
    f"{SYSTEM_GUARDRAILS}\n\n"
    "You are an expert project manager. Break down the provided assignment "
    "into a sensible sequence of discrete tasks. "
    "Consider the available team members if provided. "
    "Do not produce direct assignment solutions. "
    "Output raw JSON without markdown."
)

TASK_DISTRIBUTION_USER = """
Assignment details:
<assignment_document>
{summary}
</assignment_document>

Available Members:
{members}

Output a list of tasks. 
Schema:
[
  {{
    "title": "Task name",
    "description": "Task details (guided learning, no solutions)",
    "assigned_to": "<optional member ID if applicable, or null>"
  }}
]
"""
