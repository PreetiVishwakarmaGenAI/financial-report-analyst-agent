import logging
from pathlib import Path
from typing import Dict, List

from pypdf import PdfReader

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service responsible for reading PDF documents.

    Responsibilities:
    - Validate PDF
    - Extract text page by page
    - Return extracted pages with metadata

    This service DOES NOT:
    - Chunk text
    - Generate embeddings
    - Store vectors
    """

    def extract_pdf(self, file_path: str) -> List[Dict]:
        """
        Extract text from a PDF file.

        Args:
            file_path: Path to the PDF.

        Returns:
            List of dictionaries containing page number and text.

            Example:
            [
                {
                    "page": 1,
                    "text": "This is page one..."
                },
                {
                    "page": 2,
                    "text": "This is page two..."
                }
            ]
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        if path.suffix.lower() != ".pdf":
            raise ValueError("Only PDF files are supported.")

        logger.info("Reading PDF: %s", file_path)

        reader = PdfReader(file_path)

        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text()

                pages.append(
                    {
                        "page": page_number,
                        "text": text.strip() if text else "",
                    }
                )

            except Exception:
                logger.exception(
                    "Failed to extract text from page %d",
                    page_number,
                )
                raise

        logger.info(
            "Successfully extracted %d pages from %s",
            len(pages),
            path.name,
        )

        return pages