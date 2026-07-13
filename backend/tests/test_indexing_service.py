import asyncio
from typing import Any

import pytest

import services.indexing_service as indexing_module
from models.document import StoredDocument
from models.errors import AppError
from models.pdf import PDFPageText


class FakeCollection:
    pass


def _stored_document(pages: list[PDFPageText]) -> StoredDocument:
    return StoredDocument(
        document_id="doc-test",
        file_name="test.pdf",
        page_count=len(pages),
        pages=pages,
        full_text="\n".join(page.text for page in pages).strip() or "fallback",
        created_at="2026-05-20T12:00:00+00:00",
    )


def test_index_document_chunks_embeds_and_stores(monkeypatch: pytest.MonkeyPatch) -> None:
    document = _stored_document(
        [
            PDFPageText(page_number=1, text="abcdef"),
            PDFPageText(page_number=2, text="ghijkl"),
        ]
    )
    captured_texts: list[str] = []
    captured_collection: FakeCollection | None = None
    progress_updates: list[tuple[int, int]] = []
    collection = FakeCollection()

    async def fake_embed_texts(texts: list[str]):
        captured_texts.extend(texts)
        return [[0.1, 0.2] for _ in texts], "test-embedding-model"

    def fake_upsert_chunks(chunks, embeddings, collection=None):
        nonlocal captured_collection
        captured_collection = collection
        assert [chunk.text for chunk in chunks] == ["abc", "def", "ghi", "jkl"]
        assert embeddings == [[0.1, 0.2], [0.1, 0.2], [0.1, 0.2], [0.1, 0.2]]
        return len(chunks)

    monkeypatch.setattr(indexing_module, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(indexing_module, "upsert_chunks", fake_upsert_chunks)
    monkeypatch.setattr(indexing_module, "delete_document_chunks", lambda document_id, collection=None: None)

    result = asyncio.run(
        indexing_module.index_document(
            document,
            chunk_size=3,
            chunk_overlap=0,
            collection=collection,
            batch_size=4,
            on_progress=lambda completed, total: progress_updates.append((completed, total)),
        )
    )

    assert captured_texts == ["abc", "def", "ghi", "jkl"]
    assert captured_collection is collection
    assert result.document_id == "doc-test"
    assert result.chunk_count == 4
    assert result.embedding_model == "test-embedding-model"
    assert progress_updates == [(0, 4), (4, 4)]


def test_index_document_processes_chunks_in_batches(monkeypatch: pytest.MonkeyPatch) -> None:
    document = _stored_document([PDFPageText(page_number=1, text="abcdefghijkl")])
    embedded_batches: list[list[str]] = []
    stored_batches: list[list[str]] = []

    async def fake_embed_texts(texts: list[str]):
        embedded_batches.append(texts)
        return [[0.1, 0.2] for _ in texts], "test-embedding-model"

    def fake_upsert_chunks(chunks, embeddings, collection=None):
        stored_batches.append([chunk.text for chunk in chunks])
        return len(chunks)

    monkeypatch.setattr(indexing_module, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(indexing_module, "upsert_chunks", fake_upsert_chunks)
    monkeypatch.setattr(indexing_module, "delete_document_chunks", lambda document_id, collection=None: None)

    result = asyncio.run(indexing_module.index_document(
        document, chunk_size=3, chunk_overlap=0, batch_size=2, collection=FakeCollection()
    ))

    assert embedded_batches == [["abc", "def"], ["ghi", "jkl"]]
    assert stored_batches == embedded_batches
    assert result.chunk_count == 4


def test_index_document_rejects_document_without_chunks() -> None:
    document = _stored_document([PDFPageText(page_number=1, text="   ")])

    with pytest.raises(AppError, match="keine indexierbaren"):
        asyncio.run(indexing_module.index_document(document))


def test_index_document_removes_chunks_when_vector_storage_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    document = _stored_document([PDFPageText(page_number=1, text="Text mit Chunk")])
    collection = FakeCollection()
    deleted_document_ids: list[str] = []

    async def fake_embed_texts(texts: list[str]) -> tuple[list[list[float]], str]:
        return [[0.1, 0.2] for _ in texts], "test-embedding-model"

    def failing_upsert_chunks(chunks: list[Any], embeddings: list[list[float]], collection: Any | None = None) -> int:
        raise RuntimeError("Speichern fehlgeschlagen")

    def fake_delete_document_chunks(document_id: str, collection: Any | None = None) -> None:
        deleted_document_ids.append(document_id)

    monkeypatch.setattr(indexing_module, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(indexing_module, "upsert_chunks", failing_upsert_chunks)
    monkeypatch.setattr(indexing_module, "delete_document_chunks", fake_delete_document_chunks)

    with pytest.raises(RuntimeError, match="Speichern fehlgeschlagen"):
        asyncio.run(indexing_module.index_document(document, collection=collection, batch_size=1))

    assert deleted_document_ids == ["doc-test", "doc-test"]
