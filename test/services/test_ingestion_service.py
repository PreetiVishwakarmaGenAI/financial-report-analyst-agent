import uuid

from app.services.document_service import DocumentService
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService
from app.services.ingestion_service import IngestionService


def test_pdf_ingestion():

    embedding_service = EmbeddingService()

    vector_store = VectorStoreService(
        embedding_service
    )

    # Start with a clean collection
    vector_store.reset_collection()

    ingestion_service = IngestionService(
        document_service=DocumentService(),
        chunking_service=ChunkingService(),
        vector_store_service=vector_store,
    )

    result = ingestion_service.ingest(
        "test/test_data/sample.pdf"
    )

    assert result["status"] == "Indexed"

    assert result["pages"] > 0

    assert result["chunks"] > 0

    assert vector_store.document_count() == result["chunks"]