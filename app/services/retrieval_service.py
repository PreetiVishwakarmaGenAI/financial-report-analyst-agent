import logging
from typing import Dict, List, Optional

from app.services.vector_store_service import VectorStoreService

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    Service responsible for retrieving relevant chunks
    from the vector database.

    Workflow:
        User Query
             │
             ▼
      Generate Embedding
             │
             ▼
      Similarity Search
             │
             ▼
      Return Top Matching Chunks
    """

    def __init__(self, vector_store_service: VectorStoreService):
        self.vector_store_service = vector_store_service

    def retrieve(
        self,
        query: str,
        document_id: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Dict]:
        """
        Retrieve the most relevant chunks for a query.

        Args:
            query: User query.
            document_id: Optional document to search within.
            top_k: Number of results.

        Returns:
            List of retrieved chunks.
        """

        logger.info(
            "Retrieving top %d chunks for query: %s",
            top_k,
            query,
        )

        metadata_filter = None

        if document_id:
            metadata_filter = {
                "document_id": document_id
            }

        results = self.vector_store_service.similarity_search(
            query=query,
            n_results=top_k,
            metadata_filter=metadata_filter,
        )

        retrieved_chunks = []

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc_id, document, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances,
        ):
            retrieved_chunks.append(
                {
                    "id": doc_id,
                    "content": document,
                    "metadata": metadata,
                    "score": 1 - distance,
                }
            )

        logger.info(
            "Retrieved %d chunks.",
            len(retrieved_chunks),
        )

        return retrieved_chunks