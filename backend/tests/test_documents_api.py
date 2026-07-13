from fastapi.testclient import TestClient

import api.documents as documents_api
from main import app
from models.document import DeleteDocumentResponse
from models.pdf import PDFPageText, PDFUploadResponse
from storage.document_store import save_document_text
import storage.file_storage as file_storage


client = TestClient(app)


def test_get_documents_returns_stored_document_summaries(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(tmp_path))
    save_document_text(
        PDFUploadResponse(
            document_id="doc-a",
            filename="a.pdf",
            page_count=2,
            pages=[PDFPageText(page_number=1, text="A")],
            full_text="A",
        )
    )
    save_document_text(
        PDFUploadResponse(
            document_id="doc-b",
            filename="b.pdf",
            page_count=1,
            pages=[PDFPageText(page_number=1, text="B")],
            full_text="B",
        )
    )

    response = client.get("/documents")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {document["document_id"] for document in data} == {"doc-a", "doc-b"}
    assert {document["filename"] for document in data} == {"a.pdf", "b.pdf"}


def test_get_documents_returns_empty_list(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(tmp_path))

    response = client.get("/documents")

    assert response.status_code == 200
    assert response.json() == []


def test_retry_document_indexing_enqueues_document(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(tmp_path))
    save_document_text(
        PDFUploadResponse(
            document_id="doc-retry",
            filename="retry.pdf",
            page_count=1,
            pages=[PDFPageText(page_number=1, text="Erneut indexieren")],
            full_text="Erneut indexieren",
            indexing_status="failed",
        )
    )
    enqueued: list[str] = []
    monkeypatch.setattr(documents_api.indexing_queue, "contains", lambda document_id: False)
    monkeypatch.setattr(documents_api.indexing_queue, "enqueue", lambda document_id: enqueued.append(document_id) or True)
    monkeypatch.setattr(documents_api.indexing_queue, "get_position", lambda document_id: 1)
    monkeypatch.setattr(documents_api.indexing_queue, "is_active", lambda document_id: False)

    response = client.post("/documents/doc-retry/index")

    assert response.status_code == 200
    assert response.json()["indexing_status"] == "indexing"
    assert response.json()["indexing_queue_position"] == 1
    assert enqueued == ["doc-retry"]


def test_cancel_document_indexing_marks_document_cancelled(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(tmp_path))
    save_document_text(
        PDFUploadResponse(
            document_id="doc-cancel",
            filename="cancel.pdf",
            page_count=1,
            pages=[PDFPageText(page_number=1, text="Abbrechen")],
            full_text="Abbrechen",
            indexing_status="indexing",
        )
    )

    async def fake_cancel(document_id: str) -> bool:
        return document_id == "doc-cancel"

    monkeypatch.setattr(documents_api.indexing_queue, "cancel", fake_cancel)
    monkeypatch.setattr(documents_api.indexing_queue, "get_position", lambda document_id: None)
    monkeypatch.setattr(documents_api.indexing_queue, "is_active", lambda document_id: False)

    response = client.post("/documents/doc-cancel/index/cancel")

    assert response.status_code == 200
    assert response.json()["indexing_status"] == "cancelled"
    assert response.json()["indexing_active"] is False


def test_get_document_by_id_returns_document_detail(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(tmp_path))
    save_document_text(
        PDFUploadResponse(
            document_id="doc-detail",
            filename="detail.pdf",
            page_count=1,
            pages=[PDFPageText(page_number=1, text="Detailtext")],
            full_text="Detailtext",
        )
    )

    response = client.get("/documents/doc-detail")

    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == "doc-detail"
    assert data["filename"] == "detail.pdf"
    assert data["pages"][0]["text"] == "Detailtext"
    assert data["full_text"] == "Detailtext"


def test_get_document_file_returns_local_pdf(monkeypatch, tmp_path) -> None:
    documents_dir = tmp_path / "documents"
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(documents_dir))
    monkeypatch.setattr(file_storage, "UPLOAD_DIR", uploads_dir)

    save_document_text(
        PDFUploadResponse(
            document_id="doc-file",
            filename="file.pdf",
            page_count=1,
            pages=[PDFPageText(page_number=1, text="Detailtext")],
            full_text="Detailtext",
        )
    )
    (uploads_dir / "doc-file_file.pdf").write_bytes(b"%PDF-test")

    response = client.get("/documents/doc-file/file")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content == b"%PDF-test"


