from fastapi import APIRouter, HTTPException

from models.errors import AppError
from models.rag import RagAskRequest, RagAskResponse
from services.rag_service import answer_rag_question


router = APIRouter()


@router.post("/rag/ask", response_model=RagAskResponse)
async def ask_document_with_rag(request: RagAskRequest) -> RagAskResponse:
    """Beantwortet eine Frage anhand lokal gefundener RAG-Chunks."""
    try:
        return await answer_rag_question(
            document_id=request.document_id,
            question=request.question,
            top_k=request.top_k,
        )
    except AppError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Interner Fehler: {exc}") from exc
