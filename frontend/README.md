# Documind Frontend

Lokale React/TypeScript-Oberflaeche fuer Documind.

## Status

Phase 4 gestartet:

- Vite + React + TypeScript
- PDF Upload
- persistente Dokumentenliste aus dem Backend
- lokales Loeschen gespeicherter Dokumente
- RAG-Fragefeld
- Antwortanzeige
- Quellenanzeige
- Lade- und Fehlerzustaende

## Start

Backend zuerst starten:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Frontend starten:

```powershell
cd frontend
npm install
npm run dev
```

App:

```text
http://127.0.0.1:5173
```

## Hinweise

- Das Frontend spricht lokal mit `http://127.0.0.1:8000`.
- Fuer Upload und RAG muessen Ollama, `llama3` und `nomic-embed-text` lokal verfuegbar sein.
- Die Dokumentenliste wird beim Start aus `GET /documents` geladen.
