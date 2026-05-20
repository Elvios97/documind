# Codex Rules

Diese Datei enthält feste Regeln für die Arbeit an Documind.

## Grundregeln

- Erst analysieren, dann planen, dann umsetzen.
- Vor Änderungen kurz erklären, welche Dateien betroffen sind.
- Keine großen Umbauten ohne Bestätigung.
- Bestehende Funktionalität nicht entfernen, außer es wurde ausdrücklich gewünscht.
- Änderungen klein, nachvollziehbar und testbar halten.
- Wenn komplette Datei-Inhalte angefordert werden, vollständige Dateien liefern.
- Keine unnötigen Dependencies hinzufügen.
- Keine Secrets, API Keys oder Tokens in Dateien schreiben.
- Keine absoluten lokalen Pfade in Code oder Dokumentation fest einbauen.
- Keine Cloud-Funktionalität einbauen.
- Keine externen KI-APIs einbauen.
- Keine Online-Speicherung, kein Login und keine Synchronisation ergänzen.
- Bestehende Projektstruktur beachten.

## Technische Regeln

- Python-Code mit Type Hints schreiben.
- Pydantic-Modelle für API-Daten nutzen.
- API, Services, Storage und Models sauber trennen.
- Wiederverwendbare Logik in Services auslagern.
- Kommentare nur dort einsetzen, wo sie echte Orientierung geben.
- Fehler verständlich und kontrolliert behandeln.
- Lokale Daten unter `local_data/` oder klar dokumentierten lokalen Ordnern speichern.
- Für wichtige Funktionen Tests ergänzen.
- Tests nicht löschen, nur damit der Build grün wird.

## Dokumentationsregeln

- Wichtige Änderungen kurz erklären:
  - Was wurde geändert?
  - Warum wurde es geändert?
  - Welche Dateien wurden geändert?
  - Wie kann es getestet werden?
- Wichtige technische Entscheidungen in `docs/entscheidungen.md` dokumentieren.
- Gelöste oder relevante Fehler in `docs/fehlerlog.md` dokumentieren.
- Bei API-Änderungen `docs/api.md` aktualisieren.
- Bei Architekturänderungen `docs/architecture.md` aktualisieren.
- Bei Setup-Änderungen `docs/setup.md` aktualisieren.

## Arbeitsweise

1. Anforderungen lesen.
2. Relevante Dateien suchen.
3. Problem oder Ziel kurz erklären.
4. Kurzen Plan erstellen.
5. Bei größeren Änderungen auf Bestätigung warten.
6. Änderungen klein umsetzen.
7. Tests oder Checks ausführen.
8. Ergebnis verständlich zusammenfassen.

## Fehlerbehebung

Bei Fehlern:

- Fehlermeldung vollständig verstehen.
- Ursache erklären.
- Eine kleine Lösung vorschlagen.
- Keine blinden Massenänderungen.
- Wenn mehrere Ursachen möglich sind, zuerst die wahrscheinlichste prüfen.
- Nach dem Fix passenden Test ausführen oder nennen.

## Projektfokus

Documind ist lokal, datenschutzfreundlich und portfolio-tauglich. Jede Änderung soll dieses Ziel unterstützen.
