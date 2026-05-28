# Git Workflow

## Branch-Empfehlung

Für kleine Projekte reicht ein einfacher Workflow:

- `main`: stabiler Stand
- `feature/<kurzer-name>`: neue Features
- `fix/<kurzer-name>`: Bugfixes
- `docs/<kurzer-name>`: reine Dokumentationsänderungen

Beispiele:

```bash
git checkout -b feature/rag-chunking
git checkout -b fix/pdf-upload-error
git checkout -b docs/roadmap-update
```

## Reihenfolge pro Feature

1. `git status` prüfen.
2. Ziel und betroffene Dateien klären.
3. Kleine Änderung umsetzen.
4. Tests oder passende Checks ausführen.
5. `git diff` prüfen.
6. Dokumentation aktualisieren, wenn nötig.
7. Commit erstellen.

## Änderungen ansehen

```bash
git status
git diff
```

## Dateien hinzufügen

Gezielt hinzufügen ist besser als blind alles zu übernehmen:

```bash
git add docs/project-plan.md
git add backend/services/chunking_service.py
```

Wenn bewusst alles geprüft wurde:

```bash
git add .
```

## Commit-Konvention

Empfohlene Präfixe:

- `feat:` neues Feature
- `fix:` Bugfix
- `docs:` Dokumentation
- `test:` Tests
- `refactor:` Strukturverbesserung ohne neues Verhalten
- `chore:` Wartung

## Beispiel-Commits

```bash
git commit -m "docs: update project roadmap"
git commit -m "feat: add pdf chunking service"
git commit -m "test: cover empty pdf upload"
git commit -m "fix: handle missing ollama model"
```

## Tests vor Commit

Vor Backend-Commits:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest
```

Vor Frontend-Commits später:

```powershell
cd frontend
npm test
```

## README vor größerem Commit aktualisieren

README oder `docs/` aktualisieren, wenn sich eines davon ändert:

- Setup
- API-Endpunkte
- Architektur
- Roadmap
- neue Dependencies
- wichtige technische Entscheidungen

## Sicherer Ablauf mit Codex

1. Vorher `git status` prüfen.
2. Codex nur eine kleine Aufgabe geben.
3. Bei größeren Änderungen erst Plan bestätigen.
4. Danach `git diff` lesen.
5. Tests ausführen.
6. Commit erstellen.
