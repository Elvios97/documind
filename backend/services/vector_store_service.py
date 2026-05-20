import os
from pathlib import Path
from typing import Any

from models.chunk import RetrievedChunk, TextChunk
from models.errors import AppError


BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent
DEFAULT_CHROMA_DIR = PROJECT_DIR / "local_data" / "chroma"
DEFAULT_COLLECTION_NAME = "documind_chunks"


def get_chroma_dir() -> Path:
    """Liefert den lokalen Speicherort fuer ChromaDB-Daten."""
    configured_dir = os.getenv("DOCUMIND_CHROMA_DIR")
    if configured_dir:
        return Path(configured_dir)
    return DEFAULT_CHROMA_DIR


def get_vector_collection(collection_name: str = DEFAULT_COLLECTION_NAME) -> Any:
    """Erstellt oder laedt die lokale ChromaDB Collection."""
    try:
        import chromadb
    except ImportError as exc:
        raise AppError(
            500,
            "ChromaDB ist nicht installiert. Fuehre im Backend aus: pip install -r requirements.txt",
        ) from exc

    chroma_dir = get_chroma_dir()
    chroma_dir.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(chroma_dir))
    return client.get_or_create_collection(name=collection_name)


def upsert_chunks(
    chunks: list[TextChunk],
    embeddings: list[list[float]],
    collection: Any | None = None,
) -> int:
    """Speichert Chunks mit ihren Embeddings in ChromaDB."""
    _validate_chunks_and_embeddings(chunks, embeddings)
    target_collection = collection or get_vector_collection()

    target_collection.upsert(
        ids=[chunk.chunk_id for chunk in chunks],
        embeddings=embeddings,
        documents=[chunk.text for chunk in chunks],
        metadatas=[_chunk_metadata(chunk) for chunk in chunks],
    )

    return len(chunks)


def query_chunks(
    query_embedding: list[float],
    top_k: int = 5,
    document_id: str | None = None,
    collection: Any | None = None,
) -> list[RetrievedChunk]:
    """Sucht relevante Chunks anhand eines Query-Embeddings."""
    _validate_query_settings(query_embedding, top_k)
    target_collection = collection or get_vector_collection()

    where_filter = {"document_id": document_id} if document_id else None
    query_kwargs: dict[str, Any] = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
    }
    if where_filter:
        query_kwargs["where"] = where_filter

    result = target_collection.query(**query_kwargs)
    return _parse_query_result(result)


def _validate_chunks_and_embeddings(chunks: list[TextChunk], embeddings: list[list[float]]) -> None:
    if not chunks:
        raise AppError(400, "Es muss mindestens ein Chunk gespeichert werden.")

    if len(chunks) != len(embeddings):
        raise AppError(400, "Anzahl der Chunks und Embeddings muss uebereinstimmen.")

    for embedding in embeddings:
        _validate_embedding(embedding)


def _validate_query_settings(query_embedding: list[float], top_k: int) -> None:
    _validate_embedding(query_embedding)

    if top_k <= 0:
        raise AppError(400, "top_k muss groesser als 0 sein.")


def _validate_embedding(embedding: list[float]) -> None:
    if not embedding:
        raise AppError(400, "Embedding darf nicht leer sein.")

    if not all(isinstance(value, int | float) for value in embedding):
        raise AppError(400, "Embedding darf nur numerische Werte enthalten.")


def _chunk_metadata(chunk: TextChunk) -> dict[str, int | str]:
    return {
        "document_id": chunk.document_id,
        "chunk_id": chunk.chunk_id,
        "chunk_index": chunk.chunk_index,
        "page_number": chunk.page_number,
    }


def _parse_query_result(result: dict[str, Any]) -> list[RetrievedChunk]:
    ids = _first_result_list(result, "ids")
    documents = _first_result_list(result, "documents")
    metadatas = _first_result_list(result, "metadatas")
    distances = _first_result_list(result, "distances", required=False)

    chunks: list[RetrievedChunk] = []
    for index, chunk_id in enumerate(ids):
        metadata = metadatas[index] if index < len(metadatas) and isinstance(metadatas[index], dict) else {}
        text = documents[index] if index < len(documents) else ""
        distance = distances[index] if index < len(distances) else None

        chunks.append(
            RetrievedChunk(
                document_id=str(metadata.get("document_id", "")),
                chunk_id=str(metadata.get("chunk_id", chunk_id)),
                chunk_index=int(metadata.get("chunk_index", index)),
                page_number=int(metadata.get("page_number", 1)),
                text=str(text),
                score=_distance_to_score(distance),
            )
        )

    return chunks


def _first_result_list(result: dict[str, Any], key: str, required: bool = True) -> list[Any]:
    raw_value = result.get(key)
    if raw_value is None and not required:
        return []

    if not isinstance(raw_value, list) or not raw_value:
        if required:
            raise AppError(502, f"ChromaDB hat kein gueltiges Feld '{key}' geliefert.")
        return []

    first_value = raw_value[0]
    if not isinstance(first_value, list):
        raise AppError(502, f"ChromaDB hat kein gueltiges Feld '{key}' geliefert.")

    return first_value


def _distance_to_score(distance: Any) -> float | None:
    if not isinstance(distance, int | float):
        return None

    score = 1.0 - float(distance)
    return max(0.0, min(1.0, score))
