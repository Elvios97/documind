import pytest

from models.chunk import TextChunk
from models.errors import AppError
from services.vector_store_service import query_chunks, upsert_chunks


class FakeCollection:
    def __init__(self, query_result: dict | None = None) -> None:
        self.upsert_payload: dict | None = None
        self.query_payload: dict | None = None
        self.query_result = query_result or {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

    def upsert(self, **kwargs) -> None:
        self.upsert_payload = kwargs

    def query(self, **kwargs) -> dict:
        self.query_payload = kwargs
        return self.query_result


def test_upsert_chunks_writes_documents_embeddings_and_metadata() -> None:
    collection = FakeCollection()
    chunks = [
        TextChunk(
            document_id="doc-test",
            chunk_id="doc-test-p0001-c0000",
            chunk_index=0,
            page_number=1,
            text="Erster Chunk",
        ),
        TextChunk(
            document_id="doc-test",
            chunk_id="doc-test-p0002-c0000",
            chunk_index=1,
            page_number=2,
            text="Zweiter Chunk",
        ),
    ]

    count = upsert_chunks(chunks, embeddings=[[0.1, 0.2], [0.3, 0.4]], collection=collection)

    assert count == 2
    assert collection.upsert_payload == {
        "ids": ["doc-test-p0001-c0000", "doc-test-p0002-c0000"],
        "embeddings": [[0.1, 0.2], [0.3, 0.4]],
        "documents": ["Erster Chunk", "Zweiter Chunk"],
        "metadatas": [
            {
                "document_id": "doc-test",
                "chunk_id": "doc-test-p0001-c0000",
                "chunk_index": 0,
                "page_number": 1,
            },
            {
                "document_id": "doc-test",
                "chunk_id": "doc-test-p0002-c0000",
                "chunk_index": 1,
                "page_number": 2,
            },
        ],
    }


def test_upsert_chunks_rejects_mismatched_embeddings() -> None:
    chunks = [
        TextChunk(
            document_id="doc-test",
            chunk_id="doc-test-p0001-c0000",
            chunk_index=0,
            page_number=1,
            text="Erster Chunk",
        )
    ]

    with pytest.raises(AppError, match="uebereinstimmen"):
        upsert_chunks(chunks, embeddings=[], collection=FakeCollection())


def test_query_chunks_returns_retrieved_chunks_with_scores() -> None:
    collection = FakeCollection(
        query_result={
            "ids": [["doc-test-p0002-c0000"]],
            "documents": [["Gefundener Chunk"]],
            "metadatas": [
                [
                    {
                        "document_id": "doc-test",
                        "chunk_id": "doc-test-p0002-c0000",
                        "chunk_index": 1,
                        "page_number": 2,
                    }
                ]
            ],
            "distances": [[0.18]],
        }
    )

    chunks = query_chunks(
        query_embedding=[0.1, 0.2],
        top_k=3,
        document_id="doc-test",
        collection=collection,
    )

    assert collection.query_payload == {
        "query_embeddings": [[0.1, 0.2]],
        "n_results": 3,
        "where": {"document_id": "doc-test"},
    }
    assert len(chunks) == 1
    assert chunks[0].document_id == "doc-test"
    assert chunks[0].chunk_id == "doc-test-p0002-c0000"
    assert chunks[0].chunk_index == 1
    assert chunks[0].page_number == 2
    assert chunks[0].text == "Gefundener Chunk"
    assert chunks[0].score == pytest.approx(0.82)


def test_query_chunks_rejects_invalid_settings() -> None:
    with pytest.raises(AppError, match="Embedding"):
        query_chunks([], collection=FakeCollection())

    with pytest.raises(AppError, match="top_k"):
        query_chunks([0.1, 0.2], top_k=0, collection=FakeCollection())


def test_query_chunks_filters_multiple_documents() -> None:
    collection = FakeCollection(query_result={"ids": [[]], "documents": [[]], "metadatas": [[]]})

    chunks = query_chunks(
        [0.1, 0.2],
        document_ids=["doc-a", "doc-b"],
        collection=collection,
    )

    assert chunks == []
    assert collection.query_payload["where"] == {"document_id": {"$in": ["doc-a", "doc-b"]}}
