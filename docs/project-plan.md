# Projektplan: Documind

## Kurzbeschreibung

Documind ist eine lokale Desktop-first App zur Analyse von PDFs mit lokaler KI. PDFs, extrahierte Texte, Vektordaten und spätere Chatdaten bleiben auf dem eigenen Rechner. Für das MVP gibt es keine Cloud, keine externen KI-APIs, keine Nutzerkonten und keine Synchronisation.

## Ziel des Projekts

Documind soll zeigen, wie eine datenschutzfreundliche PDF-Analyse mit lokalem Backend, lokaler KI und späterem lokalem RAG-System sauber umgesetzt wird. Das Projekt soll technisch nachvollziehbar, testbar und portfolio-tauglich sein.

## MVP-Scope

- Lokales FastAPI-Backend
- PDF-Upload und lokale Speicherung
- Textextraktion pro Seite mit PyMuPDF
- Lokale Speicherung der Dokumentdaten als JSON
- Einfache Frage-Antwort-Funktion über Ollama
- Lokales RAG-System mit Chunking, Embeddings und ChromaDB
- React Desktop UI
- Tauri-Vorbereitung für Windows
- Professionelle Dokumentation und Tests

## Nicht-Ziele für das MVP

- Keine Cloud-Anbindung
- Keine externen KI-APIs
- Keine Online-Speicherung
- Kein Login
- Keine Synchronisation
- Keine Mobile- oder Tablet-App
- Kein Multi-User-System
- Kein Produktivbetrieb auf fremden Servern

## Tech-Stack

- Backend: Python, FastAPI, Pydantic
- PDF-Verarbeitung: PyMuPDF
- Lokale KI: Ollama
- RAG: Chunking Service, lokale Embeddings, ChromaDB
- Storage: lokales Dateisystem, JSON, `local_data/`
- Frontend: React, TypeScript, Vite
- Desktop: Tauri, später
- Tests: pytest, später optional Vitest

## Phasenübersicht

| Phase | Name | Status | Ziel |
| --- | --- | --- | --- |
| 1 | Backend-Grundsystem | erledigt | PDF Upload und lokale Textextraktion |
| 2 | Lokale Ollama-Integration | erledigt | Fragen zu extrahiertem PDF-Text |
| 3 | Lokales RAG-System | erledigt | Relevante Textstellen statt Volltext nutzen |
| 4 | React Desktop UI | in Arbeit | Bedienbare Desktop-first Oberfläche |
| 5 | Tauri Desktop App | später | React UI als Desktop-App verpacken |
| 6 | Portfolio Polish | fortlaufend | GitHub- und Bewerbungsqualität erreichen |

## Portfolio-Ziel

Documind soll als realistisches Junior Backend / AI Backend Portfolio-Projekt funktionieren. Der Fokus liegt auf sauberer Architektur, lokalen KI-Flows, verständlicher Dokumentation, Tests und nachvollziehbaren technischen Entscheidungen.

## Definition of Done je Phase

### Phase 1: Backend-Grundsystem

- Backend startet lokal.
- PDF kann hochgeladen werden.
- Text wird mit PyMuPDF extrahiert.
- Text pro Seite und Seitenanzahl werden zurückgegeben.
- Dokument-ID wird erzeugt.
- Dokumentdaten werden lokal als JSON gespeichert.
- Fehlerfälle für falschen Dateityp, leere Datei und ungültige PDF sind behandelt.
- pytest Tests laufen erfolgreich.

### Phase 2: Lokale Ollama-Integration

- Nutzer kann eine Frage zu einem gespeicherten Dokument stellen.
- Ollama wird lokal über `http://127.0.0.1:11434` angesprochen.
- Das Modell ist über Umgebungsvariable konfigurierbar.
- Prompt fordert Antworten nur aus dem PDF-Kontext.
- Fehler für nicht laufendes Ollama und fehlendes Modell sind verständlich.
- Ollama-Aufrufe sind in Tests gemockt.
- README und `setup.md` erklären den lokalen Ollama-Start.

### Phase 3: Lokales RAG-System

- PDF wird nach Upload in Chunks aufgeteilt.
- Chunks behalten Datei, Seite und Chunk-ID.
- Embeddings werden lokal erzeugt.
- ChromaDB speichert Vektoren unter `local_data/chroma/`.
- Top-K Retrieval liefert relevante Chunks.
- Antwort basiert nur auf gefundenem Kontext.
- Quellen werden mit Datei, Seite und Chunk angezeigt.
- Tests für Chunking, Retrieval, RAG-Service und Fehlerfälle laufen.

### Phase 4: React Desktop UI

- Frontend startet lokal.
- PDF Upload ist über die UI möglich.
- Dokumentenliste wird angezeigt.
- Frage kann über die UI gestellt werden.
- Antwort und Quellen werden angezeigt.
- Ladezustände und Fehler sind verständlich.
- UI wirkt ruhig, modern und portfolio-tauglich.

### Phase 5: Tauri Desktop App

- Tauri ist eingerichtet.
- App startet lokal unter Windows.
- Frontend funktioniert in der Desktop-Hülle.
- Entwicklungsstart und Build-Prozess sind dokumentiert.
- Sicherheitskonfiguration ist geprüft.
- Offene Punkte für echten Release-Build stehen in der Roadmap.

### Phase 6: Portfolio Polish

- README erklärt Zweck, Stack, Setup und Roadmap.
- Architektur-, API-, RAG- und Setup-Dokumentation sind aktuell.
- Tests sind beschrieben.
- Datenschutz-Hinweis ist klar.
- Screenshots oder Platzhalter sind vorbereitet.
- Projektstruktur und Git-Historie wirken professionell.