def test_get_document_file_rejects_invalid_id() -> None:
    response = client.get("/documents/bad*id/file")

    assert response.status_code == 400


def test_get_document_source_view_returns_page_context(monkeypatch, tmp_path) -> None:
    documents_dir = tmp_path / "documents"
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(documents_dir))
    monkeypatch.setattr(file_storage, "UPLOAD_DIR", uploads_dir)

    save_document_text(
        PDFUploadResponse(
            document_id="doc-source",
            filename="source.pdf",
            page_count=2,
            pages=[
                PDFPageText(page_number=1, text="Erste Seite"),
                PDFPageText(page_number=2, text="Zweite Seite mit Quelle"),
            ],
            full_text="Erste Seite\n\nZweite Seite mit Quelle",
        )
    )
    (uploads_dir / "doc-source_source.pdf").write_bytes(b"%PDF-test")

    response = client.get("/documents/doc-source/source/2")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Seite 2 von 2" in response.text
    assert "Zweite Seite mit Quelle" in response.text
    assert "/documents/doc-source/file#page=2" in response.text


def test_get_document_source_view_highlights_matching_text(monkeypatch, tmp_path) -> None:
    documents_dir = tmp_path / "documents"
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(documents_dir))
    monkeypatch.setattr(file_storage, "UPLOAD_DIR", uploads_dir)

    save_document_text(
        PDFUploadResponse(
            document_id="doc-highlight",
            filename="highlight.pdf",
            page_count=1,
            pages=[
                PDFPageText(
                    page_number=1,
                    text="Einleitung\n\nDiese wichtige Quelle soll markiert werden.\n\nEnde",
                ),
            ],
            full_text="Einleitung\n\nDiese wichtige Quelle soll markiert werden.\n\nEnde",
        )
    )
    (uploads_dir / "doc-highlight_highlight.pdf").write_bytes(b"%PDF-test")

    response = client.get(
        "/documents/doc-highlight/source/1",
        params={"highlight": "Diese wichtige Quelle soll markiert werden."},
    )

    assert response.status_code == 200
    assert "<mark>Diese wichtige Quelle soll markiert werden.</mark>" in response.text


def test_get_document_source_view_rejects_invalid_page(monkeypatch, tmp_path) -> None:
    documents_dir = tmp_path / "documents"
    uploads_dir = tmp_path / "uploads"
    uploads_dir.mkdir()
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(documents_dir))
    monkeypatch.setattr(file_storage, "UPLOAD_DIR", uploads_dir)
    save_document_text(
        PDFUploadResponse(
            document_id="doc-page",
            filename="page.pdf",
            page_count=1,
            pages=[PDFPageText(page_number=1, text="Text")],
            full_text="Text",
        )
    )
    (uploads_dir / "doc-page_page.pdf").write_bytes(b"%PDF-test")

    response = client.get("/documents/doc-page/source/2")

    assert response.status_code == 400


def test_delete_document_by_id_returns_delete_response(monkeypatch) -> None:
    def fake_delete_document(document_id: str) -> DeleteDocumentResponse:
        assert document_id == "doc-delete"
        return DeleteDocumentResponse(document_id=document_id, deleted=True)

    monkeypatch.setattr(documents_api, "delete_document", fake_delete_document)

    response = client.delete("/documents/doc-delete")

    assert response.status_code == 200
    assert response.json() == {"document_id": "doc-delete", "deleted": True}


def test_get_document_hides_invalid_storage_details(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(tmp_path))
    (tmp_path / "corrupt-document.json").write_text("{invalid JSON", encoding="utf-8")

    response = client.get("/documents/corrupt-document")

    assert response.status_code == 500
    assert response.json()["detail"] == "Dokumentdaten konnten nicht gelesen werden."
    assert "JSON" not in response.text
