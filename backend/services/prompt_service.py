from services.language_service import build_language_instruction


MAX_CONTEXT_CHARACTERS = 12000


def build_pdf_question_prompt(question: str, pdf_text: str) -> str:
    """Erstellt einen vorsichtigen Prompt fuer Fragen zum PDF-Kontext."""
    clean_question = question.strip()
    clean_context = pdf_text.strip()

    if not clean_question:
        raise ValueError("Die Frage darf nicht leer sein.")

    if not clean_context:
        raise ValueError("Der PDF-Kontext darf nicht leer sein.")

    # Der einfache /ask-Endpunkt nutzt begrenzten Volltext-Kontext. Der RAG-Endpunkt
    # nutzt stattdessen bereits ChromaDB-Retrieval mit relevanten Chunks.
    limited_context = clean_context[:MAX_CONTEXT_CHARACTERS]

    return (
        "Du bist Documind, ein lokaler Assistent fuer PDF-Analyse.\n"
        "Beantworte die Nutzerfrage ausschliesslich anhand des PDF-Kontexts.\n"
        "Wenn die Antwort nicht im Kontext steht, sage ehrlich, dass du es nicht weisst.\n"
        "Nutze keine erfundenen Informationen.\n"
        f"{build_language_instruction(clean_question)}\n"
        "Antworte klar, knapp und verstaendlich.\n\n"
        "PDF-Kontext:\n"
        "-----\n"
        f"{limited_context}\n"
        "-----\n\n"
        f"Nutzerfrage: {clean_question}\n\n"
        "Antwort:"
    )


def get_used_context_length(pdf_text: str) -> int:
    """Gibt zurueck, wie viele Kontextzeichen an Ollama gesendet werden."""
    return len(pdf_text.strip()[:MAX_CONTEXT_CHARACTERS])
