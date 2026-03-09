"""
AssignMind — Email Service

Handles transactional emails via Resend with inline HTML templates.
"""

import structlog
import resend
from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()
resend.api_key = settings.resend_api_key

_BRAND = '<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">' \
         '<h2 style="color: #4A90E2;">AssignMind</h2>'

async def _send(to: str, subject: str, html: str) -> None:
    if settings.app_env == "test": return
    try:
        from_email = "AssignMind <onboarding@resend.dev>"
        # Optional: For Resend v2+, args might differ, typically:
        resend.Emails.send({
            "from": from_email, "to": [to], "subject": subject, "html": html
        })
    except Exception as e:
        logger.error("email_delivery_failed", email=to, error=str(e))

async def send_welcome_verification(email: str, name: str) -> None:
    """N-1: Account registration (verification)"""
    html = f"{_BRAND}<p>Hi {name},</p><p>Welcome to AssignMind! Please verify your phone number to activate your account and receive your free credits.</p></div>"
    await _send(email, "Welcome to AssignMind - Please Verify", html)

async def send_account_activated(email: str, name: str, credits: int) -> None:
    """N-2: Account activation (welcome)"""
    html = f"{_BRAND}<p>Hi {name},</p><p>Your account is now fully active! We've credited you with {credits} free credits to get started.</p></div>"
    await _send(email, "Account Activated - AssignMind", html)

async def send_credits_purchased(email: str, name: str, amount: int) -> None:
    """N-3: Credits purchase confirmation"""
    html = f"{_BRAND}<p>Hi {name},</p><p>Thank you for your purchase! {amount} credits have been added to your balance.</p></div>"
    await _send(email, f"Receipt: {amount} Credits Added", html)

async def send_workspace_invitation(email: str, inviter_name: str, ws_title: str) -> None:
    """N-4: Workspace invitation"""
    link = f"{settings.frontend_url}/dashboard"
    html = f"{_BRAND}<p>Hello,</p><p>{inviter_name} has invited you to join the workspace <strong>{ws_title}</strong>.</p><a href='{link}'>View Invitation</a></div>"
    await _send(email, f"Invitation to {ws_title}", html)

async def send_deadline_reminder(email: str, task_title: str, hours: int) -> None:
    """N-5 & N-6: Deadline reminders (72h and 24h)"""
    html = f"{_BRAND}<p>Reminder:</p><p>Your task <strong>{task_title}</strong> is due in {hours} hours. Please ensure it is completed on time.</p></div>"
    await _send(email, f"Task Due in {hours} Hours", html)

async def send_missed_deadline_alert(email: str, task_title: str, assignee_name: str) -> None:
    """N-7: Missed deadline alert (Team Leader)"""
    html = f"{_BRAND}<p>Alert:</p><p>The task <strong>{task_title}</strong> assigned to {assignee_name} has missed its deadline.</p></div>"
    await _send(email, f"Missed Deadline: {task_title}", html)
