from models.chunk import RetrievedChunk
from models.errors import AppError


def build_rag_question_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    """Erstellt einen Prompt aus einer Frage und gefundenen RAG-Quellen."""
    clean_question = question.strip()
    if not clean_question:
        raise AppError(400, "Die Frage darf nicht leer sein.")

    if not chunks:
        raise AppError(422, "Es wurden keine relevanten Textstellen gefunden.")

    source_blocks = []
    for source_number, chunk in enumerate(chunks, start=1):
        source_blocks.append(
            "\n".join(
                [
                    f"[Quelle {source_number}]",
                    f"Seite: {chunk.page_number}",
                    f"Chunk: {chunk.chunk_id}",
                    "Text:",
                    chunk.text.strip(),
                ]
            )
        )

    sources_text = "\n\n".join(source_blocks)

    return (
        "Du bist Documind, ein lokaler Assistent fuer PDF-Analyse.\n"
        "Beantworte die Nutzerfrage ausschliesslich anhand der gefundenen Quellen.\n"
        "Wenn die Antwort nicht in den Quellen steht, sage ehrlich, dass du es nicht weisst.\n"
        "Erfinde keine Informationen.\n"
        "Antworte klar, knapp und verstaendlich.\n"
        "Nutze Quellenhinweise wie 'Quelle 1' oder 'Seite 2', wenn es hilfreich ist.\n\n"
        "Gefundene Quellen:\n"
        "-----\n"
        f"{sources_text}\n"
        "-----\n\n"
        f"Nutzerfrage: {clean_question}\n\n"
        "Antwort:"
    )
