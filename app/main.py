from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.config.logging import configure_logging
from app.config.settings import settings
import logging

configure_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

    # Startup
    logger.info("Application starting")
    logger.info("Embedding Model: %s", settings.EMBEDDING_MODEL)
    logger.info("LLM Model: %s", settings.MODEL_NAME)
    yield

    # Shutdown


app = FastAPI(
    title="Financial Report Analyst",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "application": "Financial Report Analyst",
        "version": "1.0.0",
        "status": "running",
    }
