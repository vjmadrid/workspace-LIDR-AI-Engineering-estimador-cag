import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers.manager_routes import router as manager_router
from app.routers.estimate_routes import router as estimation_router
from app.routers.estimate_openai_routes import router as estimation_openai_router
from app.routers.estimate_anthropic_routes import router as estimation_anthropic_router
from app.routers.estimate_llmlite import router as estimation_llmlite_router


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application
    This allows for better modularity and testing
    """

    # Load settings
    settings = get_settings()

    # Application instance
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="API para generar estimaciones de proyectos de software basadas en resúmenes de reuniones.",
    )

    logger.info("APP_ENV: %s", settings.APP_ENV.value)
    logger.info("LLM_PROVIDER: %s", settings.LLM_PROVIDER.value)
    logger.info("OpenAI Model: %s", settings.OPENAI_MODEL)
    logger.info("Anthropic Model: %s", settings.ANTHROPIC_MODEL)
    logger.info("LiteLLM Model: %s", settings.LLMLITE_MODEL)

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

    return app
