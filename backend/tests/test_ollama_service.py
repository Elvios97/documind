import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from models.errors import AppError
from services.ollama_service import ask_ollama


def test_ask_ollama_returns_answer_and_model(monkeypatch: pytest.MonkeyPatch) -> None:
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"response": "Antwort aus Ollama"}

    client = MagicMock()
    client.post = AsyncMock(return_value=response)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)

    monkeypatch.setattr("services.ollama_service.httpx.AsyncClient", MagicMock(return_value=client))

    answer, model = asyncio.run(ask_ollama("Prompt", model="llama3"))

    assert answer == "Antwort aus Ollama"
    assert model == "llama3"


def test_ask_ollama_handles_missing_model(monkeypatch: pytest.MonkeyPatch) -> None:
    response = MagicMock()
    response.status_code = 404
    response.text = "model not found"
    response.json.return_value = {"error": "model not found"}

    client = MagicMock()
    client.post = AsyncMock(return_value=response)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)

    monkeypatch.setattr("services.ollama_service.httpx.AsyncClient", MagicMock(return_value=client))

    with pytest.raises(AppError, match="nicht verfuegbar"):
        asyncio.run(ask_ollama("Prompt", model="missing-model"))
