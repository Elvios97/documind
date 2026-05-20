from models.chunk import RetrievedChunk
from models.errors import AppError
from models.rag import RagAskResponse, RagSource
from services.embedding_service import embed_text
from services.ollama_service import ask_ollama
from services.rag_prompt_service import build_rag_question_prompt
from services.vector_store_service import query_chunks
from storage.document_store import load_document_text


async def answer_rag_question(document_id: str, question: str, top_k: int = 5) -> RagAskResponse:
    """Beantwortet eine Frage mit lokalem Retrieval und Ollama."""
    clean_question = question.strip()
    if not clean_question:
        raise AppError(400, "Die Frage darf nicht leer sein.")

    if top_k <= 0:
        raise AppError(400, "top_k muss groesser als 0 sein.")

    document = load_document_text(document_id)
    query_embedding, _ = await embed_text(clean_question)
    retrieved_chunks = query_chunks(query_embedding, top_k=top_k, document_id=document_id)

    if not retrieved_chunks:
        raise AppError(422, "Es wurden keine relevanten Textstellen gefunden.")

    prompt = build_rag_question_prompt(clean_question, retrieved_chunks)
    answer, model = await ask_ollama(prompt)

    return RagAskResponse(
        document_id=document_id,
        question=clean_question,
        answer=answer,
        model=model,
        sources=[_source_from_chunk(document.file_name, chunk) for chunk in retrieved_chunks],
    )


def _source_from_chunk(filename: str, chunk: RetrievedChunk) -> RagSource:
    return RagSource(
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
