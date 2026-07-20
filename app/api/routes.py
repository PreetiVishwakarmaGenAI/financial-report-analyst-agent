from fastapi import APIRouter, Request
import logging
from .upload import router as upload_router
from .query import router as query_router

router = APIRouter()
logger = logging.getLogger(__name__)

router.include_router(upload_router)
router.include_router(query_router)

@router.get("/documents")
def list_documents(request: Request):
    vector_store = request.app.state.vector_store

    data = vector_store.collection.get(include=["metadatas"])

    documents = {}

    for metadata in data["metadatas"]:
        doc_id = metadata["document_id"]

        if doc_id not in documents:
            documents[doc_id] = metadata["filename"]

    return documents

@router.get("/health")
def health():
    logger.info("Health check requested")
    return {"status": "healthy"}
