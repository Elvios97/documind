from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re

from models.document import DocumentDetail, DocumentSummary, StoredDocument
from models.errors import AppError
from models.pdf import PDFPageText, PDFUploadResponse


BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent
DEFAULT_DOCUMENTS_DIR = PROJECT_DIR / "local_data" / "documents"

DOCUMENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _document_path(document_id: str) -> Path:
    """Erzeugt einen sicheren Pfad fuer eine lokale Dokument-JSON."""
    if not document_id or not DOCUMENT_ID_PATTERN.fullmatch(document_id):
        raise AppError(400, "Ungueltige document_id.")
    return get_documents_dir() / f"{document_id}.json"


def get_documents_dir() -> Path:
    """Liefert den lokalen Speicherordner fuer extrahierte Dokumenttexte."""
    configured_dir = os.getenv("DOCUMIND_DOCUMENTS_DIR")
    if configured_dir:
        return Path(configured_dir)
    return DEFAULT_DOCUMENTS_DIR


def save_document_text(upload_result: PDFUploadResponse) -> StoredDocument:
    """Speichert extrahierten PDF-Text lokal als JSON fuer spaetere Fragen."""
    get_documents_dir().mkdir(parents=True, exist_ok=True)

    document = StoredDocument(
        document_id=upload_result.document_id,
        file_name=upload_result.filename,
        page_count=upload_result.page_count,
        pages=upload_result.pages,
        full_text=upload_result.full_text,
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    with _document_path(document.document_id).open("w", encoding="utf-8") as file:
        json.dump(document.model_dump(), file, ensure_ascii=False, indent=2)

    return document


def load_document_text(document_id: str) -> StoredDocument:
    """Laedt den gespeicherten PDF-Text anhand der document_id."""
    path = _document_path(document_id)
    if not path.exists():
        raise AppError(404, "Das Dokument wurde nicht gefunden.")

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return StoredDocument.model_validate(data)
    except AppError:
        raise
    except Exception as exc:
        raise AppError(500, f"Dokumentdaten konnten nicht gelesen werden: {exc}") from exc


def list_documents() -> list[DocumentSummary]:
    """Listet gespeicherte Dokumente fuer die UI."""
    documents_dir = get_documents_dir()
    if not documents_dir.exists():
        return []

    documents: list[DocumentSummary] = []
    for path in documents_dir.glob("*.json"):
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            document = StoredDocument.model_validate(data)
        except Exception:
            continue

        documents.append(
            DocumentSummary(
                document_id=document.document_id,
                filename=document.file_name,
                page_count=document.page_count,
                created_at=document.created_at,
            )
        )

    return sorted(documents, key=lambda document: document.created_at, reverse=True)


def get_document_detail(document_id: str) -> DocumentDetail:
    """Liefert Detaildaten zu einem gespeicherten Dokument."""
    document = load_document_text(document_id)
    return DocumentDetail(
        document_id=document.document_id,
        filename=document.file_name,
        page_count=document.page_count,
        created_at=document.created_at,
        pages=document.pages,
        full_text=document.full_text,
    )


def delete_document_text(document_id: str) -> None:
    """Loescht gespeicherte Dokumentdaten, falls sie existieren."""
    _document_path(document_id).unlink(missing_ok=True)


def create_document_record(
    document_id: str,
    file_name: str,
    page_count: int,
    pages: list[PDFPageText],
    full_text: str,
) -> StoredDocument:
    """Hilfsfunktion fuer Tests und spaetere interne Speicherpfade."""
    return StoredDocument(
        document_id=document_id,
        file_name=file_name,
        page_count=page_count,
        pages=pages,
        full_text=full_text,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
