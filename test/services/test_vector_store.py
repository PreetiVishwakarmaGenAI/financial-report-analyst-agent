import uuid

from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService


def test_chromadb_store_and_search():
    """
    Verify that documents can be
    1. Store in ChromaDB
    2. Retrieve using semantic search
    """

    # Initialize services
    embedding_service = EmbeddingService()
    vector_store = VectorStoreService(embedding_service)

    # Start with clean collection
    vector_store.reset_collection()

    # Sample documents
    documents = [
        "Lion is the king of jungle.",
        "Tiger is a wild animal.",
        "Python is a programming language.",
        "FastAPI is a modern Python web framework.",
        "Delhi is the capital of India."
    ]

    ids = [str(uuid.uuid4()) for _ in documents]

    metadatas = [
        {"source": "test"} for _ in documents
    ]
    print(metadatas)

    # Store documents
    vector_store.add_documents(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    # Verify document count
    assert vector_store.document_count() == 5

    # Semantic Search
    results = vector_store.similarity_search(
        query="Which framework is used to build APIs?",
        n_results=2
    )

    print("\nSearch Results")
    print("=" * 50)

    returned_docs = results["documents"][0]
    distances = results["distances"][0]

    for doc, distance in zip(returned_docs, distances):
        print(f"Distance : {distance:.4f}")
        print(f"Document : {doc}")
        print()

    # Validation
    assert any(
        "FastAPI" in doc
        for doc in returned_docs
    )