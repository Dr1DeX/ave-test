import sys
import uvicorn
from logging import getLogger

from app.server import app
from core.config import config
from core.utils.logging import LOGGING

logger = getLogger(__name__)


def start():
    if len(sys.argv) < 2:
        logger.error("No target specified")
    target = sys.argv[1]

    if target == "app":
        uvicorn.run(
            app,
            host=config.APP_HOST,
            port=config.APP_PORT,
            log_config=LOGGING,
            reload=False,
            workers=1,
        )


if __name__ == "__main__":
    start()
