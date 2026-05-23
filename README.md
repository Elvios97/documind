# Documind

Documind ist eine lokale Desktop-first App zur Analyse von PDFs mit lokaler KI. Das Projekt ist datenschutzfreundlich aufgebaut: PDFs, extrahierte Texte, Chunks, Embeddings, ChromaDB-Daten und spaetere Chatdaten bleiben lokal auf dem Rechner.

Der aktuelle Stand enthaelt ein Python/FastAPI-Backend mit PDF-Upload, Textextraktion, lokaler JSON-Speicherung, lokaler Ollama-Anbindung und einem lokalen RAG-System mit ChromaDB. Dazu kommt eine React-Oberflaeche fuer Upload, Dokumentenliste, Fragen, Antworten und Quellen. Die Tauri-Desktop-Huelle startet lokal unter Windows und ist fuer den MVP getestet.

## Ziele

- Lokale PDF-Analyse ohne Cloud
- Keine externen KI-APIs
- Keine Nutzerkonten
- Keine Online-Speicherung
- Lokales RAG mit Quellenangaben
- Saubere Trennung von API, Services, Storage und Modellen
- Portfolio-tauglicher Code mit Tests und Dokumentation

## Aktuelle Features

- PDF-Upload ueber FastAPI
- Lokale Speicherung der PDF unter `backend/uploads/`
- Textextraktion mit PyMuPDF
- Lokale Speicherung des extrahierten Texts als JSON unter `local_data/documents/`
- Automatische Indexierung nach erfolgreichem Upload
- Chunking mit Seitenbezug
- Lokale Embeddings ueber Ollama `nomic-embed-text`
- Lokale ChromaDB unter `local_data/chroma/`
- Einfache Frage zum gespeicherten PDF-Text ueber `POST /ask`
- RAG-Fragen mit Quellen ueber `POST /rag/ask`
- React UI fuer Upload, Dokumentauswahl, RAG-Fragen und Quellenanzeige
- Dokumentdetails und lokales Loeschen ueber Backend und UI
- Tauri-Desktop-Huelle unter `frontend/src-tauri/`, lokal unter Windows getestet
- Gemockte Tests fuer Ollama und Vector Store

Noch nicht Teil des aktuellen Stands:

- Kein automatischer Backend-Start aus der Tauri-App
- Kein automatisch gebündelter Start des FastAPI-Backends aus dem Installer
- Keine OCR fuer gescannte PDFs
- Keine Chat-History

## Tech-Stack

- Python
- FastAPI
- PyMuPDF
- Ollama lokal
- ChromaDB lokal
- Pydantic
- httpx
- pytest

## Projektstruktur

```text
documind/
|-- backend/
|   |-- api/
|   |-- models/
|   |-- services/
|   |-- storage/
|   |-- tests/
|   |-- uploads/
|   |-- main.py
|   `-- requirements.txt
|-- frontend/
|-- local_data/
|   |-- chroma/
|   |-- documents/
|   `-- chats/
|-- docs/
`-- README.md
```

## Lokale Installation

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Wenn PowerShell das Aktivieren blockiert, kann das venv-Python direkt genutzt werden:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Ollama vorbereiten

Installiere Ollama fuer Windows:

```text
https://ollama.com/download/windows
```

Lokale Modelle laden:

```powershell
ollama pull llama3
ollama pull nomic-embed-text
```

Documind nutzt standardmaessig `llama3` fuer Antworten und `nomic-embed-text` fuer Embeddings.

```powershell
$env:DOCUMIND_OLLAMA_MODEL="llama3"
$env:DOCUMIND_EMBEDDING_MODEL="nomic-embed-text"
```

## Backend starten

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Beispiel: PDF hochladen

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/pdf/upload" `
  -F "file=@C:\Pfad\zu\deiner-datei.pdf"
```

Nach erfolgreichem Upload wird das Dokument automatisch lokal indexiert.

## Beispiel: RAG-Frage stellen

```powershell
curl.exe -X POST "http://127.0.0.1:8000/rag/ask" `
  -H "Content-Type: application/json" `
  -d "{\"document_id\":\"DEINE_DOCUMENT_ID\",\"question\":\"Welche Kernaussagen stehen im Dokument?\",\"top_k\":5}"
```

Die Antwort enthaelt Text, Modellname und Quellen mit Datei, Seite, Chunk-ID und Textauszug.

## Tests starten

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

Falls Windows den Standard-Temp-Ordner blockiert:

```powershell
.\.venv\Scripts\python.exe -m pytest --basetemp .\test_tmp_codex -p no:cacheprovider
```

## Roadmap

- Phase 1: Backend-Grundsystem, PDF-Upload, lokale Textextraktion
- Phase 2: Lokale Ollama-Frage-Antwort-Funktion
- Phase 3: Lokales RAG-System mit ChromaDB und Quellenangaben
- Phase 4: React Desktop UI, Grundfunktion umgesetzt
- Phase 5: Tauri Desktop App, MVP-Desktop-Start und Windows-Installer-Build getestet
- Phase 6: Portfolio Polish

## Dokumentation

- [Projektplan](docs/project-plan.md)
- [Architektur](docs/architecture.md)
- [API](docs/api.md)
- [Setup](docs/setup.md)
- [RAG-Planung](docs/rag.md)
- [Roadmap](docs/roadmap.md)
