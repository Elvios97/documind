from typing import Any

from models.chunk import DocumentIndexResult
from models.document import StoredDocument
from models.errors import AppError
from services.chunking_service import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE, chunk_document_pages
from services.embedding_service import embed_texts
from services.vector_store_service import delete_document_chunks, upsert_chunks


async def index_document(
    document: StoredDocument,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    collection: Any | None = None,
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

    embeddings, embedding_model = await embed_texts([chunk.text for chunk in chunks])
    try:
        stored_count = upsert_chunks(chunks, embeddings, collection=collection)
    except Exception:
        # Eine teilweise Speicherung darf keinen verwaisten PDF-Text im Vector Store lassen.
        try:
            delete_document_chunks(document.document_id, collection=collection)
        except Exception:
            pass
        raise

    return DocumentIndexResult(
        document_id=document.document_id,
        chunk_count=stored_count,
        embedding_model=embedding_model,
    )
