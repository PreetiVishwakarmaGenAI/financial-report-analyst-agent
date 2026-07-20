from fastapi import APIRouter, Request

from app.schemas.query import QueryRequest
from app.services.retrieval_service import RetrievalService

router = APIRouter(
    prefix="/query",
    tags=["Query"],
)


@router.post("")
def query_documents(
    query_request: QueryRequest,
    request: Request,
):

    vector_store = request.app.state.vector_store

    retrieval_service = RetrievalService(
        vector_store
    )

    results = retrieval_service.retrieve(
        document_id=query_request.document_id,
        query=query_request.query,
        top_k=query_request.top_k,
    )

    return {
        "query": query_request.query,
        "results": results,
    }