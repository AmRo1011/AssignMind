"""
AssignMind — Assignment Analysis Prompt

Constructs the system prompt and structured JSON requests 
to process uploaded assignment documents.
"""

from app.prompts.validation import SYSTEM_GUARDRAILS

def get_analysis_system_prompt(language: str = "en") -> str:
    """Return the system prompt customized by language."""
    base = (
        f"{SYSTEM_GUARDRAILS}\n\n"
        "You are an expert academic assignment analyzer. "
        "Your role is to deeply evaluate the following assignment text and extract its core "
        "requirements, constraints, deliverables, deadlines, and recommended tools. "
        "Always respond with a valid JSON format."
    )

    lang_instruction = (
        "Output all analysis, descriptions, and summaries in Arabic, "
        "except for technical keywords which must remain in English."
    ) if language == "ar" else (
        "Output all analysis, descriptions, and summaries in English."
    )

    return f"{base}\n{lang_instruction}"

ANALYSIS_USER_TEMPLATE = """
Analyze the following assignment document and extract a completely structured breakdown.

<assignment_document>
{content}
</assignment_document>

You must return a raw JSON object with exactly the following schema.
No markdown wrappers, no introductory text, no conversational padding—just valid JSON.

Schema:
{{
  "requirements": ["List of core student expectations"],
  "constraints": ["List of constraints like format, word count, prohibited tools"],
  "deliverables": ["List of artifacts the student must produce"],
  "deadlines": ["List of any detected deadlines or milestones, or empty list"],
  "tools": ["List of softwares, frameworks, or tools recommended/required"]
}}
"""
