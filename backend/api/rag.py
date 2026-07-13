from fastapi import APIRouter, HTTPException

from models.errors import AppError
from models.rag import RagAskRequest, RagAskResponse, RagRetrieveRequest, RagRetrieveResponse
from services.rag_service import answer_rag_question, retrieve_rag_sources


router = APIRouter()


@router.post("/rag/ask", response_model=RagAskResponse)
async def ask_document_with_rag(request: RagAskRequest) -> RagAskResponse:
    """Beantwortet eine Frage anhand lokal gefundener RAG-Chunks."""
    try:
        return await answer_rag_question(
            document_ids=request.document_ids,
            question=request.question,
            top_k=request.top_k,
            mode=request.mode,
        )
    except AppError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Interner Fehler bei der Verarbeitung der Anfrage.") from exc


@router.post("/rag/retrieve", response_model=RagRetrieveResponse)
async def retrieve_document_sources(request: RagRetrieveRequest) -> RagRetrieveResponse:
    """Liefert Retrieval-Quellen ohne nachgelagerte LLM-Generierung."""
    try:
        return await retrieve_rag_sources(
            document_ids=request.document_ids,
            question=request.question,
            top_k=request.top_k,
        )
    except AppError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Interner Fehler beim Retrieval.") from exc
