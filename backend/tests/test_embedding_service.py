import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from models.errors import AppError
from services.embedding_service import embed_text, embed_texts, get_embedding_model


def test_get_embedding_model_uses_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOCUMIND_EMBEDDING_MODEL", "all-minilm")

    assert get_embedding_model() == "all-minilm"


def test_embed_text_returns_single_embedding(monkeypatch: pytest.MonkeyPatch) -> None:
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}

    client = MagicMock()
    client.post = AsyncMock(return_value=response)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)

    monkeypatch.setattr("services.embedding_service.httpx.AsyncClient", MagicMock(return_value=client))

    embedding, model = asyncio.run(embed_text("  lokaler Text  ", model="nomic-embed-text"))

    assert embedding == [0.1, 0.2, 0.3]
    assert model == "nomic-embed-text"
    client.post.assert_awaited_once()
    _, kwargs = client.post.await_args
    assert kwargs["json"]["input"] == ["lokaler Text"]
    assert kwargs["json"]["model"] == "nomic-embed-text"


def test_embed_texts_returns_batch_embeddings(monkeypatch: pytest.MonkeyPatch) -> None:
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"embeddings": [[0.1, 0.2], [0.3, 0.4]]}

    client = MagicMock()
    client.post = AsyncMock(return_value=response)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)

    monkeypatch.setattr("services.embedding_service.httpx.AsyncClient", MagicMock(return_value=client))

    embeddings, model = asyncio.run(embed_texts(["Frage", "Antwort"], model="nomic-embed-text"))

    assert embeddings == [[0.1, 0.2], [0.3, 0.4]]
    assert model == "nomic-embed-text"


def test_embed_texts_rejects_empty_input() -> None:
    with pytest.raises(AppError, match="mindestens"):
        asyncio.run(embed_texts([]))

    with pytest.raises(AppError, match="nicht leer"):
        asyncio.run(embed_texts(["Text", "   "]))


def test_embed_texts_handles_missing_model(monkeypatch: pytest.MonkeyPatch) -> None:
    response = MagicMock()
    response.status_code = 404
    response.text = "model not found"
    response.json.return_value = {"error": "model not found"}

    client = MagicMock()
    client.post = AsyncMock(return_value=response)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)

    monkeypatch.setattr("services.embedding_service.httpx.AsyncClient", MagicMock(return_value=client))

    with pytest.raises(AppError, match="nicht verfuegbar"):
        asyncio.run(embed_text("Text", model="missing-model"))


def test_embed_texts_rejects_invalid_ollama_response(monkeypatch: pytest.MonkeyPatch) -> None:
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"embeddings": [[]]}

    client = MagicMock()
    client.post = AsyncMock(return_value=response)
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)

    monkeypatch.setattr("services.embedding_service.httpx.AsyncClient", MagicMock(return_value=client))

    with pytest.raises(AppError, match="ungueltiges Embedding"):
        asyncio.run(embed_text("Text", model="nomic-embed-text"))
