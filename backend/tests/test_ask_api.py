from pathlib import Path

from fastapi.testclient import TestClient

import api.ask as ask_module
from main import app
from models.pdf import PDFPageText, PDFUploadResponse
from storage.document_store import save_document_text


client = TestClient(app)


def test_ask_rejects_empty_question() -> None:
    response = client.post(
        "/ask",
        json={"document_id": "missing-document", "question": "   "},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Die Frage darf nicht leer sein."


def test_ask_rejects_missing_document() -> None:
    response = client.post(
        "/ask",
        json={"document_id": "missing-document", "question": "Was steht drin?"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Das Dokument wurde nicht gefunden."


def test_ask_returns_mocked_ollama_answer(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(tmp_path))
    document_id = "test-document-api"
    save_document_text(
        PDFUploadResponse(
            document_id=document_id,
            filename="test.pdf",
            storage_path=str(Path("uploads") / "test.pdf"),
            page_count=1,
            pages=[PDFPageText(page_number=1, text="Documind laeuft lokal.")],
            full_text="Documind laeuft lokal.",
        )
    )

    async def fake_ask_ollama(prompt: str):
        assert "Documind laeuft lokal." in prompt
        return "Documind laeuft lokal.", "llama3"

    monkeypatch.setattr(ask_module, "ask_ollama", fake_ask_ollama)

    response = client.post(
        "/ask",
        json={"document_id": document_id, "question": "Wie laeuft Documind?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == document_id
    assert data["answer"] == "Documind laeuft lokal."
    assert data["model"] == "llama3"
    assert data["used_context_length"] == len("Documind laeuft lokal.")
