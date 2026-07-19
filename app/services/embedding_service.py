import logging
from typing import List
from sentence_transformers import SentenceTransformer
from app.config.settings import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service responsible for generating text embeddings.

    This class abstracts the underlying embedding model so that the rest
    of the application does not depend directly on SentenceTransformer.
    """

    def __init__(self) -> None:
        self.model_name = settings.EMBEDDING_MODEL
        self.model = self._load_model()

    def _load_model(self) -> SentenceTransformer:
        """
        Load the embedding model.
        Returns:
            SentenceTransformer: Loaded embedding model.
        """
        try:
            logger.info("Loading embedding model: %s", self.model_name)

            model = SentenceTransformer(self.model_name)

            logger.info("Embedding model loaded successfully.")

            return model

        except Exception:
            logger.exception("Failed to load embedding model.")
            raise

    def embed_query(self, query: str) -> List[float]:
        """
        Generate an embedding for a single query.

        Args:
            query: Input query.

        Returns:
            List[float]: Embedding vector.
        """
        return self.model.encode(query).tolist()

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.

        Args:
            documents: List of text documents.

        Returns:
            List[List[float]]: List of embedding vectors.
        """
        return self.model.encode(documents).tolist()

    @property
    def embedding_dimension(self) -> int:
        """
        Returns the embedding dimension of the loaded model.
        """
        return self.model.get_sentence_embedding_dimension()
