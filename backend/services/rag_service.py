import re

from models.chunk import RetrievedChunk
from models.errors import AppError
from models.document import StoredDocument
from models.rag import AnalysisMode, RagAskResponse, RagRetrieveResponse, RagSource
from services.embedding_service import embed_text
from services.ollama_service import ask_ollama
from services.rag_prompt_service import build_rag_question_prompt
from services.vector_store_service import query_chunks
from storage.document_store import load_document_text


MAX_SELECTED_DOCUMENTS = 5


async def answer_rag_question(
    document_ids: list[str],
    question: str,
    top_k: int = 5,
    mode: AnalysisMode = "ask",
) -> RagAskResponse:
    """Beantwortet eine Frage mit lokalem Retrieval und Ollama."""
    unique_document_ids, clean_question, documents_by_id, retrieved_chunks = await _retrieve_rag_context(
        document_ids,
        question,
        top_k,
    )
    document_names = {document_id: document.file_name for document_id, document in documents_by_id.items()}
    prompt = build_rag_question_prompt(
        clean_question,
        retrieved_chunks,
        mode=mode,
        document_names=document_names,
    )
    answer, model = await ask_ollama(prompt)
    sources = _sources_from_chunks(documents_by_id, retrieved_chunks)

    return RagAskResponse(
        document_ids=unique_document_ids,
        question=clean_question,
        answer=answer,
        model=model,
        mode=mode,
        sources=sources,
    )


async def retrieve_rag_sources(
    document_ids: list[str],
    question: str,
    top_k: int = 5,
) -> RagRetrieveResponse:
    """Fuehrt nur Retrieval aus, ohne eine LLM-Antwort zu erzeugen."""
    unique_document_ids, clean_question, documents_by_id, retrieved_chunks = await _retrieve_rag_context(
        document_ids,
        question,
        top_k,
    )
    return RagRetrieveResponse(
        document_ids=unique_document_ids,
        question=clean_question,
        sources=_sources_from_chunks(documents_by_id, retrieved_chunks),
    )


async def _retrieve_rag_context(
    document_ids: list[str],
    question: str,
    top_k: int,
) -> tuple[list[str], str, dict[str, StoredDocument], list[RetrievedChunk]]:
    clean_question = question.strip()
    if not clean_question:
        raise AppError(400, "Die Frage darf nicht leer sein.")

    if top_k <= 0:
        raise AppError(400, "top_k muss groesser als 0 sein.")

    unique_document_ids = list(dict.fromkeys(document_ids))
    if not unique_document_ids:
        raise AppError(400, "Waehle mindestens ein Dokument aus.")
    if len(unique_document_ids) > MAX_SELECTED_DOCUMENTS:
        raise AppError(400, f"Es koennen hoechstens {MAX_SELECTED_DOCUMENTS} Dokumente analysiert werden.")

    documents_by_id = {
        document_id: load_document_text(document_id)
        for document_id in unique_document_ids
    }
    for document in documents_by_id.values():
        if document.indexing_status == "indexing":
            raise AppError(409, f"'{document.file_name}' wird noch indexiert. Bitte versuche es gleich erneut.")
        if document.indexing_status == "failed":
            detail = document.indexing_error or "Unbekannter Indexierungsfehler."
            raise AppError(422, f"'{document.file_name}' konnte nicht indexiert werden: {detail}")
        if document.indexing_status == "cancelled":
            raise AppError(422, f"Die Indexierung von '{document.file_name}' wurde abgebrochen.")

    query_embedding, _ = await embed_text(clean_question)
    candidates = [
        chunk
        for document_id in unique_document_ids
        for chunk in query_chunks(query_embedding, top_k=max(top_k, 3), document_id=document_id)
    ]
    retrieved_chunks = _select_diverse_chunks(candidates, unique_document_ids, top_k)

    if not retrieved_chunks:
        raise AppError(422, "Es wurden keine relevanten Textstellen gefunden.")

    return unique_document_ids, clean_question, documents_by_id, retrieved_chunks


def _sources_from_chunks(
    documents_by_id: dict[str, StoredDocument],
    chunks: list[RetrievedChunk],
) -> list[RagSource]:
    return [
        _source_from_chunk(documents_by_id[chunk.document_id].file_name, chunk, source_number)
        for source_number, chunk in enumerate(chunks, start=1)
    ]


def _source_from_chunk(filename: str, chunk: RetrievedChunk, source_number: int) -> RagSource:
    return RagSource(
        document_id=chunk.document_id,
        source_number=source_number,
        filename=filename,
        page_number=chunk.page_number,
        chunk_id=chunk.chunk_id,
        score=chunk.score,
        text_preview=_text_preview(chunk.text),
    )


def _text_preview(text: str, max_length: int = 240) -> str:
    normalized_text = " ".join(text.split())
    if len(normalized_text) <= max_length:
        return normalized_text
    return f"{normalized_text[: max_length - 3].rstrip()}..."


def _select_diverse_chunks(
    candidates: list[RetrievedChunk],
    document_ids: list[str],
    top_k: int,
) -> list[RetrievedChunk]:
    """Entfernt Textduplikate und verteilt Treffer bei genug Platz ueber Dokumente."""
    ranked_candidates = sorted(candidates, key=_chunk_score, reverse=True)
    unique_candidates: list[RetrievedChunk] = []
    for candidate in ranked_candidates:
        if any(_texts_are_near_duplicates(candidate.text, existing.text) for existing in unique_candidates):
            continue
        unique_candidates.append(candidate)

    selected: list[RetrievedChunk] = []
    if top_k >= len(document_ids):
        for document_id in document_ids:
            best_for_document = next(
                (candidate for candidate in unique_candidates if candidate.document_id == document_id),
                None,
            )
            if best_for_document is not None:
                selected.append(best_for_document)

    selected_ids = {chunk.chunk_id for chunk in selected}
    for candidate in unique_candidates:
        if len(selected) >= top_k:
            break
        if candidate.chunk_id not in selected_ids:
            selected.append(candidate)
            selected_ids.add(candidate.chunk_id)

    return sorted(selected, key=_chunk_score, reverse=True)


def _chunk_score(chunk: RetrievedChunk) -> float:
    return chunk.score if chunk.score is not None else -1.0


def _texts_are_near_duplicates(first_text: str, second_text: str) -> bool:
    first_normalized = " ".join(first_text.casefold().split())
    second_normalized = " ".join(second_text.casefold().split())
    if first_normalized == second_normalized:
        return True

    first_tokens = set(re.findall(r"\w+", first_normalized))
    second_tokens = set(re.findall(r"\w+", second_normalized))
    if min(len(first_tokens), len(second_tokens)) < 5:
        return False

    union = first_tokens | second_tokens
    return bool(union) and len(first_tokens & second_tokens) / len(union) >= 0.88
