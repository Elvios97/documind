# Projekt-Checkliste

## Portfolio-Qualität

- [ ] Projektziel ist in README und `docs/project-plan.md` klar beschrieben
- [ ] MVP-Scope ist realistisch abgegrenzt
- [ ] Nicht-Ziele sind sichtbar dokumentiert
- [ ] Roadmap zeigt klare Phasen
- [ ] Datenschutzprinzipien sind verständlich erklärt
- [ ] Architektur ist mit einfacher Grafik dokumentiert
- [ ] API-Dokumentation enthält Beispiele
- [ ] RAG-Konzept ist nachvollziehbar erklärt
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
- [ ] README bei größeren Änderungen aktualisieren
- [ ] Entscheidungen bei Architekturänderungen ergänzen
- [ ] Fehlerlog bei echten Fehlern ergänzen

## Lokale Ausführung

- [ ] Python-Version geprüft
- [ ] virtuelle Umgebung erstellt
- [ ] Requirements installiert
- [ ] Backend startet mit Uvicorn
- [ ] Swagger UI erreichbar
- [ ] Ollama installiert
- [ ] lokales Modell geladen
- [ ] `/ask` mit lokalem Modell getestet
- [ ] Tests lokal ausgeführt
- [ ] später Frontend lokal gestartet
- [ ] später Tauri lokal gestartet

## Vor GitHub-Veröffentlichung

- [ ] `git status` prüfen
- [ ] keine Secrets im Repository
- [ ] keine lokalen PDFs committen
- [ ] keine ChromaDB-Daten committen
- [ ] keine virtuellen Umgebungen committen
- [ ] `.gitignore` prüfen
- [ ] README final lesen
- [ ] Setup-Anleitung frisch testen
- [ ] Tests ausführen
- [ ] Roadmap aktualisieren
- [ ] Commit-Historie grob prüfen
