import logging
import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from app.services.chunking_service import ChunkingService
from app.services.document_service import DocumentService
from app.services.ingestion_service import IngestionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIRECTORY = Path("data/reports")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)


@router.post("/")
async def upload_pdf(
    request: Request,
    file: UploadFile = File(...)
):
    """
    Upload and index a PDF document.
    """

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    try:

        # Save uploaded file
        file_path = UPLOAD_DIRECTORY / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info("Uploaded file saved: %s", file.filename)

        # Get services
        vector_store = request.app.state.vector_store

        ingestion_service = IngestionService(
            document_service=DocumentService(),
            chunking_service=ChunkingService(),
            vector_store_service=vector_store,
        )

        result = ingestion_service.ingest(
            str(file_path)
        )

        return result

    except Exception as ex:

        logger.exception("Upload failed")

        raise HTTPException(
            status_code=500,
            detail=str(ex),
        )