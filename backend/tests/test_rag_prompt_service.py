import pytest

from models.chunk import RetrievedChunk
from models.errors import AppError
from services.rag_prompt_service import build_rag_question_prompt


def test_build_rag_question_prompt_contains_sources_and_rules() -> None:
    chunks = [
        RetrievedChunk(
            document_id="doc-test",
            chunk_id="doc-test-p0002-c0000",
            chunk_index=0,
            page_number=2,
            text="Documind nutzt lokale Quellen.",
            score=0.82,
        )
    ]

    prompt = build_rag_question_prompt("Was nutzt Documind?", chunks)

    assert "ausschliesslich anhand der gefundenen Quellen" in prompt
    assert "Erfinde keine Informationen" in prompt
    assert "Antworte auf Deutsch" in prompt
    assert "[Quelle 1]" in prompt
    assert "Seite: 2" in prompt
    assert "doc-test-p0002-c0000" in prompt
    assert "Documind nutzt lokale Quellen." in prompt
    assert "Was nutzt Documind?" in prompt


def test_build_rag_question_prompt_answers_english_questions_in_english() -> None:
    chunks = [
        RetrievedChunk(
            document_id="doc-test",
            chunk_id="doc-test-p0001-c0000",
            chunk_index=0,
            page_number=1,
            text="Documind uses local sources.",
            score=0.88,
        )
    ]

    prompt = build_rag_question_prompt("What does Documind use?", chunks)

    assert "Answer in English" in prompt


def test_build_rag_question_prompt_rejects_empty_question() -> None:
    with pytest.raises(AppError, match="Frage"):
        build_rag_question_prompt("   ", [])


def test_build_rag_question_prompt_rejects_empty_chunks() -> None:
    with pytest.raises(AppError, match="keine relevanten"):
        build_rag_question_prompt("Was steht drin?", [])
