import logging
from typing import Dict, List, Optional

import chromadb

from app.config.settings import settings
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Service responsible for interacting with ChromaDB.

    Responsibilities:
    - Initialize ChromaDB client
    - Create/Get collection
    - Add documents
    - Perform similarity search
    """

    def __init__(self, embedding_service: EmbeddingService) -> None:
        self.embedding_service = embedding_service
        self.collection_name = settings.VECTOR_COLLECTION_NAME

        self.client = self._initialize_client()
        self.collection = self._initialize_collection()

    def _initialize_client(self) -> chromadb.PersistentClient:
        """
        Initialize the persistent ChromaDB client.
        """
        try:
            logger.info("Initializing ChromaDB client...")

            client = chromadb.PersistentClient(
                path=settings.VECTOR_DB_PATH
            )

            logger.info("ChromaDB client initialized successfully.")

            return client

        except Exception:
            logger.exception("Failed to initialize ChromaDB client.")
            raise

    def _initialize_collection(self):
        """
        Create or load the ChromaDB collection.
        """
        try:
            logger.info(
                "Loading collection '%s'...",
                self.collection_name,
            )

            collection = self.client.get_or_create_collection(
                name=self.collection_name
            )

            logger.info(
                "Collection '%s' is ready.",
                self.collection_name,
            )

            return collection

        except Exception:
            logger.exception("Failed to initialize collection.")
            raise

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
    ) -> None:
        """
        Add documents to ChromaDB.

        Embeddings are generated automatically using EmbeddingService.
        """

        embeddings = self.embedding_service.embed_documents(documents)

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        logger.info("Added %d documents to vector store.", len(documents))

    def similarity_search(
        self,
        query: str,
        n_results: int = 5,
        metadata_filter: Optional[Dict] = None,
    ):
        """
        Perform semantic similarity search.

        Args:
            query: User query.
            n_results: Number of chunks to retrieve.
            metadata_filter: Optional metadata filter
                            e.g. {"document_id": "..."}
        """

        query_embedding = self.embedding_service.embed_query(query)

        query_args = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
        }

        if metadata_filter:
            query_args["where"] = metadata_filter

        results = self.collection.query(**query_args)

        logger.info(
            "Retrieved %d similar documents.",
            n_results,
        )

        return results

    def document_count(self) -> int:
        """
        Returns the number of indexed documents.
        """
        return self.collection.count()

    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents by IDs.
        """
        self.collection.delete(ids=ids)

        logger.info("Deleted %d documents.", len(ids))

    def reset_collection(self) -> None:
        """
        Delete all documents from the collection.
        """
        self.client.delete_collection(self.collection_name)

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

        logger.info(
            "Collection '%s' has been reset.",
            self.collection_name,
        )