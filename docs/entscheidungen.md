# Entscheidungen

Diese Datei dokumentiert wichtige technische Entscheidungen im Projekt.

## Entscheidung: Lokal statt Cloud

Datum: 2026-05-20

Documind verarbeitet PDFs, extrahierte Texte, Vektordaten und spätere Chatdaten lokal.

Begründung:

- PDFs können private oder sensible Inhalte enthalten.
- Lokale Verarbeitung passt zum Datenschutz-Ziel des Projekts.
- Keine laufenden Kosten für externe KI-APIs.
- Weniger Abhängigkeit von fremden Diensten.

Alternativen:

- Cloud-Speicher
- externe KI-APIs
- gehostete Datenbank

Diese Alternativen sind nicht Teil des MVP.

## Entscheidung: Desktop-first

Datum: 2026-05-20

Documind wird zuerst für den lokalen Desktop entwickelt, besonders für Windows.

Begründung:

- Das Projekt soll vollständig lokal auf dem eigenen Rechner laufen.
- Desktop passt gut zu PDF-Arbeit und lokalen Dateien.
- Tauri kann später eine echte Desktop-App bereitstellen.

Alternativen:

- Web-App mit Serverbetrieb
- Mobile-first App
- Browser-only Tool

## Entscheidung: FastAPI Backend

Datum: 2026-05-20

Das Backend wird mit FastAPI umgesetzt.

Begründung:

- Gute Unterstützung für moderne Python APIs.
- Pydantic-Modelle passen zu klaren Request- und Response-Daten.
- Automatische OpenAPI-Dokumentation hilft beim Testen.
- Async HTTP-Aufrufe zu Ollama sind einfach möglich.

Alternativen:

- Flask
- Django
- Node.js Backend

## Entscheidung: React + später Tauri

Datum: 2026-05-20

Das Frontend wird mit React, TypeScript und Vite geplant. Tauri folgt später für die Desktop-App.

Begründung:

- React ist gut für eine interaktive PDF- und Chat-Oberfläche geeignet.
- TypeScript macht UI-Datenflüsse klarer.
- Vite ist schnell und einfach.
- Tauri ermöglicht später eine leichte Desktop-Hülle.

Alternativen:

- Flutter
- Electron
- reine Server-rendered UI

## Entscheidung: Ollama

Datum: 2026-05-20

Documind nutzt Ollama für lokale LLM-Antworten.

Begründung:

- Modelle laufen lokal.
- Keine externen KI-APIs nötig.
- Einfache lokale HTTP-API.
- Gute Grundlage für lokale Demos und manuelle Tests.

Alternativen:

- OpenAI API
- Anthropic API
- lokal selbst gehostete Modellserver

Externe APIs sind wegen des lokalen Projektziels ausgeschlossen.

## Entscheidung: ChromaDB

Datum: 2026-05-20

Für das lokale RAG-System ist ChromaDB als lokale Vektordatenbank geplant.

Begründung:

- ChromaDB ist für lokale RAG-Prototypen gut geeignet.
- Persistenz unter `local_data/chroma/` passt zur Projektstruktur.
- Metadaten wie Dokument-ID, Seite und Chunk-ID können gespeichert werden.

Alternativen:

- FAISS
- SQLite mit Vektor-Erweiterung
- eigener In-Memory Store

## Entscheidung: PyMuPDF

Datum: 2026-05-20

Documind nutzt PyMuPDF für PDF-Textextraktion.

Begründung:

- Gute Text-Extraktion aus vielen PDFs.
- Seitenweises Lesen ist einfach.
- Seitenanzahl und Text pro Seite lassen sich sauber erfassen.
- Passt gut zu Python und FastAPI.

Alternativen:

- pdfplumber
- pypdf
- OCR-basierte Verarbeitung

OCR ist später optional, aber nicht Teil des aktuellen MVP.

## Entscheidung: Tauri startet zuerst ohne Backend-Autostart

Datum: 2026-05-22

Der erste Tauri-Stand verpackt das React-Frontend. FastAPI und Ollama werden für Entwicklung und Tests weiterhin separat lokal gestartet.

Begründung:

- Der bestehende lokale Backend-Flow ist bereits getestet.
- Ein automatischer Python-Backend-Start im Desktop-Build erhöht Packaging- und Fehlerkomplexität.
- Die Tauri-Hülle kann so zuerst sauber geprüft werden.
- Eine spätere Build-Strategie kann bewusst entschieden und dokumentiert werden.
