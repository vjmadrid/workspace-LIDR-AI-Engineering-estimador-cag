import logging
from fastapi import FastAPI

from app.config import get_settings
from app.api.manager.routes import router as manager_router
from app.api.manager.routes import router as basic_router
from app.api.estimate.routes import router as estimation_router

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
        description="API para generar estimaciones de proyectos de software basadas en resúmenes de reuniones."
    )

    logger.info("APP_ENV: %s", settings.APP_ENV.value)

    # Include API routers
    app.include_router(manager_router)
    app.include_router(basic_router)
    app.include_router(estimation_router)

    return app