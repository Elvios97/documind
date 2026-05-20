from pathlib import Path
from uuid import uuid4

import fitz
from fastapi import UploadFile

from models.errors import AppError
from models.pdf import PDFPageText, PDFUploadResponse
from services.indexing_service import index_document
from storage.file_storage import save_pdf_file
from storage.document_store import delete_document_text, save_document_text


def _validate_pdf_upload(file: UploadFile | None) -> None:
    """Prueft, ob eine Datei vorhanden ist und wie eine PDF benannt wurde."""
    if file is None or not file.filename:
        raise AppError(400, "Es wurde keine Datei hochgeladen.")

    if Path(file.filename).suffix.lower() != ".pdf":
        raise AppError(400, "Falscher Dateityp. Bitte lade eine PDF-Datei hoch.")


def extract_text_from_pdf(pdf_path: Path) -> tuple[int, list[PDFPageText], str]:
    """Liest Seitenanzahl und Text pro Seite mit PyMuPDF aus."""
    try:
        with fitz.open(pdf_path) as document:
            page_count = document.page_count
            if page_count == 0:
                raise AppError(422, "Die PDF enthaelt keine Seiten.")

            pages: list[PDFPageText] = []
            for page_index in range(page_count):
                page = document.load_page(page_index)
                text = page.get_text("text").strip()
                pages.append(PDFPageText(page_number=page_index + 1, text=text))

    except AppError:
        raise
    except Exception as exc:
        raise AppError(422, f"Textextraktion fehlgeschlagen: {exc}") from exc

    full_text = "\n\n".join(page.text for page in pages).strip()
    if not full_text:
        raise AppError(422, "Die PDF enthaelt keinen extrahierbaren Text.")

    return page_count, pages, full_text


async def process_uploaded_pdf(file: UploadFile | None) -> PDFUploadResponse:
    """Orchestriert Validierung, lokale Speicherung und Textextraktion."""
    _validate_pdf_upload(file)
    assert file is not None

    document_id = str(uuid4())
    storage_path = await save_pdf_file(file, document_id)

    try:
        page_count, pages, full_text = extract_text_from_pdf(storage_path)
    except AppError:
        # Fehlerhafte oder leere PDFs sollen nicht als erfolgreich gespeichert gelten.
        storage_path.unlink(missing_ok=True)
        raise

    upload_result = PDFUploadResponse(
        document_id=document_id,
        filename=file.filename or storage_path.name,
        storage_path=str(storage_path),
        page_count=page_count,
        pages=pages,
        full_text=full_text,
    )

    try:
        stored_document = save_document_text(upload_result)
    except Exception as exc:
        storage_path.unlink(missing_ok=True)
        raise AppError(500, f"Dokumenttext konnte nicht lokal gespeichert werden: {exc}") from exc

    try:
        await index_document(stored_document)
    except AppError as exc:
        _cleanup_failed_upload(storage_path, document_id)
        raise AppError(exc.status_code, f"Dokument konnte nicht lokal indexiert werden: {exc.detail}") from exc
    except Exception as exc:
        _cleanup_failed_upload(storage_path, document_id)
        raise AppError(500, f"Dokument konnte nicht lokal indexiert werden: {exc}") from exc

    return upload_result


def _cleanup_failed_upload(storage_path: Path, document_id: str) -> None:
    storage_path.unlink(missing_ok=True)
    delete_document_text(document_id)
