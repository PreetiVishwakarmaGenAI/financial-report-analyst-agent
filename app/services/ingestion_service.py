import logging
import uuid
from pathlib import Path
from typing import Dict

from app.services.document_service import DocumentService
from app.services.chunking_service import ChunkingService
from app.services.vector_store_service import VectorStoreService

logger = logging.getLogger(__name__)


class IngestionService:
    """
    Service responsible for orchestrating the complete
    document ingestion workflow.

    Workflow:
        PDF
          │
          ▼
    DocumentService
          │
          ▼
    ChunkingService
          │
          ▼
    VectorStoreService
          │
          ▼
       ChromaDB
    """

    def __init__(
        self,
        document_service: DocumentService,
        chunking_service: ChunkingService,
        vector_store_service: VectorStoreService,
    ) -> None:

        self.document_service = document_service
        self.chunking_service = chunking_service
        self.vector_store_service = vector_store_service

    def ingest(self, file_path: str) -> Dict:
        """
        Ingest a PDF document into the vector database.

        Args:
            file_path: Path to the PDF.

        Returns:
            Dictionary containing ingestion statistics.
        """

        logger.info("Starting ingestion for %s", file_path)

        document_id = str(uuid.uuid4())
        filename = Path(file_path).name

        # Step 1 - Extract PDF
        pages = self.document_service.extract_pdf(file_path)

        # Step 2 - Create Chunks
        chunks = self.chunking_service.create_chunks(
            pages=pages,
            document_id=document_id,
            filename=filename,
        )


        # Step 3 - Prepare data for Chroma
        ids = [chunk["id"] for chunk in chunks]

        documents = [
            chunk["text"]
            for chunk in chunks
        ]

        metadatas = [
            chunk["metadata"]
            for chunk in chunks
        ]

        # Step 4 - Store vectors
        self.vector_store_service.add_documents(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        logger.info(
            "Successfully indexed '%s' into ChromaDB",
            filename,
        )

        return {
            "document_id": document_id,
            "filename": filename,
            "pages": len(pages),
            "chunks": len(chunks),
            "status": "Indexed",
        }