import logging
from fastapi import APIRouter
from app.api.manager import constants

logger = logging.getLogger(__name__)

router = APIRouter(prefix=constants.ROOT_ENDPOINT)

@router.get(constants.HEALTH_ENDPOINT, name="health")
def health_manager():
    """
    Handles HTTP requests to:
    * /manager/health
    """
    logger.info("Health check endpoint called")
    return {"success": True}
