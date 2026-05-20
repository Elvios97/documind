from pathlib import Path
import re

from fastapi import UploadFile

from models.errors import AppError


BACKEND_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BACKEND_DIR / "uploads"


def _safe_filename(filename: str) -> str:
    """Reduziert Dateinamen auf unkritische Zeichen fuer lokale Speicherung."""
    clean_name = Path(filename).name.strip()
    clean_name = re.sub(r"[^A-Za-z0-9._-]+", "_", clean_name)
    return clean_name or "document.pdf"


async def save_pdf_file(file: UploadFile, document_id: str) -> Path:
    """Speichert die hochgeladene PDF lokal im uploads-Ordner."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    content = await file.read()
    if not content:
        raise AppError(400, "Die hochgeladene PDF ist leer.")

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
