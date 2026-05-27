from services.language_service import build_language_instruction, detect_answer_language


def test_detect_answer_language_defaults_to_german_for_german_question() -> None:
    assert detect_answer_language("Was sind die wichtigsten Punkte?") == "German"


def test_detect_answer_language_detects_umlauts_as_german() -> None:
    assert detect_answer_language("Welche Risiken können entstehen?") == "German"


def test_detect_answer_language_detects_english_question() -> None:
    assert detect_answer_language("What are the key findings in this document?") == "English"


def test_build_language_instruction_for_english_question() -> None:
    instruction = build_language_instruction("Please summarize the document.")

    assert "Answer in English" in instruction

