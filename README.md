# 📄 documind - Lokale PDF AI App

## 🎯 Projektidee

**documind** ist eine lokale Desktop-Anwendung, mit der du:
- 📤 PDFs hochladen kannst
- 📝 Text aus PDFs extrahieren kannst
- 💬 Mit deinen PDFs über eine lokale KI chatten kannst
- 🔒 Alles lokal auf deinem PC ausführst (keine Cloud)

## 🚀 Ziel

Ein vollständig funktionierendes, benutzerfreundliches System zur intelligenten PDF-Analyse mit **lokalen**, open-source Modellen bauen - ideal für das Portfolio.

## 🛠️ Geplanter Tech Stack

| Layer | Technologie | Grund |
|-------|-------------|-------|
| **Frontend** | React 18 + TypeScript | Modern, responsive UI |
| **Desktop** | Tauri | Leicht, schnell, native Performance |
| **Backend** | Python FastAPI | Schnell, typ-sicher, Data-Science-friendly |
| **PDF-Verarbeitung** | PyMuPDF | Zuverlässig, schnell |
| **Lokale KI** | Ollama | Einfach zu bedienen, viele Modelle |
| **Embeddings** | Lokale Modelle | Datenschutz, keine API Kosten |
| **Vector DB** | ChromaDB | Leicht, RAG-optimiert |
| **Versionierung** | Git + GitHub | Standard |

## 📊 Aktueller Stand

### ✅ Phase 1 - ABGESCHLOSSEN
- Projektstruktur
- FastAPI Backend
- PDF Upload Endpunkt
- Dokumentation & Roadmap

### 🔄 Phase 2-8 - GEPLANT
Siehe [docs/roadmap.md](docs/roadmap.md)

## 📁 Projektstruktur

```
documind/
├── backend/                    # FastAPI Python Backend
│   ├── app/
│   │   ├── api/routes/        # API Endpunkte
│   │   ├── services/          # Business Logic
│   │   ├── core/              # Konfiguration
│   │   ├── models/            # Pydantic Modelle
│   │   ├── rag/               # RAG Pipeline (später)
│   │   └── main.py            # FastAPI App
│   ├── uploads/               # hochgeladene PDFs
│   └── requirements.txt
│
├── frontend/                  # React + Vite Frontend
│   └── (wird in Phase 6 gestartet)
│
├── docs/                      # Dokumentation
│   ├── architecture.md        # Systemarchitektur
│   ├── roadmap.md             # Projekt Roadmap
│   └── learning-notes.md      # Lernnotizen
│
├── .gitignore
├── README.md                  # diese Datei
└── LICENSE
```

## ⚡ Quick Start

### Backend starten

```bash
# 1. In backend Ordner gehen
cd backend

# 2. Virtuelle Umgebung erstellen (erste Mal)
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # macOS/Linux

# 3. Dependencies installieren
pip install -r requirements.txt

# 4. Server starten
uvicorn app.main:app --reload
```

Server läuft dann unter: **http://127.0.0.1:8000**

### API testen

```bash
# Healthcheck
curl http://127.0.0.1:8000/

# Swagger Dokumentation
# Öffne im Browser: http://127.0.0.1:8000/docs

# PDF Upload (mit curl)
curl -X POST "http://127.0.0.1:8000/api/pdf/upload" \
  -F "file=@deine_datei.pdf"
```

## 📚 API Endpunkte

### GET `/`
Healthcheck - prüft ob Backend läuft
```json
{
  "message": "PDF AI App Backend läuft"
}
```

### POST `/api/pdf/upload`
Lädt eine PDF-Datei hoch
```bash
curl -X POST "http://127.0.0.1:8000/api/pdf/upload" \
  -F "file=@example.pdf"
```

Response:
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

## 📖 Dokumentation

- **[Architektur](docs/architecture.md)**: Systemdesign & Datenfluss
- **[Roadmap](docs/roadmap.md)**: Detaillierte Phasen & Timeline
- **[Lernnotizen](docs/learning-notes.md)**: Tutorials & Konzepte
- **[Backend README](backend/README.md)**: Backend Setup & Entwicklung

## 🎓 Was ich mit diesem Projekt lerne

- ✅ FastAPI für moderne Python APIs
- ✅ PDF-Verarbeitung mit PyMuPDF
- ✅ Lokale KI Integration (Ollama)
- ✅ Vector Embeddings & RAG
- ✅ React + TypeScript UI
- ✅ Tauri für Desktop Apps
- ✅ Full-Stack Python/JavaScript Architektur

## 🔄 Nächste Schritte

1. **Phase 2**: PDF Text Extraktion implementieren
2. **Phase 3**: Ollama Integration
3. **Phase 4**: Embeddings & Chunking
4. **Phase 5**: ChromaDB RAG
5. **Phase 6**: React UI
6. **Phase 7**: Tauri Desktop App
7. **Phase 8**: Finalisierung & Demo

## 🤝 Beitragen

Dieses Projekt ist aktuell in Entwicklung. Der Code ist strukturiert für einfache Erweiterungen in den kommenden Phasen.

## 📄 Lizenz

[Lizenz hinzufügen]

---

**Letzte Aktualisierung**: Januar 2024
**Status**: Phase 1 ✅ - Projektstruktur & Backend Setup abgeschlossen
