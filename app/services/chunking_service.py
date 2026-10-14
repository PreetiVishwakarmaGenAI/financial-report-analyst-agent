import logging
import uuid
from typing import Dict, List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.settings import settings

logger = logging.getLogger(__name__)


class ChunkingService:
    """
    Service responsible for splitting extracted document text
    into smaller chunks while preserving metadata.
    """

    def __init__(self) -> None:

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )

    
    def create_chunks(
        self,
        pages: List[Dict],
        document_id: str,
        filename: str,
    ) -> List[Dict]:
        """Split extracted PDF pages into chunks with metadata."""

        chunks = []

        logger.info(
            "Starting chunking for %s: %d pages received",
            filename,
            len(pages),
        )

        for page in pages:
            page_number = page.get("page", "unknown")
            page_text = page.get("text", "")

            if not isinstance(page_text, str):
                logger.warning(
                    "Skipping page %s: expected string, got %s",
                    page_number,
                    type(page_text).__name__,
                )
                continue

            page_text = page_text.strip()

            if not page_text:
                logger.warning(
                    "Page %s has no extractable text in %s",
                    page_number,
                    filename,
                )
                continue

            split_text = self.text_splitter.split_text(page_text)

            logger.debug(
                "Page %s: extracted_chars=%d, chunks=%d",
                page_number,
                len(page_text),
                len(split_text),
            )

            for chunk_number, chunk in enumerate(split_text, start=1):
                if not chunk.strip():
                    continue

                chunks.append({
                    "id": str(uuid.uuid4()),
                    "text": chunk,
                    "metadata": {
                        "document_id": document_id,
                        "filename": filename,
                        "page": page_number,
                        "chunk": chunk_number,
                    },
                })

        logger.info(
            "Chunking completed for %s: %d chunks created",
            filename,
            len(chunks),
        )

        return chunks
