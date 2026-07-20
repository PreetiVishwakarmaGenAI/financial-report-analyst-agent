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
        """
        Split extracted pages into chunks.

        Returns

        [
            {
                "id": "...",
                "text": "...",
                "metadata": {...}
            }
        ]
        """

        chunks = []

        for page in pages:

            page_number = page["page"]
            page_text = page["text"]

            if not page_text.strip():
                continue

            split_text = self.text_splitter.split_text(page_text)

            for chunk_number, chunk in enumerate(split_text, start=1):

                chunks.append(
                    {
                        "id": str(uuid.uuid4()),
                        "text": chunk,
                        "metadata": {
                            "document_id": document_id,
                            "filename": filename,
                            "page": page_number,
                            "chunk": chunk_number,
                        },
                    }
                )

        logger.info(
            "Created %d chunks for document %s",
            len(chunks),
            filename,
        )

        return chunks