import os

import httpx

from models.errors import AppError


DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "llama3"


def get_ollama_model() -> str:
    """Liest das lokale Ollama-Modell aus der Umgebung oder nutzt llama3."""
    return os.getenv("DOCUMIND_OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)


def get_ollama_base_url() -> str:
    """Liest die lokale Ollama-URL aus der Umgebung."""
    return os.getenv("DOCUMIND_OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).rstrip("/")


async def ask_ollama(prompt: str, model: str | None = None) -> tuple[str, str]:
    """Sendet einen Prompt an die lokale Ollama-API und gibt die Antwort zurueck."""
    selected_model = model or get_ollama_model()
    url = f"{get_ollama_base_url()}/api/generate"

    payload = {
        "model": selected_model,
        "prompt": prompt,
        "stream": False,
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
        raise AppError(504, "Ollama hat nicht rechtzeitig geantwortet.") from exc
    except httpx.HTTPError as exc:
        raise AppError(503, f"Fehler bei der Verbindung zu Ollama: {exc}") from exc

    if response.status_code == 404:
        raise AppError(
            404,
            f"Das Ollama-Modell '{selected_model}' ist nicht verfuegbar. Fuehre aus: ollama pull {selected_model}",
        )

    if response.status_code >= 400:
        detail = _extract_ollama_error(response)
        raise AppError(response.status_code, f"Ollama-Fehler: {detail}")

    try:
        data = response.json()
    except ValueError as exc:
        raise AppError(502, "Ollama hat keine gueltige JSON-Antwort geliefert.") from exc

    answer = str(data.get("response", "")).strip()
    if not answer:
        raise AppError(502, "Ollama hat keine Antwort zurueckgegeben.")

    return answer, selected_model


def _extract_ollama_error(response: httpx.Response) -> str:
    """Liest eine verstaendliche Fehlermeldung aus einer Ollama-Antwort."""
    try:
        data = response.json()
        error = data.get("error")
        if error:
            return str(error)
    except ValueError:
        pass
    return response.text or "Unbekannter Fehler"
