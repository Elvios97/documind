# RAG-Planung

## Was ist RAG?

RAG steht für Retrieval Augmented Generation. Das System sucht zuerst relevante Textstellen und gibt diese als Kontext an ein Sprachmodell. Das Modell beantwortet die Frage dann anhand dieses Kontextes.

Kurz gesagt:

```text
Frage -> relevante Textstellen suchen -> Prompt bauen -> lokale Antwort erzeugen
```

## Warum RAG für Documind?

Phase 2 sendet noch einen begrenzten Ausschnitt des gesamten PDF-Texts an Ollama. Das ist einfach, aber für längere PDFs nicht gut genug.

RAG verbessert Documind, weil:

- längere PDFs besser verarbeitet werden können
- nur relevante Textstellen an Ollama gehen
- Antworten nachvollziehbare Quellen bekommen
- Halluzinationen reduziert werden
- lokale Daten weiterhin lokal bleiben

## Chunking

Beim Chunking wird der PDF-Text in kleinere Abschnitte zerlegt.

Geplante Eigenschaften:

- konfigurierbare Chunk-Größe
- konfigurierbarer Overlap
- Seitenzahl bleibt erhalten
- Dokument-ID bleibt erhalten
- Chunk-ID wird erzeugt
- leerer oder zu kurzer Text wird sauber behandelt

Beispiel für Chunk-Metadaten:

```json
{
  "document_id": "doc-123",
  "chunk_id": "chunk-0001",
  "page_number": 1,
  "text": "Textauszug aus Seite 1"
}
```

## Embeddings

Embeddings wandeln Text in Zahlenvektoren um. Ähnliche Texte erhalten ähnliche Vektoren. Dadurch kann Documind relevante Textstellen semantisch suchen.

Wichtig:

- Embeddings werden lokal erzeugt.
- Es werden keine externen Embedding-APIs genutzt.
- Das lokale Standardmodell ist `nomic-embed-text` über Ollama.
- Der Embedding Service nutzt Ollamas lokalen Endpoint `POST /api/embed`.
- Das Modell kann über `DOCUMIND_EMBEDDING_MODEL` geändert werden.

## ChromaDB

ChromaDB speichert die Embeddings lokal.

Geplanter Speicherort:

```text
local_data/chroma/
```

ChromaDB soll speichern:

- Chunk-Text
- Embedding
- Dokument-ID
- Dateiname
- Seitenzahl
- Chunk-ID

Der Vector Store Service nutzt eine lokale ChromaDB Collection namens `documind_chunks`. Der Speicherort kann über `DOCUMIND_CHROMA_DIR` geändert werden.

Der Indexing Service verbindet die bisherigen Bausteine:

```text
StoredDocument -> Chunking -> Embeddings -> Vector Store
```

Nach erfolgreichem PDF-Upload wird das gespeicherte Dokument automatisch indexiert. Wenn die Indexierung fehlschlägt, gilt der Upload nicht als erfolgreich und lokale Zwischenstände werden aufgeräumt.

Der RAG Service verbindet danach die Abfrage:

```text
Frage -> Query-Embedding -> Top-K Retrieval -> RAG Prompt -> Ollama -> Antwort mit Quellen
```

Der Endpoint `POST /rag/ask` gibt Antwort, Modellname und Quellen zurück.

## Retrieval

Beim Retrieval wird aus der Nutzerfrage ein Query-Embedding erzeugt. Danach sucht ChromaDB die ähnlichsten Chunks.

Geplante Einstellungen:

- `top_k` bestimmt die Anzahl der Treffer
- Standardwert zunächst klein halten, zum Beispiel 5
- Treffer enthalten Score und Metadaten
- wenn keine Treffer gefunden werden, gibt die API eine verständliche Fehlermeldung zurück

## Prompting

Der RAG Prompt soll klar begrenzen, was Ollama tun darf:

- nur gefundene Chunks verwenden
- keine Informationen erfinden
- Unsicherheit klar benennen
- Antwort kurz und verständlich formulieren
- Quellen berücksichtigen

## Quellenangaben

Antworten sollen Quellen enthalten:

- Dateiname
- Seite
- Chunk-ID
- kurzer Textauszug
- optional Score

Beispiel:

```json
{
  "filename": "vertrag.pdf",
  "page_number": 3,
  "chunk_id": "chunk-0012",
  "text_preview": "Die Kündigungsfrist beträgt ..."
}
```

## Grenzen des Systems

- Gescannte PDFs benötigen später OCR.
- Schlechte PDF-Textstruktur kann zu schwachen Chunks führen.
- Lokale Modelle können langsamer sein als Cloud-Modelle.
- RAG reduziert Halluzinationen, verhindert sie aber nicht vollständig.
- Quellen zeigen den verwendeten Kontext, nicht automatisch die absolute Wahrheit.

## Tests für RAG

Geplante Tests:

- Chunking erzeugt stabile Chunk-IDs
- Chunking behält Seitenzahlen
- Overlap funktioniert korrekt
- leere Texte werden sauber behandelt
- Embedding Service kann gemockt werden
- Vector Store speichert Chunks mit Embeddings
- Vector Store findet Chunks per Query-Embedding
- Indexing Service verbindet Chunking, Embeddings und Vector Store
- RAG Service baut korrekten Kontext
- `POST /rag/ask` gibt Antwort und Quellen zurück
- Fehlerfälle für fehlenden Index und fehlendes Dokument
