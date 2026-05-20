import os

import httpx

from models.errors import AppError
from services.ollama_service import get_ollama_base_url


DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"


def get_embedding_model() -> str:
    """Liest das lokale Embedding-Modell aus der Umgebung."""
    return os.getenv("DOCUMIND_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)


async def embed_text(text: str, model: str | None = None) -> tuple[list[float], str]:
    """Erzeugt ein lokales Embedding fuer einen einzelnen Text."""
    embeddings, selected_model = await embed_texts([text], model=model)
    return embeddings[0], selected_model


async def embed_texts(texts: list[str], model: str | None = None) -> tuple[list[list[float]], str]:
    """Erzeugt lokale Embeddings fuer mehrere Texte ueber Ollama."""
    clean_texts = _clean_texts(texts)
    selected_model = model or get_embedding_model()
    url = f"{get_ollama_base_url()}/api/embed"

    payload = {
        "model": selected_model,
        "input": clean_texts,
        "truncate": True,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
    except httpx.ConnectError as exc:
        raise AppError(
            503,
            "Ollama ist lokal nicht erreichbar. Starte Ollama und pruefe http://127.0.0.1:11434.",
        ) from exc
    except httpx.TimeoutException as exc:
        raise AppError(504, "Ollama hat nicht rechtzeitig auf die Embedding-Anfrage geantwortet.") from exc
    except httpx.HTTPError as exc:
        raise AppError(503, f"Fehler bei der Verbindung zu Ollama: {exc}") from exc

    if response.status_code == 404:
        raise AppError(
            404,
            f"Das Embedding-Modell '{selected_model}' ist nicht verfuegbar. Fuehre aus: ollama pull {selected_model}",
        )

    if response.status_code >= 400:
        detail = _extract_ollama_error(response)
        raise AppError(response.status_code, f"Ollama-Embedding-Fehler: {detail}")

    try:
        data = response.json()
    except ValueError as exc:
        raise AppError(502, "Ollama hat keine gueltige JSON-Embedding-Antwort geliefert.") from exc

    embeddings = _parse_embeddings(data, expected_count=len(clean_texts))
    return embeddings, selected_model


def _clean_texts(texts: list[str]) -> list[str]:
    if not texts:
        raise AppError(400, "Es muss mindestens ein Text fuer Embeddings uebergeben werden.")

    clean_texts = [text.strip() for text in texts]
    if any(not text for text in clean_texts):
        raise AppError(400, "Embedding-Texte duerfen nicht leer sein.")

    return clean_texts


def _parse_embeddings(data: dict, expected_count: int) -> list[list[float]]:
    raw_embeddings = data.get("embeddings")
    if not isinstance(raw_embeddings, list) or len(raw_embeddings) != expected_count:
        raise AppError(502, "Ollama hat keine passende Embedding-Liste geliefert.")

    embeddings: list[list[float]] = []
    for raw_embedding in raw_embeddings:
        if not isinstance(raw_embedding, list) or not raw_embedding:
            raise AppError(502, "Ollama hat ein leeres oder ungueltiges Embedding geliefert.")

        try:
            embeddings.append([float(value) for value in raw_embedding])
        except (TypeError, ValueError) as exc:
            raise AppError(502, "Ollama hat ein nicht numerisches Embedding geliefert.") from exc

    return embeddings


def _extract_ollama_error(response: httpx.Response) -> str:
    try:
        data = response.json()
        error = data.get("error")
        if error:
            return str(error)
    except ValueError:
        pass
    return response.text or "Unbekannter Fehler"
