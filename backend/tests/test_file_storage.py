import asyncio
import io

from fastapi import UploadFile
import pytest

from models.errors import AppError
import storage.file_storage as file_storage


def test_save_pdf_file_rejects_oversized_upload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(file_storage, "MAX_PDF_UPLOAD_BYTES", 8)
    upload = UploadFile(filename="too-large.pdf", file=io.BytesIO(b"%PDF-oversized"))

    with pytest.raises(AppError, match="zu gross"):
        asyncio.run(file_storage.save_pdf_file(upload, "doc-too-large"))

    assert not (file_storage.UPLOAD_DIR / "doc-too-large_too-large.pdf").exists()
