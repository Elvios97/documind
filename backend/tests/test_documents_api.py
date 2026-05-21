from pathlib import Path

from fastapi.testclient import TestClient

import api.documents as documents_api
from main import app
from models.document import DeleteDocumentResponse
from models.pdf import PDFPageText, PDFUploadResponse
from storage.document_store import save_document_text


client = TestClient(app)


def test_get_documents_returns_stored_document_summaries(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(tmp_path))
    save_document_text(
        PDFUploadResponse(
            document_id="doc-a",
            filename="a.pdf",
            storage_path=str(Path("uploads") / "a.pdf"),
            page_count=2,
            pages=[PDFPageText(page_number=1, text="A")],
            full_text="A",
        )
    )
    save_document_text(
        PDFUploadResponse(
            document_id="doc-b",
            filename="b.pdf",
            storage_path=str(Path("uploads") / "b.pdf"),
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


def test_get_document_by_id_returns_document_detail(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(tmp_path))
    save_document_text(
        PDFUploadResponse(
            document_id="doc-detail",
            filename="detail.pdf",
            storage_path=str(Path("uploads") / "detail.pdf"),
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


def test_delete_document_by_id_returns_delete_response(monkeypatch) -> None:
    def fake_delete_document(document_id: str) -> DeleteDocumentResponse:
        assert document_id == "doc-delete"
        return DeleteDocumentResponse(document_id=document_id, deleted=True)

    monkeypatch.setattr(documents_api, "delete_document", fake_delete_document)

    response = client.delete("/documents/doc-delete")

    assert response.status_code == 200
    assert response.json() == {"document_id": "doc-delete", "deleted": True}
