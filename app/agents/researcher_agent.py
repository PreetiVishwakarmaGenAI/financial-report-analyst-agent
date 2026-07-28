import logging

from app.graph.state import AgentState
from app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)


class ResearcherAgent:
    """
    Researcher Agent responsible for retrieving
    relevant evidence from the vector store.
    """

    def __init__(
        self,
        retrieval_service: RetrievalService,
    ):
        self.retrieval_service = retrieval_service

    def execute(
        self,
        state: AgentState,
    ) -> AgentState:
        """
        Retrieve relevant chunks for all retrieval_queries.
        """

        logger.info("Researcher Agent started.")

        retrieved_chunks = []

        for question in state.retrieval_queries:

            logger.debug(
                "Retrieving chunks for retrieval query: %s",
                question,
            )

            chunks = self.retrieval_service.retrieve(
                query=question,
                document_id=state.document_id,
                top_k=state.top_k,
            )

            retrieved_chunks.extend(chunks)

        state.retrieved_chunks = self._deduplicate_chunks(
            retrieved_chunks
        )

        logger.info(
            "Researcher completed. Retrieved %d unique chunks.",
            len(state.retrieved_chunks),
        )

        return state

    @staticmethod
    def _deduplicate_chunks(chunks):
        """
        Remove duplicate chunks based on chunk_id.
        """

        unique_chunks = {}

        for chunk in chunks:
            unique_chunks[chunk.chunk_id] = chunk

        return list(unique_chunks.values())