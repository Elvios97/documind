# documind - Roadmap

## Phase 1: Projektstruktur + PDF Upload ✅ AKTUELL
- [x] Projektstruktur aufsetzen
- [x] FastAPI Backend grundgerüst
- [x] Healthcheck Endpunkt
- [x] PDF Upload Endpunkt
- [x] PDF Service (Geschäftslogik)
- [x] Requirements & Dokumentation
- [x] Git initialisierung

**Dauer**: 1-2 Tage
**Abhängigkeiten**: Keine

---

## Phase 2: PDF Text Extraktion
- [ ] PyMuPDF Integration
- [ ] PDF Read Endpunkt
- [ ] Text Extraction Service
- [ ] Fehlerbehandlung für beschädigte PDFs
- [ ] Tests für Extraktion
- [ ] Dokumentation

**Dauer**: 2-3 Tage
**Abhängigkeiten**: Phase 1

---

## Phase 3: Ollama Integration (Lokale KI)
- [ ] Ollama Installation & Setup Doku
- [ ] Ollama API Client
- [ ] LLM Query Endpunkt
- [ ] Prompt Engineering Grundlagen
- [ ] Response Streaming
- [ ] Tests

**Dauer**: 2-3 Tage
**Abhängigkeiten**: Phase 2

---

## Phase 4: Chunking + Embeddings
- [ ] Text Chunking Logik
- [ ] Embedding Model Integration
- [ ] Embedding Service
- [ ] Batch Processing für große PDFs
- [ ] Performance Optimierung
- [ ] Tests

**Dauer**: 3-4 Tage
**Abhängigkeiten**: Phase 3

---

## Phase 5: ChromaDB + RAG
- [ ] ChromaDB Installation
- [ ] Vector Store Integration
- [ ] RAG Pipeline Implementation
- [ ] Context Retrieval Logik
- [ ] Relevance Scoring
- [ ] Tests & Evaluation

**Dauer**: 3-4 Tage
**Abhängigkeiten**: Phase 4

---

## Phase 6: React UI
- [ ] React 18 + TypeScript Projekt
- [ ] Vite Setup
- [ ] PDF Upload Component
- [ ] Chat Interface
- [ ] API Client Integration
- [ ] UI/UX Polish
- [ ] Responsive Design

**Dauer**: 4-5 Tage
**Abhängigkeiten**: Phase 5

---

## Phase 7: Tauri Desktop App
- [ ] Tauri Setup
- [ ] Backend Integration in App
- [ ] Building & Packaging
- [ ] Auto-Update Logik
- [ ] Installer für Windows/macOS/Linux

**Dauer**: 2-3 Tage
**Abhängigkeiten**: Phase 6

---

## Phase 8: Portfolio Demo & Polish
- [ ] Demo Scenario erstellen
- [ ] Performance Tuning
- [ ] Error Messages verbessern
- [ ] Doku finalisieren
- [ ] GitHub README
- [ ] Demo Video erstellen (optional)
- [ ] Release Vorbereitung

**Dauer**: 2-3 Tage
**Abhängigkeiten**: Phase 7

---

## Gesamtgeschätzter Zeitaufwand

- **Mindestens**: 20-25 Tage (wenn alles glatt läuft)
- **Realistisch**: 30-40 Tage (mit Testing, Debugging, Iteration)
- **Mit Pausen**: 6-8 Wochen

## Priorität & MVP

### MVP (Minimum Viable Product)
- Phase 1-5: Funktionierendes RAG System über CLI
- Kann über curl getestet werden

### Core Features
- Phase 1-6: Voll funktionale Desktop App

### Polish & Extras
- Phase 7-8: Production-ready Anwendung
