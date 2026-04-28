import logging
from fastapi import APIRouter
from app.api.manager import constants

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/basic")

@router.get("/")
def root():
    logger.info("Execute root endpoint")
    return {"message": "Hello from estimador-cag!"}


