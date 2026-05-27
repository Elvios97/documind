import services.document_service as document_service
from models.pdf import PDFPageText, PDFUploadResponse
from storage.document_store import _document_path, save_document_text
from storage.file_storage import UPLOAD_DIR


def test_delete_document_removes_json_pdf_and_vector_chunks(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(tmp_path))
    deleted_vector_ids: list[str] = []

    def fake_delete_document_chunks(document_id: str) -> None:
        deleted_vector_ids.append(document_id)

    monkeypatch.setattr(document_service, "delete_document_chunks", fake_delete_document_chunks)

    save_document_text(
        PDFUploadResponse(
            document_id="doc-delete-service",
            filename="delete.pdf",
            page_count=1,
            pages=[PDFPageText(page_number=1, text="Delete me")],
            full_text="Delete me",
        )
    )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = UPLOAD_DIR / "doc-delete-service_delete.pdf"
    pdf_path.write_bytes(b"%PDF-1.7\n")

    response = document_service.delete_document("doc-delete-service")

    assert response.document_id == "doc-delete-service"
    assert response.deleted is True
    assert deleted_vector_ids == ["doc-delete-service"]
    assert not _document_path("doc-delete-service").exists()
    assert not pdf_path.exists()
