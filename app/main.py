import logging
from fastapi import FastAPI

from app.config import get_settings


# =====================
# Logging Configuration
# =====================

settings = get_settings()

logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    from app.api.manager.routes import router as manager_router

    """
    Factory function to create and configure the FastAPI application
    This allows for better modularity and testing
    """
    app = FastAPI(
        title="Estimador CAG",
        version="0.1.0",
        description="API para generar estimaciones de proyectos de software basadas en resúmenes de reuniones."
    )

    # Include API routers
    app.include_router(manager_router)

    return app

app = create_app()

logger.info("APP_ENV: %s", settings.APP_ENV.value)

@app.get("/")
def root():
    logger.info("Execute root endpoint")
    return {"message": "Hello from estimador-cag!"}