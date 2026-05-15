# documind - Architektur

## Systemübersicht

```
┌─────────────────────────────────────────────────────┐
│              React Desktop UI (Vite)                 │
│          (später: Tauri Desktop App)                 │
└────────────────────────┬────────────────────────────┘
                         │ HTTP/REST API
                         │
┌────────────────────────▼────────────────────────────┐
│         FastAPI Backend (Python)                     │
│  - API Routes                                        │
│  - PDF Upload Handler                               │
│  - Service Layer                                     │
└────────────────────────┬────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐   ┌──────────┐   ┌─────────────┐
    │  PDF    │   │ Local    │   │   ChromaDB  │
    │ Upload  │   │  Ollama  │   │ Vector DB   │
    │ Storage │   │  (LLM)   │   │             │
    └─────────┘   └──────────┘   └─────────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
    ┌────────────────────▼────────────────────┐
    │       RAG Pipeline                       │
    │  1. PDF Text Chunking                   │
    │  2. Embedding Generation                │
    │  3. Vector Storage in ChromaDB           │
    │  4. Query Processing                    │
    │  5. Context Retrieval                   │
    │  6. LLM Response via Ollama             │
    └─────────────────────────────────────────┘
```

## Datenfluss

### Upload-Phase
1. User lädt PDF in React UI hoch
2. Frontend sendet POST zu `/api/pdf/upload`
3. Backend speichert Datei in `backend/uploads/`
4. Response mit Metadaten an Frontend

### Verarbeitung-Phase (geplant)
1. Backend liest PDF mit PyMuPDF
2. Text wird in Chunks aufgeteilt
3. Chunks in Embeddings konvertiert (local model)
4. Embeddings in ChromaDB gespeichert

### Chat-Phase (geplant)
1. User Frage sendet an Backend
2. Question Embedding wird generiert
3. ChromaDB findet ähnliche Chunks (RAG)
4. Kontext + Question zu Ollama LLM
5. LLM generiert Antwort
6. Response an Frontend

## Komponenten

### Backend (`backend/app/`)
- **core/config.py**: Zentrale Konfiguration
- **api/routes/**: API Endpunkte
- **services/**: Business-Logik
- **models/**: Pydantic Validierungsmodelle
- **rag/**: RAG-Pipeline (Phase 5)

### Frontend (`frontend/`)
- React Komponenten
- API Client
- UI für Upload & Chat

### Dokumentation (`docs/`)
- architecture.md (diese Datei)
- roadmap.md
- learning-notes.md

## Deployment

### Entwicklung
- Backend: `uvicorn app.main:app --reload`
- Frontend: `npm run dev`

### Produktion (später)
- Backend: Containerized FastAPI mit Gunicorn
- Frontend: Tauri Desktop App
- Optional: Docker Compose für Orchestration

## Lokale KI Integration

- **Ollama**: Lokale LLM ausführen
- **Embeddings**: Lokale Modelle (z.B. nomic-embed-text)
- **ChromaDB**: Lokale Vector Database
- **Vorteil**: Datenschutz, keine API-Abhängigkeit
