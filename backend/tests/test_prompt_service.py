import pytest

from services.prompt_service import MAX_CONTEXT_CHARACTERS, build_pdf_question_prompt, get_used_context_length


def test_build_pdf_question_prompt_contains_safety_rules() -> None:
    prompt = build_pdf_question_prompt(
        question="Was ist das Thema?",
        pdf_text="Dieses PDF beschreibt lokale KI.",
    )

    assert "ausschliesslich anhand des PDF-Kontexts" in prompt
    assert "nicht im Kontext steht" in prompt
    assert "Nutze keine erfundenen Informationen" in prompt
    assert "Antworte auf Deutsch" in prompt
    assert "Was ist das Thema?" in prompt
    assert "Dieses PDF beschreibt lokale KI." in prompt


def test_build_pdf_question_prompt_uses_english_for_english_question() -> None:
    prompt = build_pdf_question_prompt(
        question="What is the topic?",
        pdf_text="This PDF describes local AI.",
    )

    assert "Answer in English" in prompt


def test_build_pdf_question_prompt_rejects_empty_question() -> None:
    with pytest.raises(ValueError, match="Frage"):
        build_pdf_question_prompt(question="   ", pdf_text="Kontext")


def test_prompt_context_is_limited() -> None:
    long_text = "a" * (MAX_CONTEXT_CHARACTERS + 500)

    prompt = build_pdf_question_prompt(question="Kurz?", pdf_text=long_text)

    assert get_used_context_length(long_text) == MAX_CONTEXT_CHARACTERS
    assert ("a" * (MAX_CONTEXT_CHARACTERS + 1)) not in prompt
