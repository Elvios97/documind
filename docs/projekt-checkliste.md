# Projekt-Checkliste

## Portfolio-Qualität

- [x] Projektziel ist in README und `docs/project-plan.md` klar beschrieben
- [x] MVP-Scope ist realistisch abgegrenzt
- [x] Nicht-Ziele sind sichtbar dokumentiert
- [x] Roadmap zeigt klare Phasen
- [x] Datenschutzprinzipien sind verständlich erklärt
- [x] Architektur ist mit einfacher Grafik dokumentiert
- [x] API-Dokumentation enthält Beispiele
- [x] RAG-Konzept ist nachvollziehbar erklärt
- [ ] Screenshots oder Platzhalter sind vorbereitet
- [ ] Projekt wirkt für GitHub sauber und fokussiert

## Backend

- [x] FastAPI App startet lokal
- [x] Healthcheck vorhanden
- [x] PDF Upload vorhanden
- [x] PDF-Speicherung lokal
- [x] Textextraktion mit PyMuPDF
- [x] Dokumentdaten lokal als JSON
- [x] Fehlerbehandlung für Upload
- [x] Ollama Service vorhanden
- [x] Ask Endpoint vorhanden
- [x] RAG Endpoint vorhanden
- [x] ChromaDB lokal eingebunden
- [ ] API-Versionierung später prüfen

## Tests

- [x] pytest eingerichtet
- [x] Tests für PDF Upload
- [x] Tests für Prompt Service
- [x] Tests für Ollama Service mit Mock
- [x] Tests für Ask API
- [ ] Tests für kaputte PDFs erweitern
- [x] Tests für Chunking ergänzen
- [x] Tests für Retrieval ergänzen
- [x] Tests für RAG-Service ergänzen
- [ ] Frontend-Tests später prüfen

## Dokumentation

- [x] `docs/project-plan.md` gepflegt
- [x] `docs/roadmap.md` gepflegt
- [x] `docs/setup.md` gepflegt
- [x] `docs/api.md` gepflegt
- [x] `docs/architecture.md` gepflegt
- [x] `docs/rag.md` gepflegt
- [x] `docs/codex-rules.md` gepflegt
- [x] `docs/codex-prompts.md` gepflegt
- [x] README bei größeren Änderungen aktualisieren
- [x] Entscheidungen bei Architekturänderungen ergänzen
- [ ] Fehlerlog bei echten Fehlern ergänzen

## Lokale Ausführung

- [x] Python-Version geprüft
- [x] virtuelle Umgebung erstellt
- [x] Requirements installiert
- [x] Backend startet mit Uvicorn
- [x] Swagger UI erreichbar
- [x] Ollama installiert
- [x] lokales Modell geladen
- [x] `/ask` mit lokalem Modell getestet
- [x] Tests lokal ausgeführt
- [x] Frontend lokal gestartet
- [x] Tauri lokal gestartet
- [x] Tauri Windows-Installer lokal gebaut

## Vor GitHub-Veröffentlichung

- [ ] `git status` prüfen
- [ ] keine Secrets im Repository
- [x] keine lokalen PDFs committen
- [x] keine ChromaDB-Daten committen
- [x] ältere `main`-Historie enthält keine lokalen Dokument- oder Chroma-Daten
- [ ] keine virtuellen Umgebungen committen
- [x] `.gitignore` prüfen
- [ ] README final lesen
- [ ] Setup-Anleitung frisch testen
- [ ] Tests ausführen
- [ ] Roadmap aktualisieren
- [ ] Commit-Historie grob prüfen
