GERMAN_MARKERS = {
    " der ",
    " die ",
    " das ",
    " und ",
    " ist ",
    " sind ",
    " was ",
    " welche ",
    " welcher ",
    " welches ",
    " warum ",
    " wie ",
    " wer ",
    " wieso ",
    " worum ",
    " zusammen ",
    " dokument ",
}

ENGLISH_MARKERS = {
    " the ",
    " and ",
    " is ",
    " are ",
    " what ",
    " which ",
    " why ",
    " how ",
    " who ",
    " summarize ",
    " summary ",
    " document ",
}


def detect_answer_language(question: str) -> str:
    """Erkennt fuer den MVP grob Deutsch oder Englisch anhand der Nutzerfrage."""
    normalized_question = f" {question.strip().lower()} "

    if any(character in normalized_question for character in "äöüß"):
        return "German"

    german_score = sum(1 for marker in GERMAN_MARKERS if marker in normalized_question)
    english_score = sum(1 for marker in ENGLISH_MARKERS if marker in normalized_question)

    if english_score > german_score:
        return "English"

    return "German"


def build_language_instruction(question: str) -> str:
    language = detect_answer_language(question)
    if language == "English":
        return "Answer in English because the user asked in English."

    return "Antworte auf Deutsch, weil die Nutzerfrage auf Deutsch gestellt wurde."
