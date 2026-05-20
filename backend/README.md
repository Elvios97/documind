# Documind Backend

Lokales FastAPI-Backend fuer PDF-Upload, PDF-Textextraktion, lokale Ollama-Fragen und ein lokales RAG-System mit ChromaDB.

## Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Ohne Aktivieren der venv:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## Ollama

Benoetigte lokale Modelle:

```powershell
ollama pull llama3
ollama pull nomic-embed-text
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Bei Windows-Temp-Problemen:

```powershell
.\.venv\Scripts\python.exe -m pytest --basetemp .\test_tmp_codex -p no:cacheprovider
```

## Endpunkte

- `GET /`: Healthcheck
- `POST /api/pdf/upload`: PDF hochladen, speichern, Text extrahieren und lokal indexieren
- `POST /ask`: Frage an den gespeicherten PDF-Text stellen
- `POST /rag/ask`: Frage ueber lokale RAG-Suche stellen und Quellen erhalten

## Lokale Daten

- Hochgeladene PDFs: `backend/uploads/`
- Extrahierte Dokumenttexte: `../local_data/documents/`
- ChromaDB-Daten: `../local_data/chroma/`
- Spaetere Chatdaten: `../local_data/chats/`

Die Tests koennen den Dokumentenspeicher mit `DOCUMIND_DOCUMENTS_DIR` auf einen temporaeren Ordner umleiten. ChromaDB kann mit `DOCUMIND_CHROMA_DIR` auf einen anderen lokalen Ordner zeigen.
