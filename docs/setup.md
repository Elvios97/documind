# Lokales Setup

Diese Anleitung richtet sich zuerst an Windows und PowerShell.

## Voraussetzungen

- Windows-PC
- Python 3.11 oder neuer
- Git
- Ollama für Windows
- Node.js für das Frontend
- Rust für Tauri
- Microsoft C++ Build Tools mit "Desktop development with C++" für Tauri unter Windows
- Microsoft Edge WebView2 Runtime für Tauri unter Windows

## Python Setup

Im Projektordner:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`requirements.txt` installiert auch ChromaDB für das lokale RAG-System.

## Virtuelle Umgebung aktivieren

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
```

Wenn PowerShell Skripte blockiert, muss die lokale Execution Policy geprüft werden. Nur Änderungen vornehmen, wenn klar ist, was sie bewirken.

## Backend starten

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Tests starten

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest
```

Die Ollama-Tests sind gemockt und benötigen keinen laufenden Ollama-Server.

Frontend-Tests und Produktions-Build:

```powershell
cd frontend
npm.cmd test
npm.cmd run build
```

## Ollama installieren und starten

Ollama für Windows installieren:

```text
https://ollama.com/download/windows
```

Nach der Installation sollte Ollama lokal erreichbar sein:

```text
http://127.0.0.1:11434
```

## Modell laden

Documind nutzt standardmäßig `llama3` für Antworten.

```powershell
ollama pull llama3
```

Für lokale Embeddings nutzt Documind standardmäßig `nomic-embed-text`:

```powershell
ollama pull nomic-embed-text
```

Optional testen:

```powershell
ollama run llama3
```

Ein anderes Modell kann für die aktuelle PowerShell-Session gesetzt werden:

```powershell
$env:DOCUMIND_OLLAMA_MODEL="llama3"
```

Ein anderes Embedding-Modell kann separat gesetzt werden:

```powershell
$env:DOCUMIND_EMBEDDING_MODEL="nomic-embed-text"
```

## PDF hochladen

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/pdf/upload" `
  -F "file=@C:\Pfad\zu\deiner-datei.pdf"
```

Die Response enthält eine `document_id`.

## Frage stellen

```powershell
curl.exe -X POST "http://127.0.0.1:8000/ask" `
  -H "Content-Type: application/json" `
  -d "{\"document_id\":\"DEINE_DOCUMENT_ID\",\"question\":\"Worum geht es in diesem Dokument?\"}"
```

## Frontend starten

Das Frontend liegt unter `frontend/`. Die Dokumentenliste wird aus `GET /documents` geladen.

```powershell
cd frontend
npm install
npm run dev
```

App:

```text
http://127.0.0.1:5174
```

## Tauri Desktop-Hülle starten

Die Tauri-Grundstruktur liegt unter `frontend/src-tauri/`. In der Entwicklung startet Tauri das FastAPI-Backend automatisch aus `backend/.venv`, sofern Port 8000 nicht bereits belegt ist. Ollama muss separat lokal laufen.

Vor dem ersten Start unter Windows prüfen:

- Rust ist installiert und `cargo --version` funktioniert in einer neuen PowerShell.
- Microsoft C++ Build Tools sind installiert.
- Microsoft Edge WebView2 Runtime ist vorhanden.

Dann:

```powershell
cd frontend
npm run tauri dev
```

Wenn PowerShell `npm` blockiert, kann derselbe Befehl mit `npm.cmd` ausgeführt werden:

```powershell
npm.cmd run tauri dev
```

## Windows-Release bauen

Zuerst wird das Python-Backend als ausführbare Datei gebaut:

```powershell
.\scripts\build-backend.ps1 -InstallBuildDependencies
```

Das Ergebnis liegt unter `backend/dist/documind-backend.exe`. Anschließend kann Tauri diese Datei als Ressource in den Installer aufnehmen:

```powershell
cd frontend
npm run tauri build
```

Der Tauri-Build erzeugt das lokale NSIS-Setup unter:

```text
frontend/src-tauri/target/release/bundle/nsis/
```

Die Build-Ausgaben sind lokal und werden nicht in Git eingecheckt.

Das NSIS-Setup enthält damit die React/Tauri-Oberfläche und das FastAPI-Backend. Ollama und die Modelle `llama3` und `nomic-embed-text` bleiben separate Voraussetzungen. Ein MSI-Build ist derzeit nicht Teil des unterstützten Releasepfads, da der lokale WiX-Packager beim Linken abbricht.

Vor einer Veröffentlichung muss der Installer auf einem sauberen Windows-System geprüft werden. Dabei sind Installation, Backend-Autostart, Ollama-Fehlermeldung, Upload, RAG-Frage, Quellenansicht und Deinstallation zu testen.

## Windows-Hinweise

- PowerShell-Beispiele nutzen Backticks für Zeilenumbrüche.
- Lokale Pfade mit Leerzeichen am besten in Anführungszeichen setzen.
- Ollama muss lokal laufen, wenn `/ask` echt getestet wird.
- Virtuelle Umgebung und lokale Daten gehören nicht in Git.
- `backend/uploads/`, `local_data/documents/` und `local_data/chroma/` enthalten lokale Daten.
- Tauri benötigt unter Windows Rust, C++ Build Tools und WebView2, bevor `tauri dev` oder `tauri build` vollständig laufen.
- Wenn ChromaDB neu ergänzt wurde, Requirements erneut installieren:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```
