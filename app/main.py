from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.config.logging import configure_logging
from app.config.settings import settings
import logging

from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService

configure_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

    # Startup
    try:
        logger.info("Application starting")
        logger.info("Loading Embedding Model: %s", settings.EMBEDDING_MODEL)
        app.state.embedding_service = EmbeddingService()
        logger.info("Embedding model loaded Successfully")

        logger.info("Initializing ChromaDB...")
        app.state.vector_store = VectorStoreService(
            app.state.embedding_service
        )
        logger.info(
            "ChromaDB initialized with collection '%s'",
            settings.VECTOR_COLLECTION_NAME,
        )
        logger.info("LLM Model: %s", settings.MODEL_NAME)
        yield
    except Exception as e:
        logger.error("Error occurred during application startup: %s", str(e))
        raise

    # Shutdown
    logger.info("Application shutting down")

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
