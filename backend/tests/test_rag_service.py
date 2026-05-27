import asyncio

import pytest

import services.rag_service as rag_module
from models.chunk import RetrievedChunk
from models.errors import AppError
from models.pdf import PDFPageText, PDFUploadResponse
from storage.document_store import save_document_text


def test_answer_rag_question_returns_answer_and_sources(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(tmp_path))
    save_document_text(
        PDFUploadResponse(
            document_id="doc-test",
            filename="quelle.pdf",
            page_count=1,
            pages=[PDFPageText(page_number=1, text="Documind bleibt lokal.")],
            full_text="Documind bleibt lokal.",
        )
    )

    async def fake_embed_text(text: str):
        assert text == "Warum ist Documind lokal?"
        return [0.1, 0.2], "nomic-embed-text"

    def fake_query_chunks(query_embedding, top_k, document_id):
        assert query_embedding == [0.1, 0.2]
        assert top_k == 3
        assert document_id == "doc-test"
        return [
            RetrievedChunk(
                document_id="doc-test",
                chunk_id="doc-test-p0001-c0000",
                chunk_index=0,
                page_number=1,
                text="Documind bleibt lokal und nutzt keine Cloud.",
                score=0.9,
            )
        ]

    async def fake_ask_ollama(prompt: str):
        assert "Documind bleibt lokal" in prompt
        return "Documind bleibt lokal.", "llama3"

    monkeypatch.setattr(rag_module, "embed_text", fake_embed_text)
    monkeypatch.setattr(rag_module, "query_chunks", fake_query_chunks)
    monkeypatch.setattr(rag_module, "ask_ollama", fake_ask_ollama)

    response = asyncio.run(
        rag_module.answer_rag_question(
            document_id="doc-test",
            question=" Warum ist Documind lokal? ",
            top_k=3,
        )
    )

    assert response.document_id == "doc-test"
    assert response.question == "Warum ist Documind lokal?"
    assert response.answer == "Documind bleibt lokal."
    assert response.model == "llama3"
    assert len(response.sources) == 1
    assert response.sources[0].filename == "quelle.pdf"
    assert response.sources[0].page_number == 1
    assert response.sources[0].chunk_id == "doc-test-p0001-c0000"
    assert response.sources[0].score == 0.9


def test_answer_rag_question_rejects_no_retrieval_results(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setenv("DOCUMIND_DOCUMENTS_DIR", str(tmp_path))
    save_document_text(
        PDFUploadResponse(
            document_id="doc-test",
            filename="quelle.pdf",
            page_count=1,
            pages=[PDFPageText(page_number=1, text="Documind bleibt lokal.")],
            full_text="Documind bleibt lokal.",
        )
    )

    async def fake_embed_text(text: str):
        return [0.1, 0.2], "nomic-embed-text"

    def fake_query_chunks(query_embedding, top_k, document_id):
        return []

    monkeypatch.setattr(rag_module, "embed_text", fake_embed_text)
    monkeypatch.setattr(rag_module, "query_chunks", fake_query_chunks)

    with pytest.raises(AppError, match="keine relevanten"):
        asyncio.run(rag_module.answer_rag_question("doc-test", "Was steht drin?"))
