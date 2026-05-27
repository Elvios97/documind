from fastapi.testclient import TestClient

import api.rag as rag_api
from main import app
from models.rag import RagAskResponse, RagSource


client = TestClient(app)


def test_rag_ask_returns_mocked_answer(monkeypatch) -> None:
    async def fake_answer_rag_question(document_id: str, question: str, top_k: int):
        assert document_id == "doc-test"
        assert question == "Was steht drin?"
        assert top_k == 2
        return RagAskResponse(
            document_id=document_id,
            question=question,
            answer="Documind bleibt lokal.",
            model="llama3",
            sources=[
                RagSource(
                    filename="quelle.pdf",
                    page_number=1,
                    chunk_id="doc-test-p0001-c0000",
                    score=0.91,
                    text_preview="Documind bleibt lokal.",
                )
            ],
        )

    monkeypatch.setattr(rag_api, "answer_rag_question", fake_answer_rag_question)

    response = client.post(
        "/rag/ask",
        json={"document_id": "doc-test", "question": "Was steht drin?", "top_k": 2},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Documind bleibt lokal."
    assert data["model"] == "llama3"
    assert data["sources"][0]["filename"] == "quelle.pdf"
    assert data["sources"][0]["page_number"] == 1


def test_rag_ask_rejects_invalid_top_k() -> None:
    response = client.post(
        "/rag/ask",
        json={"document_id": "doc-test", "question": "Was steht drin?", "top_k": 0},
    )

    assert response.status_code == 422


def test_rag_ask_hides_internal_error_details(monkeypatch) -> None:
    async def failing_answer_rag_question(document_id: str, question: str, top_k: int) -> None:
        raise RuntimeError(r"C:\Users\schra\private\vector.db")

    monkeypatch.setattr(rag_api, "answer_rag_question", failing_answer_rag_question)

    response = client.post(
        "/rag/ask",
        json={"document_id": "doc-test", "question": "Was steht drin?", "top_k": 2},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Interner Fehler bei der Verarbeitung der Anfrage."
    assert "private" not in response.text
