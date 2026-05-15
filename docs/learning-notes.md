# documind - Lernnotizen

## FastAPI

### Was ist FastAPI?
- Modernes Python Web Framework für APIs
- Schnell, einfach, starke Typisierung
- Built-in automatische Dokumentation (Swagger/ReDoc)
- Basiert auf Starlette & Pydantic

### Key Concepts
- **Router**: Gruppieren zusammenhängender Endpunkte
- **Middleware**: Verarbeitet jeden Request/Response
- **Dependency Injection**: Automatische Bereitstellung von Abhängigkeiten
- **Pydantic Models**: Validierung & Serialisierung

### Tipps
- `--reload` Flag aktiviert Auto-Reload bei Dateiänderungen
- Automatische OpenAPI Dokumentation unter `/docs`
- Async/Await für I/O-Operationen nutzen

---

## PDF-Verarbeitung

### PyMuPDF (fitz)
```python
import fitz  # PyMuPDF

# PDF öffnen
pdf = fitz.open("document.pdf")

# Seite extrahieren
page = pdf[0]

# Text extrahieren
text = page.get_text()

# Bilder extrahieren
images = page.get_images()
```

### Häufige Herausforderungen
- Gescannte PDFs (benötigen OCR)
- Verschiedene Encodings
- Große Dateien (memory-effizient verarbeiten)
- DRM-geschützte Dokumente

---

## Ollama (Lokale KI)

### Was ist Ollama?
- Tool zum lokalen Ausführen von LLMs
- Keine Internetverbindung nötig
- Privacy-fokussiert
- Unterstützt verschiedene Modelle (Llama2, Mistral, etc.)

### Installation
```bash
# Windows: Download von ollama.ai
# macOS: brew install ollama
# Linux: curl https://ollama.ai/install.sh | sh
```

### Modelle laden
```bash
ollama pull llama2
ollama pull mistral
ollama pull nomic-embed-text
```

### API Nutzung
```python
import requests

response = requests.post('http://localhost:11434/api/generate',
    json={
        "model": "llama2",
        "prompt": "Why is the sky blue?",
        "stream": False
    }
)
```

---

## Embeddings

### Was sind Embeddings?
- Vektorielle Darstellung von Text
- Semantisch ähnliche Texte → ähnliche Vektoren
- Ermöglichen Ähnlichkeitssuche

### Embedding Modelle
- `nomic-embed-text`: Klein, schnell, lokal
- `all-MiniLM-L6-v2`: ONNX Format
- OpenAI's Modelle: Cloud, teuer

### Verwendung
```python
from ollama import Ollama

client = Ollama(model="nomic-embed-text")
embedding = client.embed("Hello world")
```

---

## ChromaDB

### Was ist ChromaDB?
- Lokale Vector Database
- Speichert & sucht Embeddings
- Einfache REST API
- Ideal für RAG Systeme

### Installation
```bash
pip install chromadb
```

### Grundlagen
```python
import chromadb

# Client erstellen
client = chromadb.Client()

# Collection erstellen
collection = client.create_collection("my_docs")

# Dokumente hinzufügen
collection.add(
    documents=["This is document 1"],
    embeddings=[[1.1, 2.3]],  # Embeddings
    ids=["id1"]
)

# Suche
results = collection.query(
    query_embeddings=[[1.1, 2.3]],
    n_results=3
)
```

---

## RAG (Retrieval Augmented Generation)

### Konzept
1. **Retrieval**: Relevante Dokumente finden (Vector Similarity Search)
2. **Augmentation**: Kontext zu LLM hinzufügen
3. **Generation**: LLM generiert Antwort basierend auf Kontext

### Workflow
```
Benutzer Frage
    ↓
Embedding generieren
    ↓
In ChromaDB suchen
    ↓
Top K Chunks abrufen
    ↓
Prompt + Kontext zusammenstellen
    ↓
Zu Ollama senden
    ↓
Antwort erhalten & zurückgeben
```

### Vorteile
- Bessere Antworten (Domain-spezifisch)
- Halluzinationen reduzieren
- Referenzen auf Quelle möglich

---

## React

### Was ist React?
- JavaScript UI Library
- Komponentenbasiert
- Virtual DOM für Performance
- Große Ökosystem

### Basics
- **JSX**: HTML-ähnliche Syntax in JavaScript
- **Components**: Wiederverwendbare UI-Einheiten
- **State**: Komponenten-Daten
- **Props**: Daten zwischen Komponenten

### TypeScript mit React
```typescript
interface Props {
  title: string;
  count?: number;
}

const MyComponent: React.FC<Props> = ({ title, count = 0 }) => {
  return <h1>{title} - {count}</h1>;
};
```

---

## Tauri

### Was ist Tauri?
- Desktop App Framework (Alternative zu Electron)
- Kleiner, schneller, sicherer
- Kombiniert Rust Backend + Web Frontend
- Native Systemzugriff

### Vorteile
- ~50 MB vs. ~150 MB (vs Electron)
- Bessere Performance
- Rust Security Modell

### Grundstruktur
```
- src-tauri/: Rust Backend
- src/: React Frontend
- tauri.conf.json: Config
```

---

## Best Practices für dieses Projekt

1. **Modularität**: Kleine, fokussierte Module
2. **Fehlerbehandlung**: Explizite Error Messages
3. **Testing**: Unit Tests für kritische Logik
4. **Dokumentation**: Code Comments & READMEs
5. **Performance**: Async für I/O, Caching wo sinnvoll
6. **Security**: Input Validation, Safe File Handling
7. **Versionierung**: Aussagekräftige Git Commits
