# Documind

Documind is a local desktop-first PDF assistant for private document analysis with local AI. It combines a FastAPI backend, local PDF processing, Ollama, ChromaDB-based retrieval and a React/Tauri interface.

The project implements a complete local AI workflow: PDFs are uploaded, parsed, chunked, embedded, indexed and queried without external AI APIs or cloud storage.

## Highlights

- Local PDF upload and text extraction with PyMuPDF
- Automatic document indexing after upload
- Chunking with page references
- Local embeddings through Ollama `nomic-embed-text`
- Local vector storage with ChromaDB
- RAG answers with source references, page numbers and chunk IDs
- Clickable source cards that open the local PDF at the referenced page
- React UI for upload, document selection, questions, answers and sources
- Tauri desktop shell for Windows
- German/English answer language based on the user question
- Backend health state, loading states and clear error handling
- Tests for upload, storage, chunking, embeddings, RAG, API behavior and privacy constraints

## Privacy Model

Documind is designed to keep document data local.

- No cloud storage
- No external AI APIs
- No user accounts
- No synchronization
- PDFs, extracted text, chunks, embeddings and ChromaDB data stay on the local machine
- Ollama is only allowed through `localhost`, `127.0.0.1` or `::1`
- External Ollama or embedding servers are rejected
- API responses do not expose local storage paths
- Internal errors and local paths are not returned to clients
- PDF uploads are limited to 50 MB

## Tech Stack

| Area | Technology |
| --- | --- |
| Backend | Python, FastAPI, Pydantic |
| PDF processing | PyMuPDF |
| Local LLM | Ollama |
| Embeddings | Ollama `nomic-embed-text` |
| Vector store | ChromaDB |
| Frontend | React, TypeScript, Vite |
| Desktop shell | Tauri |
| Tests | pytest |

## Architecture

```text
React / Tauri UI
        |
        | local HTTP
        v
FastAPI Backend
        |
        |-- PDF upload and validation
        |-- Text extraction with PyMuPDF
        |-- Local JSON document storage
        |-- Chunking and page references
        |-- Local embeddings through Ollama
        |-- ChromaDB retrieval
        |-- Source-backed answer generation
        v
Local filesystem
```

## Project Structure

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
|   |-- src/
|   `-- src-tauri/
|-- local_data/
|   |-- chroma/
|   |-- documents/
|   `-- chats/
|-- docs/
`-- README.md
```

## Local Setup

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

### Ollama

Install Ollama for Windows:

```text
https://ollama.com/download/windows
```

Pull the required local models:

```powershell
ollama pull llama3
ollama pull nomic-embed-text
```

Optional model configuration:

```powershell
$env:DOCUMIND_OLLAMA_MODEL="llama3"
$env:DOCUMIND_EMBEDDING_MODEL="nomic-embed-text"
```

### Frontend

```powershell
cd frontend
npm install
npm.cmd run dev -- --port 5173
```

App:

```text
http://127.0.0.1:5173
```

### Tauri

Ollama must be running locally before starting the desktop shell. The Tauri app checks whether the FastAPI backend is reachable on `127.0.0.1:8000` and starts the local backend automatically in development when `backend/.venv` exists.

```powershell
cd frontend
npm.cmd run tauri dev
```

## API Examples

Upload a PDF:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/pdf/upload" `
  -F "file=@C:\Pfad\zu\deiner-datei.pdf"
```

Ask a RAG question:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/rag/ask" `
  -H "Content-Type: application/json" `
  -d "{\"document_id\":\"DEINE_DOCUMENT_ID\",\"question\":\"Welche Kernaussagen stehen im Dokument?\",\"top_k\":5}"
```

The RAG response includes:

- answer text
- used model
- source filename
- page number
- chunk ID
- text preview
- similarity score when available

## Tests

Run the backend test suite:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

Current local test result:

```text
57 passed
```

## Known Limitations

- The Tauri app can start the FastAPI backend automatically in development from `backend/.venv`.
- A release build can start a backend executable named `documind-backend.exe` next to the Tauri executable or a custom executable from `DOCUMIND_BACKEND_EXE`.
- The installer does not bundle or build the Python backend executable yet.
- OCR for scanned PDFs is not included.
- Chat history is not included.

These limits define the current local-first scope and keep the project focused on a clear PDF RAG workflow.

## Documentation

- [Architecture](docs/architecture.md)
- [API](docs/api.md)
- [Setup](docs/setup.md)
- [RAG notes](docs/rag.md)
- [Screenshot notes](docs/screenshots/README.md)
