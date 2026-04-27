import logging
from fastapi import FastAPI

# =====================
# Logging Configuration
# =====================

logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application
    This allows for better modularity and testing
    """
    app = FastAPI(
        title="Estimador CAG",
        version="0.1.0",
        description="API para generar estimaciones de proyectos de software basadas en resúmenes de reuniones.",
    )
    return app

app = create_app()

@app.get("/")
def root():
    logger.info("Execute root endpoint")
    return {"message": "Hello from estimador-cag!"}