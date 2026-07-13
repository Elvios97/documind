import os
from collections.abc import Callable
from typing import Any

from models.chunk import DocumentIndexResult
from models.document import StoredDocument
from models.errors import AppError
from services.chunking_service import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE, chunk_document_pages
from services.embedding_service import embed_texts
from services.vector_store_service import delete_document_chunks, upsert_chunks


DEFAULT_EMBEDDING_BATCH_SIZE = 16


def get_embedding_batch_size() -> int:
    try:
        batch_size = int(os.getenv("DOCUMIND_EMBEDDING_BATCH_SIZE", DEFAULT_EMBEDDING_BATCH_SIZE))
    except ValueError as exc:
        raise AppError(500, "DOCUMIND_EMBEDDING_BATCH_SIZE muss eine ganze Zahl sein.") from exc
    if batch_size <= 0:
        raise AppError(500, "DOCUMIND_EMBEDDING_BATCH_SIZE muss groesser als 0 sein.")
    return batch_size


async def index_document(
    document: StoredDocument,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    collection: Any | None = None,
    batch_size: int | None = None,
    on_progress: Callable[[int, int], None] | None = None,
) -> DocumentIndexResult:
    """Erstellt Chunks, Embeddings und speichert sie im lokalen Vector Store."""
    chunks = chunk_document_pages(
        document_id=document.document_id,
        pages=document.pages,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    if not chunks:
        raise AppError(422, "Das Dokument enthaelt keine indexierbaren Text-Chunks.")

    selected_batch_size = get_embedding_batch_size() if batch_size is None else batch_size
    if selected_batch_size <= 0:
        raise AppError(400, "batch_size muss groesser als 0 sein.")

    total_chunks = len(chunks)
    completed_chunks = 0
    embedding_model = ""
    if on_progress:
        on_progress(completed_chunks, total_chunks)

    try:
        delete_document_chunks(document.document_id, collection=collection)
        for start in range(0, total_chunks, selected_batch_size):
            chunk_batch = chunks[start:start + selected_batch_size]
            embeddings, embedding_model = await embed_texts([chunk.text for chunk in chunk_batch])
            upsert_chunks(chunk_batch, embeddings, collection=collection)
            completed_chunks += len(chunk_batch)
            if on_progress:
                on_progress(completed_chunks, total_chunks)
    except Exception:
        # Eine teilweise Speicherung darf keinen verwaisten PDF-Text im Vector Store lassen.
        try:
            delete_document_chunks(document.document_id, collection=collection)
        except Exception:
            pass
        raise

    return DocumentIndexResult(
        document_id=document.document_id,
        chunk_count=completed_chunks,
        embedding_model=embedding_model,
    )
