import logging
import logging.config
from app.config.settings import settings


def configure_logging() -> None:
    """Configure application-wide logging."""

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": (
                        "%(asctime)s | %(levelname)-8s | " "%(name)s | %(message)s"
                    ),
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": settings.LOG_LEVEL,
                }
            },
            "root": {
                "handlers": ["console"],
                "level": settings.LOG_LEVEL,
            },
        }
    )
