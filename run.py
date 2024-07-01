import logging
import waitress
from app import create_app
from app.config import settings

logger = logging.getLogger(settings.name)

if __name__ == "__main__":
    app = create_app()
    logger.info("Starting %s on port %s", settings.name, settings.port)
    waitress.serve(
        app,
        host="0.0.0.0",
        port=settings.port,
        threads=settings.threads,
    )
