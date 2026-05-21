from fastapi import APIRouter

from models.document import DeleteDocumentResponse, DocumentDetail, DocumentSummary
from models.errors import AppError
from services.document_service import delete_document, get_document
from storage.document_store import list_documents
from fastapi import HTTPException


router = APIRouter()


@router.get("/documents", response_model=list[DocumentSummary])
async def get_documents() -> list[DocumentSummary]:
    """Liefert lokal gespeicherte Dokumente fuer die Frontend-Sidebar."""
    return list_documents()


@router.get("/documents/{document_id}", response_model=DocumentDetail)
async def get_document_by_id(document_id: str) -> DocumentDetail:
    """Liefert Detaildaten zu einem lokal gespeicherten Dokument."""
    try:
        return get_document(document_id)
    except AppError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error


@router.delete("/documents/{document_id}", response_model=DeleteDocumentResponse)
async def delete_document_by_id(document_id: str) -> DeleteDocumentResponse:
    """Loescht ein Dokument lokal inklusive Upload und RAG-Chunks."""
    try:
        return delete_document(document_id)
    except AppError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error
