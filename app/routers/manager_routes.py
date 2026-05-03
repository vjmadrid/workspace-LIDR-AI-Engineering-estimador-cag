import logging

from fastapi import APIRouter

from app.config import get_settings
from app.constants import manager_constants

logger = logging.getLogger(__name__)

router = APIRouter(prefix=manager_constants.ROOT_ENDPOINT)


@router.get(manager_constants.HEALTH_ENDPOINT, name="health")
def health_manager():
    """
    Handles HTTP requests to:
    * /manager/health
    """
    logger.info("Health check endpoint called")
    settings = get_settings()
    return {
        "success": True,
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.APP_ENV,
    }
