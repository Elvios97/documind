# Codex Prompts

Diese Prompts helfen, Codex im Projekt konsistent zu nutzen.

## Master-Prompt

```text
Lies zuerst docs/codex-rules.md und docs/project-plan.md.
Analysiere das Projekt.
Erstelle einen kurzen Plan.
Ändere noch keine Dateien, bevor ich bestätige.
Beachte: Documind bleibt lokal. Keine Cloud, keine externen KI-APIs, keine Online-Speicherung.
```

## Phase-1-Prompt: Backend-Grundsystem

```text
Lies docs/codex-rules.md, docs/project-plan.md und docs/api.md.
Hilf mir bei Phase 1: FastAPI Backend, PDF Upload, lokale Speicherung und PyMuPDF Textextraktion.
Erstelle zuerst einen kurzen Plan.
Achte auf Type Hints, saubere Fehlerbehandlung und pytest Tests.
```

## Phase-2-Prompt: Lokale Ollama-Integration

```text
Lies docs/codex-rules.md, docs/project-plan.md und docs/setup.md.
Hilf mir bei Phase 2: lokale Ollama-Integration und POST /ask.
Ollama darf nur lokal genutzt werden.
Erstelle zuerst einen kurzen Plan.
Mocke Ollama in Tests.
```

## Phase-3-Prompt: Lokales RAG-System

```text
Lies docs/codex-rules.md, docs/project-plan.md und docs/rag.md.
Hilf mir bei Phase 3: Chunking, lokale Embeddings, ChromaDB und POST /rag/ask.
Alles muss lokal bleiben.
Erstelle zuerst einen kurzen Plan.
Beginne mit einem kleinen, testbaren Schritt.
```

## Phase-4-Prompt: React Desktop UI

```text
Lies docs/codex-rules.md, docs/project-plan.md und docs/api.md.
Hilf mir bei Phase 4: React + TypeScript + Vite Desktop UI.
Baue eine ruhige Desktop-first Oberfläche mit PDF Upload, Dokumentenliste, Fragefeld, Antwortanzeige und Quellenanzeige.
Erstelle zuerst einen kurzen Plan.
```

## Phase-5-Prompt: Tauri Desktop App

```text
Lies docs/codex-rules.md, docs/project-plan.md und docs/setup.md.
Hilf mir bei Phase 5: Tauri Desktop App für Windows.
Halte die Umsetzung klein und dokumentiere Entwicklungsstart und Build-Prozess.
Erstelle zuerst einen kurzen Plan.
```

## Dokumentations-Polish-Prompt

```text
Lies docs/codex-rules.md und alle Dateien in docs/.
Prüfe, ob Documind auf GitHub professionell wirkt.
Verbessere Dokumentation, Roadmap, Setup und README realistisch und knapp.
Keine neuen Features einbauen.
```

## Prompt für Bugfixing

```text
Lies zuerst docs/codex-rules.md.
Analysiere diesen Fehler.
Erkläre mir die wahrscheinliche Ursache.
Erstelle einen kleinen Fix-Plan.
Ändere noch keine Dateien, bevor ich bestätige.

Fehler:
[FEHLER HIER EINFÜGEN]
```

## Prompt für Tests

```text
Lies docs/codex-rules.md und prüfe die vorhandenen Tests.
Schlage sinnvolle Tests für diese Funktion vor.
Erstelle zuerst einen Testplan.
Danach ergänze nur kleine, zielgerichtete Tests.

Funktion:
[FUNKTION HIER BESCHREIBEN]
```

## Prompt für README-Verbesserung

```text
Lies README.md und docs/project-plan.md.
Verbessere die README für eine öffentliche Projektpräsentation.
Sie soll Zweck, Features, lokalen Datenschutz, Stack, Setup, Tests und Roadmap erklären.
Keine übertriebenen Buzzwords.
```
