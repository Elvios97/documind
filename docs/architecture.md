# Architektur

Documind ist eine lokale Windows-Desktop-Anwendung. React läuft in einer Tauri-Hülle und kommuniziert ausschließlich über HTTP mit einem lokalen FastAPI-Backend. Dokumente, Metadaten und Vektordaten bleiben auf dem Rechner.

## Systemübersicht

```text
React UI / Tauri
        |
        | HTTP auf 127.0.0.1:8000
        v
FastAPI Backend
        |
        |-- PDF-Verarbeitung mit PyMuPDF
        |-- Dokument-Lifecycle und JSON-Speicherung
        |-- Chunking und Indexierung
        |-- Ollama für Embeddings und Antworten
        `-- ChromaDB für Retrieval
        |
        v
Lokales Dateisystem + lokaler Ollama-Dienst
```

## Datenfluss

1. Die UI lädt eine PDF an `POST /api/pdf/upload`.
2. Das Backend validiert Dateityp, Größe und PDF-Inhalt.
3. PyMuPDF extrahiert Text und Seiteninformationen.
4. Dokumentmetadaten und PDF werden lokal gespeichert.
5. Die Upload-API antwortet mit dem persistenten Status `indexing`.
6. Eine Hintergrundaufgabe zerlegt den Text in überlappende Chunks.
7. Ollama erzeugt lokale Embeddings mit `nomic-embed-text`.
8. ChromaDB speichert die Vektoren unter `local_data/chroma/` und setzt den Status auf `ready`.
9. `POST /rag/ask` sucht relevante Chunks für das ausgewählte Dokument.
10. Ollama erzeugt eine Antwort ausschließlich aus diesem Kontext.
11. Die UI zeigt Antwort, Modell und anklickbare Quellenkarten.

## Backend-Schichten

- `api/`: HTTP-Routen und Übersetzung kontrollierter Fehler
- `services/`: PDF-Verarbeitung, Chunking, Embeddings, Retrieval und RAG
- `storage/`: PDF- und JSON-Lifecycle
- `models/`: Pydantic-Request- und Response-Modelle
- `tests/`: isolierte Service- und API-Tests

Die API enthält möglichst wenig Geschäftslogik. Externe Ollama-Aufrufe werden in Tests gemockt.

## Lokale Speicherung

| Datenart | Ort |
| --- | --- |
| hochgeladene PDFs | `backend/uploads/` |
| Dokumentmetadaten und Text | `local_data/documents/` |
| Vektordaten | `local_data/chroma/` |
| spätere Chatdaten | `local_data/chats/` |

Diese Laufzeitdaten werden nicht in Git eingecheckt. Beim Löschen eines Dokuments entfernt das Backend PDF, Metadaten und zugehörige Vektordaten.

## Desktop-Start

In der Entwicklung sucht Tauri nach `backend/.venv` und startet Uvicorn automatisch, sofern Port 8000 nicht bereits belegt ist. Für einen Release wird `backend/dist/documind-backend.exe` als Tauri-Ressource gebündelt. Der Prozess wird beim Schließen der Anwendung beendet.

Ollama bleibt ein separat installierter lokaler Dienst.

## Sicherheitsgrenzen

- Ollama-Verbindungen sind auf Loopback-Adressen beschränkt.
- Tauri-CSP erlaubt Backend-Verbindungen und Frames nur über `127.0.0.1:8000`.
- CORS akzeptiert nur die bekannten lokalen Entwicklungs- und Tauri-Ursprünge.
- lokale Pfade und interne Exceptions werden nicht an Clients ausgegeben.
- Uploads sind auf PDF und 50 MB begrenzt.

## Geplante Erweiterung

Multi-Dokument-RAG benötigt eine Liste ausgewählter Dokument-IDs, Retrieval über mehrere Collections und eine dokumentübergreifend ausgewogene Quellenrangfolge. Die bestehende Quellenstruktur kann dafür weiterverwendet werden, weil jede Quelle bereits Dateiname, Seite und Chunk-ID enthält.
