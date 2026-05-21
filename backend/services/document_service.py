from models.document import DeleteDocumentResponse, DocumentDetail
from storage.document_store import delete_document_text, get_document_detail
from storage.file_storage import delete_pdf_files_for_document
from services.vector_store_service import delete_document_chunks


def get_document(document_id: str) -> DocumentDetail:
    """Liefert Dokumentdetails fuer API und spaetere UI."""
    return get_document_detail(document_id)


def delete_document(document_id: str) -> DeleteDocumentResponse:
    """Loescht ein Dokument aus JSON-Speicher, Uploads und Vector Store."""
    get_document_detail(document_id)
    delete_document_chunks(document_id)
    delete_pdf_files_for_document(document_id)
    delete_document_text(document_id)

    return DeleteDocumentResponse(document_id=document_id, deleted=True)
