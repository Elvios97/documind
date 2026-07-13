# Roadmap

## Aktueller Stand

Der lokale Einzel-Dokument-RAG-Workflow ist umgesetzt:

- PDF-Upload, Validierung und Textextraktion
- Chunking mit Seitenbezug
- lokale Embeddings über Ollama
- lokale ChromaDB-Indexierung
- RAG-Antworten mit Quellen
- React-Oberfläche und Tauri-Desktop-Hülle
- Dokumentenverwaltung und lokale PDF-Quellenansicht
- automatisierte Backend- und Frontend-Tests
- CI für Tests und Frontend-Build
- vorbereiteter Build eines gebündelten Windows-Backends

## Nächster Meilenstein: Multi-Dokument-RAG

Ziel ist, mehrere ausgewählte Dokumente gemeinsam abzufragen und zusammenzufassen. Dafür sind notwendig:

1. Auswahl mehrerer Dokument-IDs in API und UI
2. Retrieval über mehrere Dokument-Collections
3. begrenzte, ausgewogene Top-K-Auswahl über alle Dokumente
4. eindeutige Quellenzuordnung pro Dokument und Seite
5. Schutz vor zu großem Kontext und dominierenden Einzeldokumenten
6. Service-, API- und UI-Tests für gemischte Treffer und fehlende Dokumente

Dieses Feature wird getrennt umgesetzt, weil es Datenmodell, Retrieval, UI und Tests gemeinsam verändert.

## Release-Polish

- [x] professionelle Haupt-README
- [x] Architektur-, API-, RAG- und Setup-Dokumentation
- [x] Backend- und Frontend-Tests
- [x] GitHub-Actions-CI
- [x] feste Frontend-Abhängigkeitsversionen
- [x] PyInstaller-Buildpfad für `documind-backend.exe`
- [x] Tauri-Ressourcenkonfiguration für das Backend
- [ ] finale Screenshots oder kurzes Demo-GIF in der README einbinden
- [ ] NSIS-Installer auf einem sauberen Windows-System testen
- [ ] ersten GitHub Release veröffentlichen

## Spätere Features

- OCR für gescannte PDFs
- lokale Chat-Historie
- Export von Antworten und Quellen
- Modellwechsel in der UI
- Retrieval-Evaluation mit festen Testdokumenten und Fragen
- Zusammenfassungsprofile, beispielsweise kurz, ausführlich oder risikoorientiert

## Bewusste Abgrenzung

- keine Cloud-Konten oder Synchronisation
- keine externen KI-APIs
- Ollama und Modelle bleiben separate lokale Voraussetzungen
- Windows bleibt zunächst die primär unterstützte Desktop-Plattform
