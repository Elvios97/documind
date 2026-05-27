# API-Dokumentation

Basis-URL im lokalen Betrieb:

```text
http://127.0.0.1:8000
```

## Statusübersicht

| Endpoint | Status | Zweck |
| --- | --- | --- |
| `GET /` | vorhanden | Healthcheck |
| `POST /api/pdf/upload` | vorhanden | aktueller PDF Upload |
| `POST /documents/upload` | geplant | zukünftiger einheitlicher Upload Endpoint |
| `GET /documents` | vorhanden | Dokumentenliste |
| `GET /documents/{document_id}` | vorhanden | Dokumentdetails |
| `DELETE /documents/{document_id}` | vorhanden | Dokument lokal löschen |
| `POST /ask` | vorhanden | einfache Frage über gespeicherten PDF-Text |
| `POST /rag/ask` | vorhanden | Frage über lokales RAG-System |

## GET `/`

Healthcheck für das Backend.

Beispiel-Response:

```json
{
  "status": "ok",
  "message": "Documind Backend laeuft lokal."
}
```

## POST `/api/pdf/upload`

Status: vorhanden

Aktueller Upload-Endpunkt. Lädt eine PDF hoch, speichert sie lokal und extrahiert Text mit PyMuPDF.

Request:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/pdf/upload" `
  -F "file=@C:\Pfad\zu\deiner-datei.pdf"
```

Response:

```json
{
  "document_id": "7ffdb5c4-5a42-4ee3-9aa2-47f317bdca10",
  "filename": "deiner-datei.pdf",
  "page_count": 2,
  "pages": [
    {
      "page_number": 1,
      "text": "Text der ersten Seite"
    }
  ],
  "full_text": "Gesamter extrahierter Text"
}
```

Fehlerfälle:

- `400`: keine Datei
- `400`: falscher Dateityp
- `400`: leere Datei
- `413`: PDF ist groesser als 50 MB
- `422`: ungültige PDF
- `422`: PDF ohne extrahierbaren Text
- `500`: Dokumentdaten konnten nicht gespeichert werden

Der interne Dateipfad der gespeicherten PDF wird nicht über die API ausgegeben.

## POST `/documents/upload`

Status: geplant

Zukünftiger Upload-Endpunkt mit einheitlicher Dokument-API. Kann später den aktuellen `/api/pdf/upload` Endpoint ersetzen oder ergänzen.

Geplante Response:

```json
{
  "document_id": "7ffdb5c4-5a42-4ee3-9aa2-47f317bdca10",
  "filename": "beispiel.pdf",
  "page_count": 5,
  "status": "indexed"
}
```

## GET `/documents`

Status: vorhanden

Liefert lokal gespeicherte Dokumente für die UI.

Response:

```json
[
  {
    "document_id": "7ffdb5c4-5a42-4ee3-9aa2-47f317bdca10",
    "filename": "beispiel.pdf",
    "page_count": 5,
    "created_at": "2026-05-20T12:00:00Z"
  }
]
```

## GET `/documents/{document_id}`

Status: vorhanden

Liefert Details zu einem lokal gespeicherten Dokument.

Response:

```json
{
  "document_id": "7ffdb5c4-5a42-4ee3-9aa2-47f317bdca10",
  "filename": "beispiel.pdf",
  "page_count": 5,
  "pages": [
    {
      "page_number": 1,
      "text": "Text der ersten Seite"
    }
  ]
}
```

Fehlerfälle:

- `400`: ungültige `document_id`
- `404`: Dokument wurde nicht gefunden

## DELETE `/documents/{document_id}`

Status: vorhanden

Löscht ein Dokument inklusive lokaler PDF, JSON-Daten und Vektordaten.

Response:

```json
{
  "document_id": "7ffdb5c4-5a42-4ee3-9aa2-47f317bdca10",
  "deleted": true
}
```

## POST `/ask`

Status: vorhanden

Stellt eine Frage zu einem zuvor hochgeladenen Dokument. Phase 2 nutzt dafür noch einen begrenzten Ausschnitt des vollständigen PDF-Texts.

Request:

```json
{
  "document_id": "7ffdb5c4-5a42-4ee3-9aa2-47f317bdca10",
  "question": "Worum geht es in diesem Dokument?"
}
```

Response:

```json
{
  "document_id": "7ffdb5c4-5a42-4ee3-9aa2-47f317bdca10",
  "question": "Worum geht es in diesem Dokument?",
  "answer": "Das Dokument beschreibt ...",
  "model": "llama3",
  "used_context_length": 4182
}
```

Fehlerfälle:

- `400`: Frage ist leer
- `400`: ungültige `document_id`
- `404`: Dokument wurde nicht gefunden
- `404`: Ollama-Modell ist nicht verfügbar
- `422`: gespeicherter PDF-Text ist leer
- `503`: Ollama ist lokal nicht erreichbar
- `504`: Ollama antwortet nicht rechtzeitig
- `500`: interner Fehler

## POST `/rag/ask`

Status: vorhanden

Stellt eine Frage über das lokale RAG-System. Der Endpoint sucht relevante Chunks in ChromaDB und gibt Antwort plus Quellen zurück.

Request:

```json
{
  "document_id": "7ffdb5c4-5a42-4ee3-9aa2-47f317bdca10",
  "question": "Welche Kernaussagen stehen im Dokument?",
  "top_k": 5
}
```

Response:

```json
{
  "document_id": "7ffdb5c4-5a42-4ee3-9aa2-47f317bdca10",
  "question": "Welche Kernaussagen stehen im Dokument?",
  "answer": "Die Kernaussagen sind ...",
  "model": "llama3",
  "sources": [
    {
      "filename": "beispiel.pdf",
      "page_number": 2,
      "chunk_id": "chunk-0004",
      "score": 0.82,
      "text_preview": "Auszug aus dem gefundenen Chunk"
    }
  ]
}
```

Fehlerfälle:

- `400`: Frage ist leer
- `400`: ungültige `document_id`
- `404`: Dokument oder Index wurde nicht gefunden
- `422`: keine relevanten Chunks gefunden
- `503`: Ollama oder lokaler Vector Store nicht erreichbar
- `500`: interner Fehler
