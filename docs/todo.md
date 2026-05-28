# Todo

## Aktuelle Priorität

Phase 5 ist lokal getestet: Die Tauri-Desktop-App startet unter Windows und der PDF-/Frage-Workflow funktioniert in der Desktop-Hülle. Die zuvor versionierten lokalen Dokument- und Chroma-Daten wurden aus der veröffentlichten `main`-Historie entfernt.

## Nächster sinnvoller Schritt

1. README und Projekt-Checkliste final durchgehen.
2. Screenshot der laufenden Desktop-App vorbereiten.
3. MVP-Abschluss und GitHub-Präsentation final prüfen.

## Phase 1: Backend-Grundsystem

- [x] FastAPI Backend einrichten
- [x] Healthcheck bereitstellen
- [x] PDF Upload Endpoint bauen
- [x] PDF lokal im `backend/uploads/` Ordner speichern
- [x] PDF-Dateityp prüfen
- [x] leere Uploads ablehnen
- [x] ungültige PDF-Dateien ablehnen
- [x] Text pro Seite mit PyMuPDF extrahieren
- [x] Seitenanzahl erkennen
- [x] Dokument-ID erzeugen
- [x] Dokumentdaten lokal als JSON speichern
- [x] Tests für Upload und Textextraktion ergänzen
- [ ] zusätzliche Tests für kaputte PDFs prüfen

## Phase 2: Lokale Ollama-Integration

- [x] Ollama Service bauen
- [x] Modell über Umgebungsvariable konfigurierbar machen
- [x] Prompt Service bauen
- [x] `POST /ask` Endpoint bereitstellen
- [x] gespeicherten PDF-Text laden
- [x] leere Fragen ablehnen
- [x] fehlende Dokumente sauber melden
- [x] Fehler für nicht erreichbares Ollama behandeln
- [x] Fehler für fehlendes Modell behandeln
- [x] Ollama-Aufrufe in Tests mocken
- [x] Setup für Ollama dokumentieren
- [x] Phase-2-End-to-End-Test mit laufender App und Ollama prüfen

## Phase 3: Lokales RAG-System

- [x] Chunk-Datenmodell definieren
- [x] Chunking Service bauen
- [x] Chunk-Größe konfigurierbar machen
- [x] Chunk Overlap unterstützen
- [x] Seitenzahlen in Chunks behalten
- [x] Tests für Chunking ergänzen
- [x] lokales Embedding-Modell auswählen
- [x] Embedding Service bauen
- [x] Tests für Embedding Service ergänzen
- [x] ChromaDB Dependency ergänzen
- [x] Vector Store Service bauen
- [x] Tests für Vector Store ergänzen
- [x] Indexing Service für Chunking, Embeddings und Vector Store bauen
- [x] Tests für Indexing Service ergänzen
- [x] PDF nach Upload automatisch indexieren
- [x] Top-K Retrieval bauen
- [x] RAG Prompt Service ergänzen
- [x] `POST /rag/ask` Endpoint bauen
- [x] Quellenangaben zurückgeben
- [x] Tests für Retrieval und RAG-Service ergänzen

## Phase 4: React Desktop UI

- [x] Vite React TypeScript Projekt einrichten
- [x] API Client für Backend bauen
- [x] Desktop-first Layout planen
- [x] Sidebar bauen
- [x] PDF Upload Komponente bauen
- [x] Dokumentenliste bauen
- [x] Persistente Dokumentenliste aus Backend laden
- [x] Dokumentdetails Endpoint bauen
- [x] Dokument lokal löschen Endpoint bauen
- [x] Dokument lokal aus UI löschen
- [x] Fragefeld bauen
- [x] Antwortanzeige bauen
- [x] Quellenanzeige bauen
- [x] Ladezustände ergänzen
- [x] Fehlermeldungen ergänzen
- [x] Browser-End-to-End-Test durchführen
- [x] UI nach echtem Test nachschärfen
- [x] Backend-Erreichbarkeitsanzeige ergänzen

## Phase 5: Tauri Desktop App

- [x] Tauri Setup prüfen
- [x] Tauri CLI und `src-tauri/` Grundstruktur einrichten
- [x] Windows-Entwicklungsstart dokumentieren
- [x] Frontend in Tauri starten und lokal prüfen
- [x] Backend-Startstrategie klären
- [x] Build-Prozess dokumentieren
- [x] Sicherheitskonfiguration prüfen
- [x] Windows-Installer-Build lokal erzeugen
- [ ] Backend-Bündelung für einen späteren eigenständigen Release entscheiden

## Phase 6: Dokumentation und Release Polish

- [x] README finalisieren
- [x] Screenshots oder Platzhalter ergänzen
- [x] Datenschutz-Hinweis schärfen
- [x] Screenshot-tauglichen UI-Stand vorbereiten
- [x] `.gitignore` für lokale Dokument- und Chroma-Daten korrigieren
- [x] Bereits versionierte lokale Dokument- und Chroma-Daten aus der Git-Historie entfernen
- [x] Roadmap aktuell halten
- [ ] API-Doku nach jedem neuen Endpoint aktualisieren
- [ ] Fehlerlog bei echten Problemen pflegen
- [x] Entscheidungen bei Architekturänderungen ergänzen
- [x] Tests vor größeren Commits ausführen
