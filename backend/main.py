"""
AssignMind Backend — FastAPI Application Entry Point

Configures the FastAPI app with:
- CORS restricted to frontend origin (no wildcard in production)
- Structured JSON logging
- Lifespan events for startup/shutdown
- Health check endpoint
"""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import check_db_connection, engine

settings = get_settings()


# ── Logging Setup ──


def _configure_logging() -> None:
    """Configure structured logging with structlog."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            (
                structlog.dev.ConsoleRenderer()
                if settings.log_format == "text"
                else structlog.processors.JSONRenderer()
            ),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


_configure_logging()
logger = structlog.get_logger()


# ── Lifespan ──


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown events."""
    await logger.ainfo(
        "application_starting",
        env=settings.app_env,
        port=settings.app_port,
    )
    
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from app.services.email_scheduler_service import process_deadline_emails
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(process_deadline_emails, "interval", minutes=5)
    scheduler.start()
    
    yield
    
    scheduler.shutdown()
    await engine.dispose()
    await logger.ainfo("application_shutdown")


# ── App Factory ──


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns a fully configured FastAPI instance with CORS,
    structured logging, and the health check endpoint.
    """
    application = FastAPI(
        title="AssignMind API",
        description="AI-powered academic team collaboration platform",
        version="0.1.0",
        docs_url="/api/docs" if not settings.is_production else None,
        redoc_url="/api/redoc" if not settings.is_production else None,
        openapi_url="/api/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    _add_cors(application)
    _add_routes(application)
    _add_exception_handlers(application)

    return application


def _add_cors(application: FastAPI) -> None:
    """
    Add CORS middleware restricted to allowed origins.

    No wildcard origins in production (Constitution §II).
    """
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins + [
            "https://assignmind.pages.dev",
            "https://www.assignmind.pages.dev",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS", "HEAD", "PUT"],
        allow_headers=["*"],
        expose_headers=["*"],
    )


def _add_routes(application: FastAPI) -> None:
    """Register all route handlers on the application."""
    from app.routers.auth import router as auth_router
    from app.routers.users import router as users_router
    from app.routers.assignments import router as assignments_router
    from app.routers.workspaces import router as workspaces_router
    from app.routers.invitations import router as invitations_router
    from app.routers.tasks import router as tasks_router
    from app.routers.chat import router as chat_router
    from app.routers.webhooks import router as webhooks_router
    from app.routers.credits import router as credits_router

    application.include_router(auth_router)
    application.include_router(users_router)
    application.include_router(assignments_router)
    application.include_router(workspaces_router)
    application.include_router(invitations_router)
    application.include_router(tasks_router)
    application.include_router(chat_router)
    application.include_router(webhooks_router)
    application.include_router(credits_router)

    application.get(
        "/api/health",
        tags=["health"],
        summary="Health Check",
    )(_health_check)


def _add_exception_handlers(application: FastAPI) -> None:
    """
    Add global exception handlers.

    All errors use standardized envelope: { "error": { "code", "message" } }
    No stack traces exposed to client (Constitution — Error Handling).
    """
    application.add_exception_handler(
        Exception,
        _global_exception_handler,
    )


# ── Health Check ──


async def _health_check() -> dict:
    """
    Health check endpoint — verifies database connectivity.

    Returns service status without exposing internal details.
    """
    db_healthy = await check_db_connection()
    status = "healthy" if db_healthy else "degraded"

    return {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "database": "connected" if db_healthy else "unreachable",
        },
    }


# ── Global Exception Handler ──


async def _global_exception_handler(request: object, exc: Exception) -> JSONResponse:
    """
    Catch unhandled exceptions and return a safe error response.

    Never exposes stack traces or internal details (Constitution).
    """
    await logger.aerror(
        "unhandled_exception",
        error_type=type(exc).__name__,
        error_message=str(exc),
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
            }
        },
    )


# ── Application Instance ──

app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=(not settings.is_production),
    )
