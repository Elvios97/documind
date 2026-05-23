# Fehlerlog

Hier werden relevante Fehler, Ursachen und Lösungen dokumentiert. Nicht jeder kleine Tippfehler muss eingetragen werden. Wichtig sind Fehler, aus denen man später lernen kann.

## Vorlage

### Datum

YYYY-MM-DD

### Problem

Kurz beschreiben, was nicht funktioniert hat.

```text
Fehlermeldung oder auffälliges Verhalten hier einfügen
```

### Kontext

- Wann tritt der Fehler auf?
- Welche Aktion wurde ausgeführt?
- Welche Datei oder Funktion ist betroffen?
- Was wurde kurz vorher geändert?

### Ursache

Kurz erklären, warum der Fehler passiert ist.

### Lösung

Kurz erklären, wie der Fehler behoben wurde.

### Betroffene Dateien

- `pfad/zur/datei.py`
- `docs/beispiel.md`

### Tests oder Checks

- [ ] Test ausgeführt
- [ ] App lokal gestartet
- [ ] manueller API-Check durchgeführt
- [ ] noch offen

### Learning

Was sollte beim nächsten Mal beachtet werden?

## Einträge

### Datum

2026-05-23

### Problem

Lokale Laufzeitdaten aus PDF-Tests wurden in früheren Commits verfolgt und nach GitHub übertragen.

```text
local_data/documents/*.json
local_data/chroma/*
backend/.pytest_tmp/*
```

### Kontext

- Der Fehler wurde vor dem Upload der Tauri-Phase bei der Prüfung von `git status` und `git log` entdeckt.
- Dokument-JSONs können extrahierten PDF-Text enthalten.
- ChromaDB-Dateien können lokal erzeugte Vektordaten enthalten.

### Ursache

Die Datenordner waren für die lokale Ausführung angelegt, einzelne Laufzeitdateien wurden aber bereits committet, bevor die Ignore-Regeln vollständig griffen.

### Lösung

- `.gitignore` schließt Dokument-JSONs, ChromaDB-Dateien und pytest-Laufzeitdaten künftig aus.
- Bereits verfolgte Laufzeitdateien werden aus dem Git-Index und aus der veröffentlichten Git-Historie entfernt.
- Lokale Nutzerdaten werden vor der Bereinigung in einem ignorierten lokalen Ordner gesichert.

### Betroffene Dateien

- `.gitignore`
- `docs/todo.md`
- `docs/projekt-checkliste.md`
- `docs/fehlerlog.md`

### Tests oder Checks

- [x] Verfolgte Laufzeitdaten mit `git ls-files` identifiziert
- [x] Neue Laufzeitdaten mit `git check-ignore` geprüft
- [x] Lokale Dokument- und Chroma-Daten vor der Bereinigung gesichert
- [ ] Bereinigte Git-Historie und GitHub-Stand geprüft

### Learning

Lokale Datenordner müssen vor dem ersten echten App-Test vollständig ignoriert werden. Vor jedem öffentlichen Push ist ein kurzer Check mit `git status` und `git ls-files local_data` sinnvoll.
