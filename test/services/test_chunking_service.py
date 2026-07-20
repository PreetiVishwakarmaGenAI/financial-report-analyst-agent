import uuid

from app.services.chunking_service import ChunkingService


def test_chunk_creation():

    service = ChunkingService()

    pages = [
        {
            "page": 1,
            "text": (
                "Python is an amazing programming language. "
                * 300
            )
        }
    ]

    chunks = service.create_chunks(
        pages=pages,
        document_id=str(uuid.uuid4()),
        filename="sample.pdf",
    )

    assert len(chunks) > 1

    first = chunks[0]

    assert "id" in first
    assert "text" in first
    assert "metadata" in first

    assert first["metadata"]["page"] == 1
    assert first["metadata"]["filename"] == "sample.pdf"