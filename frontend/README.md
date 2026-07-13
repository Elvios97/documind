# Documind Frontend

Lokale React/TypeScript-Oberflaeche fuer Documind.

## Status

Phase 4 Grundfunktion:

- Vite + React + TypeScript
- PDF Upload
- persistente Dokumentenliste aus dem Backend
- lokales Loeschen gespeicherter Dokumente
- RAG-Fragefeld
- Antwortanzeige
- Quellenanzeige
- Lade- und Fehlerzustaende
- Tauri-Grundstruktur fuer Phase 5

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
http://127.0.0.1:5174
```

## Hinweise

- Das Frontend spricht lokal mit `http://127.0.0.1:8000`.
- Fuer Upload und RAG muessen Ollama, `llama3` und `nomic-embed-text` lokal verfuegbar sein.
- Die Dokumentenliste wird beim Start aus `GET /documents` geladen.

## Tauri vorbereiten

Die Desktop-Huelle liegt unter `src-tauri/`. In diesem ersten Phase-5-Schritt startet Documind das FastAPI-Backend noch separat.

Nach installiertem Rust und den Tauri-Voraussetzungen:

```powershell
cd frontend
npm run tauri dev
```

Build-Vorbereitung:

```powershell
cd frontend
npm run tauri build
```
