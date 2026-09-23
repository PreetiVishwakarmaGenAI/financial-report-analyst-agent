import logging
from app.tools.base_tool import BaseTool
from app.graph.state import AgentState
from app.services.retrieval_service import RetrievalService


logger = logging.getLogger(__name__)

class RetrievalTool(BaseTool):
    @property
    def name(self):
        return "retrieval"

    @property
    def description(self):
        return (
            "Retrieve information from uploaded financial reports."
        )

    def __init__(self, retrieval_service: RetrievalService = None):
        self.retrieval_service = retrieval_service

    def run(self, state: AgentState) -> AgentState:
        """
        Execute the retrieval tool.
        """
        logger.info("Retrieval Tool started.")

        retrieved_chunks = []

        queries = state.retrieval_queries

        if state.retry_count > 0:

            logger.info(
                "Refining retrieval using reflection feedback."
            )

            logger.info(
                "Feedback: %s",
                state.reflection_feedback,
            )

            queries = self._build_retry_queries(
                state
            )
        
        for query in queries:

            logger.debug(
                "Retrieving chunks for retrieval query: %s",
                query,
            )
            try:
                chunks = self.retrieval_service.retrieve(
                    query=query,
                    document_id=state.document_id,
                    top_k=state.top_k,
                )
            except Exception as e:
                logger.error(
                    "Error occurred while retrieving chunks for query '%s': %s",
                    query,
                    str(e),
                )
                raise

            retrieved_chunks.extend(chunks)

        state.retrieved_chunks = self._deduplicate_chunks(
            retrieved_chunks
        )

        logger.info(
            "Retrieval Tool completed. Retrieved %d unique chunks.",
            len(state.retrieved_chunks),
        )

        return state

    def _build_retry_queries(self, state: AgentState) -> list[str]:

        feedback = state.reflection_feedback

        return [
            f"""
            Original research question:
            {query}

            Reflection feedback:
            {feedback}

            Perform a more targeted search that addresses
            the reflection feedback.
            """
            for query in state.retrieval_queries
        ]

    @staticmethod
    def _deduplicate_chunks(chunks):
        """
        Remove duplicate chunks based on chunk_id.
        """

        unique_chunks = {}

        for chunk in chunks:
            unique_chunks[chunk.chunk_id] = chunk

        return list(unique_chunks.values())
