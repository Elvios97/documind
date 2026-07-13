from pathlib import Path
from uuid import uuid4

import fitz
from fastapi import UploadFile

from models.errors import AppError
from models.pdf import PDFPageText, PDFUploadResponse
from services.indexing_service import index_document
from storage.file_storage import save_pdf_file
from storage.document_store import (
    save_document_text,
    update_document_indexing_progress,
    update_document_indexing_status,
)


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
        raise AppError(422, "Textextraktion fehlgeschlagen. Bitte pruefe die PDF-Datei.") from exc

    full_text = "\n\n".join(page.text for page in pages).strip()
    if not full_text:
        raise AppError(422, "Die PDF enthaelt keinen extrahierbaren Text.")

    return page_count, pages, full_text


async def process_uploaded_pdf(file: UploadFile | None) -> PDFUploadResponse:
    """Validiert, speichert und extrahiert eine PDF vor der Hintergrundindexierung."""
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
        page_count=page_count,
        pages=pages,
        full_text=full_text,
        indexing_status="indexing",
    )

    try:
        stored_document = save_document_text(upload_result)
    except Exception as exc:
        storage_path.unlink(missing_ok=True)
        raise AppError(500, "Dokumenttext konnte nicht lokal gespeichert werden.") from exc

    return upload_result


async def index_uploaded_document(document_id: str) -> None:
    """Indexiert ein bereits gespeichertes Dokument als Hintergrundaufgabe."""
    from storage.document_store import load_document_text

    try:
        document = load_document_text(document_id)
        await index_document(
            document,
            on_progress=lambda completed, total: update_document_indexing_progress(
                document_id, completed, total
            ),
        )
        update_document_indexing_status(document_id, "ready")
    except AppError as exc:
        update_document_indexing_status(document_id, "failed", exc.detail)
    except Exception:
        try:
            update_document_indexing_status(
                document_id,
                "failed",
                "Dokument konnte nicht lokal indexiert werden.",
            )
        except AppError as exc:
            if exc.status_code != 404:
                raise
