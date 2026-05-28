# Learning Notes

Diese Datei sammelt kurze Lernnotizen zu den wichtigsten Technologien in Documind.

## FastAPI

FastAPI ist ein Python-Framework für APIs. Es passt gut zu Documind, weil Requests und Responses mit Type Hints und Pydantic-Modellen klar beschrieben werden können.

Wichtige Konzepte:

- `FastAPI()` erstellt die App.
- `APIRouter` gruppiert Endpunkte.
- Pydantic validiert Request- und Response-Daten.
- Swagger UI ist lokal unter `/docs` erreichbar.
- Async-Funktionen sind sinnvoll für Datei- und HTTP-Arbeit.

## PyMuPDF

PyMuPDF wird über `fitz` importiert und liest PDF-Dateien.

Documind nutzt PyMuPDF für:

- Seitenanzahl
- Text pro Seite
- vollständigen Dokumenttext

Grenzen:

- Gescannte PDFs enthalten oft keinen normalen Text.
- Dafür wäre später OCR nötig.
- Manche PDFs haben eine schwierige Text-Reihenfolge.

## Ollama

Ollama führt Sprachmodelle lokal aus. Documind nutzt Ollama, damit keine PDF-Inhalte an externe KI-Dienste gesendet werden.

Wichtig:

- Standardadresse: `http://127.0.0.1:11434`
- Modell laden: `ollama pull llama3`
- Antwort-Endpunkt: `/api/generate`
- Tests sollten Ollama mocken

## RAG

RAG bedeutet Retrieval Augmented Generation. Das System sucht passende Textstellen und gibt nur diese als Kontext an das Modell.

In Documind:

1. PDF-Text extrahieren.
2. Text in Chunks teilen.
3. Chunks in Embeddings umwandeln.
4. Embeddings in ChromaDB speichern.
5. Bei Fragen relevante Chunks suchen.
6. Ollama mit gefundenem Kontext antworten lassen.

## ChromaDB

ChromaDB ist eine lokale Vektordatenbank. Sie speichert Embeddings und Metadaten.

Für Documind wichtig:

- Speicherung lokal unter `local_data/chroma/`
- Suche nach ähnlichen Textstellen
- Metadaten für Quellenangaben
- nicht in Git committen

## Embeddings

Embeddings sind Zahlenvektoren für Text. Ähnliche Texte haben ähnliche Vektoren.

Documind braucht Embeddings, um passende PDF-Abschnitte zu einer Frage zu finden.

Wichtig:

- lokal erzeugen
- nicht über externe APIs
- Modellwahl dokumentieren
- Embedding Service testbar halten

## Testing

Tests sind wichtig für Qualitätssicherung und spätere Änderungen.

Aktuelle Testarten:

- API Tests mit FastAPI TestClient
- Service Tests für Prompt und Ollama
- Upload- und Extraktions-Tests
- Mocks für externe lokale Prozesse wie Ollama

Gute Tests prüfen:

- normale Erfolgspfade
- klare Fehlerfälle
- lokale Speicherung
- keine echten KI-Aufrufe in Unit Tests

## React später

React wird für die Desktop-first Oberfläche genutzt.

Geplante UI-Bereiche:

- Sidebar
- Dokumentenliste
- Upload
- Fragefeld
- Antwortbereich
- Quellenbereich

TypeScript hilft, API-Daten klar zu typisieren.

## Tauri später

Tauri verpackt das React Frontend als Desktop-App. Für Documind ist Tauri interessant, weil es schlanker als Electron ist und gut zu einer lokalen App passt.

Offen bleibt später:

- Wie Backend und Frontend gemeinsam gestartet werden
- Wie Builds für Windows erzeugt werden
- Welche Sicherheitsregeln in Tauri nötig sind
