from fastapi.testclient import TestClient

import api.rag as rag_api
from main import app
from models.rag import AnalysisMode, RagAskResponse, RagRetrieveResponse, RagSource


client = TestClient(app)


def test_rag_ask_returns_mocked_answer(monkeypatch) -> None:
    async def fake_answer_rag_question(
        document_ids: list[str], question: str, top_k: int, mode: AnalysisMode
    ):
        assert document_ids == ["doc-test", "doc-second"]
        assert question == "Was steht drin?"
        assert top_k == 2
        assert mode == "compare"
        return RagAskResponse(
            document_ids=document_ids,
            question=question,
            answer="Documind bleibt lokal.",
            model="llama3",
            mode=mode,
            sources=[
                RagSource(
                    document_id="doc-test",
                    source_number=1,
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
        json={
            "document_ids": ["doc-test", "doc-second"],
            "question": "Was steht drin?",
            "top_k": 2,
            "mode": "compare",
        },
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
        json={"document_ids": ["doc-test"], "question": "Was steht drin?", "top_k": 0},
    )

    assert response.status_code == 422


def test_rag_retrieve_returns_sources_without_llm_answer(monkeypatch) -> None:
    async def fake_retrieve_rag_sources(
        document_ids: list[str], question: str, top_k: int
    ) -> RagRetrieveResponse:
        assert document_ids == ["doc-test", "doc-second"]
        assert question == "Welche Unterschiede gibt es?"
        assert top_k == 4
        return RagRetrieveResponse(
            document_ids=document_ids,
            question=question,
            sources=[
                RagSource(
                    document_id="doc-second",
                    source_number=1,
                    filename="vergleich.pdf",
                    page_number=3,
                    chunk_id="doc-second-p0003-c0000",
                    score=0.88,
                    text_preview="Ein relevanter Abschnitt.",
                )
            ],
        )

    monkeypatch.setattr(rag_api, "retrieve_rag_sources", fake_retrieve_rag_sources)

    response = client.post(
        "/rag/retrieve",
        json={
            "document_ids": ["doc-test", "doc-second"],
            "question": "Welche Unterschiede gibt es?",
            "top_k": 4,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["sources"][0]["filename"] == "vergleich.pdf"
    assert data["sources"][0]["source_number"] == 1
    assert "answer" not in data
    assert "model" not in data


def test_rag_ask_rejects_more_than_five_documents() -> None:
    response = client.post(
        "/rag/ask",
        json={
            "document_ids": [f"doc-{index}" for index in range(6)],
            "question": "Was steht drin?",
            "top_k": 5,
        },
    )

    assert response.status_code == 422


def test_rag_ask_hides_internal_error_details(monkeypatch) -> None:
    async def failing_answer_rag_question(
        document_ids: list[str], question: str, top_k: int, mode: AnalysisMode
    ) -> None:
        raise RuntimeError(r"C:\Users\schra\private\vector.db")

    monkeypatch.setattr(rag_api, "answer_rag_question", failing_answer_rag_question)

    response = client.post(
        "/rag/ask",
        json={"document_ids": ["doc-test"], "question": "Was steht drin?", "top_k": 2},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Interner Fehler bei der Verarbeitung der Anfrage."
    assert "private" not in response.text
