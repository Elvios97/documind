from pathlib import Path
import re

from fastapi import UploadFile

from models.errors import AppError


BACKEND_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BACKEND_DIR / "uploads"
MAX_PDF_UPLOAD_BYTES = 50 * 1024 * 1024
DOCUMENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _safe_filename(filename: str) -> str:
    """Reduziert Dateinamen auf unkritische Zeichen fuer lokale Speicherung."""
    clean_name = Path(filename).name.strip()
    clean_name = re.sub(r"[^A-Za-z0-9._-]+", "_", clean_name)
    return clean_name or "document.pdf"


async def save_pdf_file(file: UploadFile, document_id: str) -> Path:
    """Speichert die hochgeladene PDF lokal im uploads-Ordner."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    content = await file.read(MAX_PDF_UPLOAD_BYTES + 1)
    if not content:
        raise AppError(400, "Die hochgeladene PDF ist leer.")

    if len(content) > MAX_PDF_UPLOAD_BYTES:
        raise AppError(413, "Die PDF ist zu gross. Maximal erlaubt sind 50 MB.")

    # Ein PDF beginnt normalerweise mit dieser Signatur. Das faengt falsche
    # Dateien ab, selbst wenn sie versehentlich mit .pdf benannt wurden.
    if not content.startswith(b"%PDF"):
        raise AppError(400, "Die Datei ist keine gueltige PDF-Datei.")

    filename = _safe_filename(file.filename or "document.pdf")
    stored_filename = f"{document_id}_{filename}"
    storage_path = UPLOAD_DIR / stored_filename

    with storage_path.open("wb") as stored_file:
        stored_file.write(content)

    return storage_path.resolve()


def delete_pdf_files_for_document(document_id: str) -> int:
    """Loescht lokal gespeicherte PDF-Dateien fuer ein Dokument."""
    _validate_document_id(document_id)
    if not UPLOAD_DIR.exists():
        return 0

    deleted_count = 0
    for path in UPLOAD_DIR.glob(f"{document_id}_*"):
        if path.is_file():
            path.unlink(missing_ok=True)
            deleted_count += 1

    return deleted_count


def get_pdf_file_for_document(document_id: str) -> Path:
    """Liefert die lokal gespeicherte PDF-Datei fuer ein Dokument."""
    _validate_document_id(document_id)
    if not UPLOAD_DIR.exists():
        raise AppError(404, "Die PDF-Datei wurde nicht gefunden.")

    matching_files = sorted(path for path in UPLOAD_DIR.glob(f"{document_id}_*") if path.is_file())
    if not matching_files:
        raise AppError(404, "Die PDF-Datei wurde nicht gefunden.")

    return matching_files[0]


def _validate_document_id(document_id: str) -> None:
    if not document_id or not DOCUMENT_ID_PATTERN.fullmatch(document_id):
        raise AppError(400, "Ungueltige document_id.")
