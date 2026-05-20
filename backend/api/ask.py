from fastapi import APIRouter, HTTPException

from models.ask import AskRequest, AskResponse
from models.errors import AppError
from services.ollama_service import ask_ollama
from services.prompt_service import build_pdf_question_prompt, get_used_context_length
from storage.document_store import load_document_text


router = APIRouter()


@router.post("/ask", response_model=AskResponse)
async def ask_document(request: AskRequest) -> AskResponse:
    """Beantwortet eine Frage anhand eines lokal gespeicherten PDF-Texts."""
    try:
        question = request.question.strip()
        if not question:
            raise AppError(400, "Die Frage darf nicht leer sein.")

        document = load_document_text(request.document_id)
        if not document.full_text.strip():
            raise AppError(422, "Der gespeicherte PDF-Text ist leer.")

        prompt = build_pdf_question_prompt(question, document.full_text)
        answer, model = await ask_ollama(prompt)

        return AskResponse(
            document_id=request.document_id,
            question=question,
            answer=answer,
            model=model,
            used_context_length=get_used_context_length(document.full_text),
        )
    except AppError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Interner Fehler: {exc}") from exc
