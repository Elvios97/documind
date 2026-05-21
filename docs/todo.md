# Todo

## Aktuelle Priorität

Phase 4-Grundfunktion ist getestet. Dokumentliste, Details und lokales Löschen sind angebunden.

## Nächster sinnvoller Schritt

1. Frontend einmal komplett testen: Reload, Upload, Frage, Quellen, Löschen.
2. UI bei Bedarf glätten.
3. Danach Phase-4-Stand committen oder hochladen.

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

- [ ] Tauri Setup prüfen
- [ ] Windows-Entwicklungsstart dokumentieren
- [ ] Frontend in Tauri starten
- [ ] Backend-Startstrategie klären
- [ ] Build-Prozess dokumentieren
- [ ] Sicherheitskonfiguration prüfen

## Phase 6: Portfolio Polish

- [ ] README finalisieren
- [ ] Screenshots oder Platzhalter ergänzen
- [ ] Datenschutz-Hinweis schärfen
- [ ] Roadmap aktuell halten
- [ ] API-Doku nach jedem neuen Endpoint aktualisieren
- [ ] Fehlerlog bei echten Problemen pflegen
- [ ] Entscheidungen bei Architekturänderungen ergänzen
- [ ] Tests vor größeren Commits ausführen
