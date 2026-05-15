# Backend README

## Übersicht

Dieses ist das FastAPI Backend für die documind PDF AI App.

## Virtuelle Umgebung erstellen

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

## Dependencies installieren

```bash
pip install -r requirements.txt
```

## FastAPI starten

```bash
# Entwicklungsserver
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Produktivserver
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Die API ist dann verfügbar unter: http://127.0.0.1:8000

## API-Dokumentation

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## Verfügbare Endpunkte

### Healthcheck
- **GET** `/`
  - Antwortet: `{"message": "PDF AI App Backend läuft"}`

### PDF Upload
- **POST** `/api/pdf/upload`
  - Body: FormData mit `file` (PDF-Datei)
  - Antwortet mit:
    ```json
    {
      "status": "success",
      "filename": "20240115_143022_example.pdf",
      "original_filename": "example.pdf",
      "content_type": "application/pdf",
      "file_path": "/absolute/path/to/file.pdf",
      "file_size": 12345,
      "upload_timestamp": "2024-01-15T14:30:22.123456",
      "message": "PDF erfolgreich hochgeladen"
    }
    ```

## Projektstruktur

```
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── pdf_routes.py      # PDF-Endpunkte
│   ├── services/
│   │   └── pdf_service.py         # PDF-Geschäftslogik
│   ├── rag/                       # RAG (kommende Phase)
│   ├── models/                    # Pydantic Modelle
│   ├── core/
│   │   └── config.py              # Konfiguration
│   └── main.py                    # FastAPI App
├── uploads/                       # hochgeladene PDFs
└── requirements.txt               # Dependencies
```

## Nächste Schritte

1. Text-Extraktion aus PDFs (PyMuPDF)
2. Ollama Integration
3. Embeddings generieren
4. ChromaDB RAG implementieren
5. React Frontend bauen

## Tipps für Entwicklung

- `.env` Datei für sensible Daten erstellen (nicht committen!)
- Uploads im `.gitignore` ausschließen
- Bei Änderungen an dependencies: `pip freeze > requirements.txt`
