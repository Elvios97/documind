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


def test_get_pdf_file_for_document_returns_matching_upload(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setattr(file_storage, "UPLOAD_DIR", tmp_path)
    expected_path = tmp_path / "doc-test_example.pdf"
    expected_path.write_bytes(b"%PDF-test")

    assert file_storage.get_pdf_file_for_document("doc-test") == expected_path


def test_get_pdf_file_for_document_rejects_invalid_id() -> None:
    with pytest.raises(AppError, match="document_id"):
        file_storage.get_pdf_file_for_document("../doc-test")
