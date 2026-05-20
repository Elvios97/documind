# Architektur

Documind ist als lokale Desktop-first Anwendung geplant. Im MVP laufen Backend, KI-Modell, Dokumentdaten und Vektordaten auf dem eigenen Windows-PC.

## Architekturübersicht

```text
React UI / später Tauri
        |
        | HTTP lokal
        v
FastAPI Backend
        |
        |-- PDF-Verarbeitung mit PyMuPDF
        |-- Dokument-Speicherung als JSON
        |-- Ollama Service für lokale LLM-Antworten
        |-- RAG Service für Retrieval
        |
        v
Lokales Dateisystem
        |
        |-- backend/uploads/
        |-- local_data/documents/
        |-- local_data/chroma/
        `-- local_data/chats/ später
```

## Lokaler Datenfluss

1. Nutzer lädt eine PDF hoch.
2. FastAPI speichert die PDF lokal.
3. PyMuPDF extrahiert Text pro Seite.
4. Dokumentdaten werden als JSON unter `local_data/documents/` gespeichert.
5. In Phase 2 wird der begrenzte PDF-Text direkt an Ollama gesendet.
6. In Phase 3 wird der Text in Chunks zerlegt und lokal indexiert.
7. ChromaDB findet passende Chunks für eine Frage.
8. Ollama beantwortet die Frage nur anhand des gefundenen Kontextes.
9. Die API gibt Antwort und Quellen an das Frontend zurück.

## Frontend

Das Frontend wird in Phase 4 mit React, TypeScript und Vite gebaut. Es ist Desktop-first geplant und soll später in Tauri laufen.

Geplante Bereiche:

- Sidebar
- PDF Upload
- Dokumentenliste
- Fragefeld
- Antwortanzeige
- Quellenanzeige
- Lade- und Fehlerzustände

## Backend

Das Backend ist in Schichten aufgebaut:

- `api/`: HTTP-Endpunkte
- `services/`: Geschäftslogik
- `storage/`: lokale Speicherung
- `models/`: Pydantic-Modelle
- `rag/`: spätere RAG-Komponenten
- `tests/`: automatisierte Tests

Diese Trennung hält API, Logik, Speicherung und Datenmodelle verständlich getrennt.

## PDF-Verarbeitung

PyMuPDF extrahiert:

- Seitenanzahl
- Text pro Seite
- vollständigen Dokumenttext

Fehlerfälle:

- keine Datei
- falscher Dateityp
- leere Datei
- ungültige PDF
- PDF ohne extrahierbaren Text

## Ollama

Ollama läuft lokal unter `http://127.0.0.1:11434`. Das Modell ist konfigurierbar, standardmäßig wird `llama3` verwendet.

Wichtig:

- keine externen KI-APIs
- keine Cloud
- Tests mocken Ollama-Aufrufe
- Fehler werden verständlich an die API zurückgegeben

## RAG

Phase 3 ersetzt den Volltext-Kontext durch Retrieval:

- Text wird in Chunks zerlegt.
- Chunks behalten Seiteninformationen.
- Embeddings werden lokal erzeugt.
- ChromaDB speichert Vektoren lokal.
- Top-K relevante Chunks werden gefunden.
- Ollama erhält nur diese Chunks als Kontext.
- Antworten enthalten Quellenangaben.

## ChromaDB

ChromaDB wird lokal unter `local_data/chroma/` gespeichert. Dieser Ordner gehört nicht in Git. ChromaDB dient nur als lokale Vektordatenbank für die eigenen Dokumente.

## Lokale Speicherung

| Datenart | Ort |
| --- | --- |
| hochgeladene PDFs | `backend/uploads/` |
| extrahierte Dokumenttexte | `local_data/documents/` |
| Vektordaten | `local_data/chroma/` |
| spätere Chatdaten | `local_data/chats/` |

## Warum keine Cloud?

Documind ist bewusst lokal gebaut:

- PDFs können private Inhalte enthalten.
- Lokale KI schützt Daten besser.
- Das Projekt zeigt Datenschutzbewusstsein.
- Keine laufenden API-Kosten.
- Keine Abhängigkeit von fremden Servern.
