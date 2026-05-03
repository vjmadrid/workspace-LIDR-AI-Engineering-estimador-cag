import logging

from app.app_factory import create_app

# =====================
# Logging Configuration
# =====================

logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# =====================
# Create Application
# =====================

app = create_app()
