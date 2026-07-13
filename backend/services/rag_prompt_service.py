from models.chunk import RetrievedChunk
from models.errors import AppError
from models.rag import AnalysisMode
from services.language_service import build_language_instruction


def build_rag_question_prompt(
    question: str,
    chunks: list[RetrievedChunk],
    mode: AnalysisMode = "ask",
    document_names: dict[str, str] | None = None,
) -> str:
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
                    f"Dokument: {(document_names or {}).get(chunk.document_id, chunk.document_id)}",
                    f"Seite: {chunk.page_number}",
                    f"Chunk: {chunk.chunk_id}",
                    "Text:",
                    chunk.text.strip(),
                ]
            )
        )

    sources_text = "\n\n".join(source_blocks)
    mode_instruction = {
        "ask": "Beantworte die konkrete Frage direkt anhand der relevantesten Quellen.",
        "compare": (
            "Vergleiche die Inhalte der Dokumente. Arbeite Gemeinsamkeiten, Unterschiede und moegliche "
            "Widersprueche klar heraus. Ordne jede Aussage nachvollziehbar einer Quelle zu."
        ),
        "summarize": (
            "Fasse zuerst die belegten Kernaussagen je Dokument knapp zusammen und formuliere danach "
            "ein dokumentuebergreifendes Gesamtfazit."
        ),
    }[mode]

    return (
        "Du bist Documind, ein lokaler Assistent fuer PDF-Analyse.\n"
        "Beantworte die Nutzerfrage ausschliesslich anhand der gefundenen Quellen.\n"
        "Wenn die Antwort nicht in den Quellen steht, sage ehrlich, dass du es nicht weisst.\n"
        "Erfinde keine Informationen.\n"
        f"Analysemodus: {mode}. {mode_instruction}\n"
        f"{build_language_instruction(clean_question)}\n"
        "Antworte klar, knapp und verstaendlich.\n"
        "Nutze eindeutige Quellenhinweise wie '[Quelle 1, Dokumentname, Seite 2]'.\n\n"
        "Gefundene Quellen:\n"
        "-----\n"
        f"{sources_text}\n"
        "-----\n\n"
        f"Nutzerfrage: {clean_question}\n\n"
        "Antwort:"
    )
