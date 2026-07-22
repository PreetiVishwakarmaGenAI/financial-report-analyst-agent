import logging
from fastapi import APIRouter, Request

from app.schemas.query import QueryRequest
from app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/query",
    tags=["Query"],
)


@router.post("")
def query_documents(
    query_request: QueryRequest,
    request: Request,
):
    llm_service = request.app.state.llm_service
    retrieval_service = request.app.state.retrieval_service

    retrieval_result = retrieval_service.retrieve(
        document_id=query_request.document_id,
        query=query_request.query,
        top_k=query_request.top_k,
    )
    context = retrieval_service.format_context_for_llm(
            retrieval_result
        )

    answer = llm_service.answer_question(
        question=query_request.query,
        context=context,
    )

    logger.info(
        "Question answered successfully."
    )

    return {
        "question": query_request.query,
        "answer": answer,
        "citations": retrieval_result,
    }