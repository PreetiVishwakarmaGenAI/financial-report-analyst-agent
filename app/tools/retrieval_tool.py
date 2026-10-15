
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
            "Retrieve relevant information from uploaded financial "
            "reports using the original question or targeted queries "
            "provided by the Reflection Agent."
        )

    def __init__(
        self,
        retrieval_service: RetrievalService = None,
    ):
        self.retrieval_service = retrieval_service

    def run(self, state: AgentState) -> AgentState:
        """Execute initial or Reflection-directed document retrieval."""

        logger.info(
            "Retrieval Tool started. document_id=%s, retry_count=%s",
            state.document_id,
            state.retry_count,
        )

        if not self.retrieval_service:
            raise ValueError(
                "RetrievalService has not been configured."
            )

        if not state.document_id:
            raise ValueError(
                "Document retrieval requires a document_id."
            )

        # The Researcher supplies targeted queries on a retry.
        # Initial retrieval uses the Planner's queries.
        if state.additional_retrieval_queries:
            queries = self._clean_queries(
                state.additional_retrieval_queries
            )
            logger.info(
                "Using %d Reflection-directed retrieval queries.",
                len(queries),
            )
        else:
            queries = self._clean_queries(
                state.retrieval_queries
            )
            logger.info(
                "Using %d Planner-provided retrieval queries.",
                len(queries),
            )

        if not queries:
            logger.warning(
                "Retrieval skipped because no valid queries were supplied."
            )
            return state

        new_chunks = []

        for query in queries:
            logger.info(
                "Retrieving document evidence for query: %s",
                query,
            )

            try:
                chunks = self.retrieval_service.retrieve(
                    query=query,
                    document_id=state.document_id,
                    top_k=state.top_k,
                )

                if chunks:
                    new_chunks.extend(chunks)

                logger.info(
                    "Query returned %d chunks.",
                    len(chunks or []),
                )

            except Exception:
                logger.exception(
                    "Retrieval failed for query: %s",
                    query,
                )
                raise

        # Preserve evidence from earlier retrieval passes.
        existing_chunks = state.retrieved_chunks or []

        state.retrieved_chunks = self._deduplicate_chunks(
            existing_chunks + new_chunks
        )

        logger.info(
            "Retrieval completed. New chunks=%d, total unique chunks=%d.",
            len(new_chunks),
            len(state.retrieved_chunks),
        )

        return state

    @staticmethod
    def _clean_queries(queries: list[str] | None) -> list[str]:
        """Remove empty queries and duplicate query strings."""
        cleaned = []
        seen = set()

        for query in queries or []:
            if not isinstance(query, str):
                continue

            query = query.strip()

            if not query:
                continue

            key = query.casefold()

            if key not in seen:
                seen.add(key)
                cleaned.append(query)

        return cleaned

    @staticmethod
    def _deduplicate_chunks(chunks):
        """Deduplicate chunks by chunk_id while preserving order."""
        unique_chunks = {}
        chunks_without_id = []

        for chunk in chunks:
            chunk_id = getattr(chunk, "chunk_id", None)

            if chunk_id is None:
                chunks_without_id.append(chunk)
                continue

            # Keep the first occurrence so original evidence is retained.
            if chunk_id not in unique_chunks:
                unique_chunks[chunk_id] = chunk

        return list(unique_chunks.values()) + chunks_without_id
