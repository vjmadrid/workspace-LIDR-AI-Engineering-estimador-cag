import logging
from fastapi import APIRouter
from app.api.manager import constants

logger = logging.getLogger(__name__)

router = APIRouter(prefix=constants.ROOT_ENDPOINT)

@router.get(constants.HEALTH_ENDPOINT, name="health")
@router.get(constants.IS_ALIVE_ENDPOINT, name="is_alive")
def health_manager():
    """
    Handles HTTP requests to:
    * /manager/health
    * /manager/isalive
    """
    logger.info("Health check endpoint called")
    return {"success": True}
