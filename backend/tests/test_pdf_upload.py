import asyncio
import io
from pathlib import Path

import fitz
from fastapi import UploadFile
import pytest

import services.pdf_service as pdf_module
from storage.document_store import _document_path, load_document_text
from storage.file_storage import UPLOAD_DIR


def test_pdf_upload_extracts_and_persists_text(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(tmp_path))
    asyncio.run(_run_pdf_upload_test(monkeypatch))


async def _run_pdf_upload_test(monkeypatch) -> None:
    pdf = fitz.open()
    page = pdf.new_page()
    page.insert_text((72, 72), "Phase 2 speichert Text lokal.")
    pdf_bytes = pdf.tobytes()
    pdf.close()

    upload = UploadFile(filename="phase2.pdf", file=io.BytesIO(pdf_bytes))
    result = await pdf_module.process_uploaded_pdf(upload)

    stored_document = load_document_text(result.document_id)
    stored_pdf_path = Path(UPLOAD_DIR) / f"{result.document_id}_phase2.pdf"

    stored_pdf_path.unlink(missing_ok=True)
    _document_path(result.document_id).unlink(missing_ok=True)

    assert result.page_count == 1
    assert result.pages[0].text == "Phase 2 speichert Text lokal."
    assert "storage_path" not in result.model_dump()
    assert stored_document.full_text == "Phase 2 speichert Text lokal."
    assert result.indexing_status == "indexing"
    assert stored_document.indexing_status == "indexing"


def test_background_indexing_persists_ready_status(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(tmp_path))
    monkeypatch.setattr(pdf_module, "uuid4", lambda: "doc-index-fail")
    asyncio.run(_run_background_indexing_success_test(monkeypatch))


async def _run_background_indexing_success_test(monkeypatch) -> None:
    pdf = fitz.open()
    page = pdf.new_page()
    page.insert_text((72, 72), "Dieser Text wird nicht erfolgreich indexiert.")
    pdf_bytes = pdf.tobytes()
    pdf.close()

    async def successful_index_document(document, **kwargs):
        assert document.indexing_status == "indexing"

    monkeypatch.setattr(pdf_module, "index_document", successful_index_document)

    upload = UploadFile(filename="phase3.pdf", file=io.BytesIO(pdf_bytes))

    result = await pdf_module.process_uploaded_pdf(upload)
    await pdf_module.index_uploaded_document(result.document_id)

    stored_document = load_document_text(result.document_id)
    Path(UPLOAD_DIR, f"{result.document_id}_phase3.pdf").unlink(missing_ok=True)
    _document_path(result.document_id).unlink(missing_ok=True)

    assert stored_document.indexing_status == "ready"
    assert stored_document.indexing_error is None


def test_background_indexing_persists_failure_status(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(tmp_path))
    asyncio.run(_run_background_indexing_failure_test(monkeypatch))


async def _run_background_indexing_failure_test(monkeypatch) -> None:
    from models.errors import AppError

    pdf = fitz.open()
    page = pdf.new_page()
    page.insert_text((72, 72), "Dieser Text kann nicht indexiert werden.")
    pdf_bytes = pdf.tobytes()
    pdf.close()

    async def failing_index_document(document, **kwargs):
        raise AppError(503, "Embedding-Modell nicht erreichbar.")

    monkeypatch.setattr(pdf_module, "index_document", failing_index_document)
    result = await pdf_module.process_uploaded_pdf(
        UploadFile(filename="failed.pdf", file=io.BytesIO(pdf_bytes))
    )
    await pdf_module.index_uploaded_document(result.document_id)

    stored_document = load_document_text(result.document_id)
    Path(UPLOAD_DIR, f"{result.document_id}_failed.pdf").unlink(missing_ok=True)
    _document_path(result.document_id).unlink(missing_ok=True)

    assert stored_document.indexing_status == "failed"
    assert stored_document.indexing_error == "Embedding-Modell nicht erreichbar."
