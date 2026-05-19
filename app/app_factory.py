import structlog
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings
from app.routers.manager_routes import router as manager_router
from app.routers.estimate_routes import router as estimation_router
from app.routers.estimate_openai_routes import router as estimation_openai_router
from app.routers.estimate_anthropic_routes import router as estimation_anthropic_router
from app.routers.estimate_llmlite_routes import router as estimation_llmlite_router
from app.routers.estimate_llmwrapper_routes import router as estimation_llmwrapper_router


def log_settings_environment_variables(settings: Settings, log) -> None:
    """Log every setting loaded from the environment configuration."""
    log.info("- Application settings loaded")

    sensitive_keywords = ("API_KEY", "PASSWORD", "SECRET", "TOKEN")
    for key, value in settings.model_dump(mode="json").items():
        if any(keyword in key.upper() for keyword in sensitive_keywords) and value:
            value = "***"
        log.info("setting_loaded", setting=key, value=value)

def configure_logging() -> None:
    """Set up structlog: JSON in production, human-readable in development."""
    settings = get_settings()

    if settings.APP_ENV == "production":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    configure_logging()
    log = structlog.get_logger()

    settings = get_settings()

    log.info("Starting the FastAPI server ...")

    # Load settings
    log.info("- Loading application settings")

    log.info("application_started", environment=settings.APP_ENV)

    # Log loaded configuration values
    log_settings_environment_variables(settings, log)

    yield
    log.info("application_shutdown")

def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application
    This allows for better modularity and testing
    """
    settings = get_settings()

    # Application instance
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="API para generar estimaciones de proyectos de software basadas en resúmenes de reuniones.",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )


    # Add CORS Support
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add API routers
    app.include_router(manager_router)
    app.include_router(estimation_router)
    app.include_router(estimation_openai_router)
    app.include_router(estimation_anthropic_router)
    app.include_router(estimation_llmlite_router)
    app.include_router(estimation_llmwrapper_router)
    return app
