from contextlib import asynccontextmanager
import logging
import os

from fastapi import FastAPI, utils

from app.api.routes import router
from app.config.logging import configure_logging
from app.config.settings import settings

from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService

from app.agents.planner_agent import PlannerAgent
from app.agents.researcher_agent import ResearcherAgent
from app.agents.synthesizer_agent import SynthesizerAgent

from app.graph.workflow import create_workflow

from dotenv import load_dotenv

from app.tools.tool_registry import ToolRegistry

load_dotenv()

configure_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

    try:
        logger.info("Application starting...")

        # ------------------------------------------------------------------
        # Embedding Service
        # ------------------------------------------------------------------
        logger.info(
            "Loading Embedding Model: %s",
            settings.EMBEDDING_MODEL,
        )

        app.state.embedding_service = EmbeddingService()

        logger.info("Embedding model loaded successfully.")

        # ------------------------------------------------------------------
        # Vector Store
        # ------------------------------------------------------------------
        logger.info("Initializing ChromaDB...")

        app.state.vector_store = VectorStoreService(
            app.state.embedding_service
        )

        logger.info(
            "ChromaDB initialized with collection '%s'",
            settings.VECTOR_COLLECTION_NAME,
        )

        # ------------------------------------------------------------------
        # Retrieval Service
        # ------------------------------------------------------------------
        logger.info("Initializing Retrieval Service...")

        app.state.retrieval_service = RetrievalService(
            app.state.vector_store
        )

        logger.info("Retrieval Service initialized successfully.")

        # ------------------------------------------------------------------
        # LLM Service
        # ------------------------------------------------------------------
        logger.info("Initializing LLM Service...")

        app.state.llm_service = LLMService()

        logger.info("LLM Service initialized successfully.")

        # ------------------------------------------------------------------
        # Graph Workflow
        # ------------------------------------------------------------------

        app.state.workflow = create_workflow(
            llm_service=app.state.llm_service,
            retrieval_service=app.state.retrieval_service,
        )

        logger.info("Graph workflow initialized successfully.")

        # ------------------------------------------------------------------
        # Configuration
        # ------------------------------------------------------------------
        logger.info(
            "Planner Model      : %s",
            settings.PLANNER_MODEL,
        )

        logger.info(
            "Researcher Model   : %s",
            settings.RESEARCHER_MODEL,
        )

        logger.info(
            "Synthesizer Model  : %s",
            settings.SYNTHESIZER_MODEL,
        )

        logger.info("Application startup completed successfully.")

        yield

    except Exception:
        logger.exception("Application startup failed.")
        raise

    finally:
        logger.info("Application shutting down.")


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