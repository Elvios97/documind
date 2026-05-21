# Roadmap

Statuswerte:

- geplant: noch nicht begonnen
- in Arbeit: wird aktiv umgesetzt
- erledigt: umgesetzt und dokumentiert
- später: bewusst nach dem MVP

## Phasenplan

| Phase | Status | Ziel |
| --- | --- | --- |
| Phase 1: Backend-Grundsystem | erledigt | PDF Upload und lokale Text-Extraktion |
| Phase 2: Lokale Ollama-Integration | erledigt | Einfache Frage-Antwort-Funktion über PDF-Text |
| Phase 3: Lokales RAG-System | erledigt | Relevante Textstellen suchen und als Kontext nutzen |
| Phase 4: React Desktop UI | in Arbeit | Desktop-first Oberfläche bauen |
| Phase 5: Tauri Desktop App | später | React UI als echte Desktop-App vorbereiten |
| Phase 6: Portfolio Polish | in Arbeit | Dokumentation, Tests und Präsentation schärfen |

## Phase 1: Backend-Grundsystem

Status: erledigt

- FastAPI Backend
- Healthcheck
- PDF Upload Endpoint
- lokale Speicherung im `backend/uploads/` Ordner
- PyMuPDF für Textextraktion
- Text pro Seite extrahieren
- Seitenanzahl erkennen
- Dokument-ID erzeugen
- Dokumentdaten lokal als JSON speichern
- Fehlerbehandlung für falschen Dateityp, leere PDF und kaputte PDF
- pytest Tests für Upload, Text-Extraktion und zentrale Fehlerfälle

## Phase 2: Lokale Ollama-Integration

Status: erledigt

- Ollama Service
- lokales Modell über `DOCUMIND_OLLAMA_MODEL` konfigurierbar
- Prompt Service
- vorhandener `POST /ask` Endpoint
- Antwort nur anhand des PDF-Kontexts
- Schutz gegen erfundene Antworten durch klare Prompt-Regeln
- Fehlerbehandlung, wenn Ollama nicht läuft
- Fehlerbehandlung, wenn Modell fehlt
- Tests mit Mock für Ollama

## Phase 3: Lokales RAG-System

Status: erledigt

- Chunking Service
- Chunk-Größe konfigurierbar
- Chunk Overlap
- Seitenzahlen behalten
- lokale Embeddings
- ChromaDB lokal unter `local_data/chroma/`
- Vector Store Service
- RAG Service
- vorhandener `POST /rag/ask` Endpoint
- Quellenangaben mit Datei, Seite und Chunk
- Top-K Suche
- Tests für Chunking, Retrieval, RAG-Service und Fehlerfälle

## Phase 4: React Desktop UI

Status: in Arbeit

- React + TypeScript + Vite
- Desktop-first UI
- Sidebar
- PDF Upload
- Dokumentenliste
- Fragefeld
- Antwortanzeige
- Quellenanzeige
- Ladezustände
- Fehlermeldungen
- API Client für FastAPI Backend
- einfache UI Tests mit Vitest optional

## Phase 5: Tauri Desktop App

Status: später

- Tauri einrichten
- Windows als Hauptziel
- Backend und Frontend lokal betreiben
- Entwicklungsstart dokumentieren
- Build-Prozess dokumentieren
- Sicherheitskonfiguration prüfen
- keine komplizierte Auto-Start-Logik, solange nicht stabil

## Phase 6: Portfolio Polish

Status: in Arbeit

- professionelle README
- Architektur-Dokumentation
- API-Dokumentation
- RAG-Dokumentation
- Setup-Anleitung
- Tests dokumentieren
- Roadmap aktualisieren
- Screenshots-Platzhalter
- Datenschutz-Hinweis
- klare Projektbeschreibung
- gute Git-Struktur
- `.gitignore`, `requirements.txt` und spätere `package.json` Scripts prüfen

## Optionale Features nach dem MVP

Status: später

- mehrere PDFs gleichzeitig
- Chat History lokal speichern
- Dokumentenordner analysieren
- Zusammenfassungen
- Export von Antworten
- Modellwechsel in der UI
- Quellen anklickbar machen
- PDF-Vorschau
- Dark Mode
- lokale Profile
- Mobile/Tablet optional
- bessere RAG-Einstellungen
- Vergleich mehrerer lokaler Modelle
