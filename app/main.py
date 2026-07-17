from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.config.logging import configure_logging
from app.config.settings import settings

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """

    # Startup
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