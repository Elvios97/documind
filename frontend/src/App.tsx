import { DragEvent, FormEvent, ReactNode, useEffect, useMemo, useRef, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Database,
  FileText,
  Loader2,
  LockKeyhole,
  MessageSquare,
  SearchCheck,
  Send,
  ShieldCheck,
  Sparkles,
  Trash2,
  UploadCloud,
  X,
} from "lucide-react";
import {
  DocumentSummary,
  RagResponse,
  UploadResponse,
  askWithRag,
  deleteDocument,
  getDocumentSourceUrl,
  getHealth,
  listDocuments,
  uploadPdf,
} from "./api";

type StoredUiDocument = Pick<UploadResponse, "document_id" | "filename" | "page_count"> & {
  uploadedAt: string;
};

type SourceViewer = {
  title: string;
  url: string;
};

const SUGGESTED_QUESTIONS = [
  "Fasse das Dokument in 5 Stichpunkten zusammen.",
  "Welche wichtigsten Entscheidungen oder Risiken stehen im Dokument?",
  "Welche Quellenstellen belegen die Antwort?",
];

export function App() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [documents, setDocuments] = useState<StoredUiDocument[]>([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState("");
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(5);
  const [answer, setAnswer] = useState<RagResponse | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(true);
  const [deletingDocumentId, setDeletingDocumentId] = useState("");
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const [sourceViewer, setSourceViewer] = useState<SourceViewer | null>(null);
  const [error, setError] = useState("");

  const selectedDocument = useMemo(
    () => documents.find((document) => document.document_id === selectedDocumentId) ?? null,
    [documents, selectedDocumentId],
  );
  const totalPageCount = useMemo(
    () => documents.reduce((sum, document) => sum + document.page_count, 0),
    [documents],
  );

  useEffect(() => {
    let isMounted = true;

    getHealth()
      .then(() => {
        if (isMounted) {
          setBackendStatus("online");
        }
      })
      .catch(() => {
        if (isMounted) {
          setBackendStatus("offline");
        }
      });

    listDocuments()
      .then((loadedDocuments) => {
        if (!isMounted) {
          return;
        }

        const uiDocuments = loadedDocuments.map(documentSummaryToUiDocument);
        setDocuments(uiDocuments);
        setSelectedDocumentId((currentSelectedId) => currentSelectedId || uiDocuments[0]?.document_id || "");
      })
      .catch(() => {
        if (isMounted) {
          setError("Dokumentenliste konnte nicht geladen werden.");
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoadingDocuments(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  async function handleUpload(file: File | null) {
    if (!file) {
      return;
    }

    setError("");
    setIsUploading(true);

    try {
      const result = await uploadPdf(file);
      const uploadedDocument = {
        document_id: result.document_id,
        filename: result.filename,
        page_count: result.page_count,
        uploadedAt: new Date().toLocaleTimeString("de-DE", {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };

      setDocuments((currentDocuments) => [uploadedDocument, ...currentDocuments]);
      setSelectedDocumentId(result.document_id);
      setAnswer(null);
      setSourceViewer(null);
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Upload fehlgeschlagen.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    void handleUpload(event.dataTransfer.files?.[0] ?? null);
  }

  async function handleAsk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedDocument || !question.trim()) {
      return;
    }

    setError("");
    setIsAsking(true);

    try {
      const result = await askWithRag(selectedDocument.document_id, question.trim(), topK);
      setAnswer(result);
      setSourceViewer(null);
    } catch (askError) {
      setError(askError instanceof Error ? askError.message : "Frage konnte nicht beantwortet werden.");
    } finally {
      setIsAsking(false);
    }
  }

  async function handleDelete(documentId: string) {
    const documentToDelete = documents.find((document) => document.document_id === documentId);
    if (!documentToDelete) {
      return;
    }

    const confirmed = window.confirm(`Dokument "${documentToDelete.filename}" lokal löschen?`);
    if (!confirmed) {
      return;
    }

    setError("");
    setDeletingDocumentId(documentId);

    try {
      await deleteDocument(documentId);
      const nextDocuments = documents.filter((document) => document.document_id !== documentId);
      setDocuments(nextDocuments);

      if (selectedDocumentId === documentId) {
        setSelectedDocumentId(nextDocuments[0]?.document_id ?? "");
        setAnswer(null);
        setQuestion("");
        setSourceViewer(null);
      }
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Dokument konnte nicht gelöscht werden.");
    } finally {
      setDeletingDocumentId("");
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">D</div>
          <div>
            <h1>Documind</h1>
            <p>Private PDF-Analyse mit lokaler KI.</p>
          </div>
        </div>

        <section className="upload-panel" aria-label="PDF Upload">
          <input
            ref={fileInputRef}
            className="file-input"
            type="file"
            accept="application/pdf"
            onChange={(event) => void handleUpload(event.target.files?.[0] ?? null)}
          />
          <div className="upload-dropzone" onDragOver={(event) => event.preventDefault()} onDrop={handleDrop}>
            <UploadCloud size={24} />
            <strong>PDF ablegen oder auswählen</strong>
            <span>Bis 50 MB, lokale Verarbeitung, automatische Indexierung.</span>
          </div>
          <button className="primary-button" type="button" onClick={() => fileInputRef.current?.click()}>
            {isUploading ? <Loader2 className="spin" size={18} /> : <UploadCloud size={18} />}
            PDF hochladen
          </button>
          <p>Textextraktion, Chunks, Embeddings und ChromaDB laufen lokal.</p>
        </section>

        <section className="privacy-panel" aria-label="Datenschutz">
          <div className="privacy-item">
            <LockKeyhole size={16} />
            <span>Keine Cloud, kein Login, keine Synchronisation.</span>
          </div>
          <div className="privacy-item">
            <ShieldCheck size={16} />
            <span>Ollama wird nur lokal über localhost genutzt.</span>
          </div>
        </section>

        <section className="document-list" aria-label="Dokumente">
          <div className="section-title">
            <FileText size={17} />
            <span>Dokumente</span>
            <strong>{documents.length}</strong>
          </div>

          {isLoadingDocuments ? (
            <p className="empty-state">Dokumente werden geladen...</p>
          ) : documents.length === 0 ? (
            <p className="empty-state">Noch keine lokal gespeicherten PDFs.</p>
          ) : (
            <div className="document-items">
              {documents.map((document) => (
                <article
                  className={document.document_id === selectedDocumentId ? "document-item active" : "document-item"}
                  key={document.document_id}
                >
                  <button
                    className="document-select"
                    type="button"
                    onClick={() => {
                      setSelectedDocumentId(document.document_id);
                      setAnswer(null);
                      setSourceViewer(null);
                    }}
                  >
                    <span>{document.filename}</span>
                    <small>
                      {document.page_count} Seiten · {document.uploadedAt}
                    </small>
                  </button>
                  <button
                    aria-label={`${document.filename} löschen`}
                    className="delete-document-button"
                    disabled={deletingDocumentId === document.document_id}
                    title="Löschen"
                    type="button"
                    onClick={() => void handleDelete(document.document_id)}
                  >
                    {deletingDocumentId === document.document_id ? <Loader2 className="spin" size={15} /> : <Trash2 size={15} />}
                  </button>
                  {document.document_id === selectedDocumentId ? <em>Aktiv</em> : null}
                </article>
              ))}
            </div>
          )}
        </section>
      </aside>

      <section className="workspace">
        <header className="workspace-header">
          <div>
            <p className="eyebrow">Lokales PDF-RAG</p>
            <h2>Privater PDF-Assistent</h2>
            <p className="workspace-subtitle">
              Stelle Fragen an lokale PDFs und erhalte Antworten mit nachvollziehbaren Quellen.
            </p>
          </div>
          <div className={`status-pill ${backendStatus}`}>
            {backendStatus === "checking" ? <Loader2 className="spin" size={15} /> : null}
            {backendStatus === "online" ? <CheckCircle2 size={15} /> : null}
            {backendStatus === "offline" ? <AlertCircle size={15} /> : null}
            Backend {backendStatus === "online" ? "online" : backendStatus === "offline" ? "offline" : "prüfen"}
          </div>
        </header>

        <section className="metric-grid" aria-label="Projektstatus">
          <article className="metric-card">
            <Database size={18} />
            <span>Dokumente</span>
            <strong>{documents.length}</strong>
          </article>
          <article className="metric-card">
            <FileText size={18} />
            <span>Seiten lokal</span>
            <strong>{totalPageCount}</strong>
          </article>
          <article className="metric-card">
            <SearchCheck size={18} />
            <span>Quellenlimit</span>
            <strong>{topK} Stellen</strong>
          </article>
          <article className="metric-card">
            <ShieldCheck size={18} />
            <span>Datenschutz</span>
            <strong>Lokal</strong>
          </article>
        </section>

        {error ? (
          <div className="error-banner" role="alert">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        ) : null}

        <section className="answer-panel">
          {answer ? (
            <>
              <div className="answer-heading">
                <MessageSquare size={20} />
                <div>
                  <span>Antwort</span>
                  <small>Modell: {answer.model}</small>
                </div>
              </div>
              <div className="answer-text">{renderAnswerContent(answer.answer)}</div>
            </>
          ) : (
            <div className="placeholder">
              <Sparkles size={26} />
              <strong>{selectedDocument ? selectedDocument.filename : "Bereit für dein erstes PDF"}</strong>
              <p>
                {selectedDocument
                  ? "Wähle eine Beispiel-Frage oder stelle eine eigene Frage. Die Antwort erscheint hier mit Quellen."
                  : "Lade ein PDF hoch, damit Documind Text extrahiert, Chunks erstellt und lokal indexiert."}
              </p>
            </div>
          )}
        </section>

        <section className="question-panel" aria-label="Frage stellen">
          <div className="selected-document">
            <span>Aktives Dokument</span>
            <strong>{selectedDocument ? selectedDocument.filename : "Noch kein PDF ausgewählt"}</strong>
            <small>{selectedDocument ? `${selectedDocument.page_count} Seiten · lokal gespeichert` : "Upload starten, um RAG zu nutzen"}</small>
          </div>

          <div className="suggestion-row">
            {SUGGESTED_QUESTIONS.map((suggestedQuestion) => (
              <button
                key={suggestedQuestion}
                disabled={!selectedDocument || isAsking}
                type="button"
                onClick={() => setQuestion(suggestedQuestion)}
              >
                {suggestedQuestion}
              </button>
            ))}
          </div>

          <form className="question-bar" onSubmit={(event) => void handleAsk(event)}>
            <input
              aria-label="Frage"
              disabled={!selectedDocument || isAsking}
              placeholder={selectedDocument ? "Frage zum Dokument stellen" : "Zuerst PDF hochladen"}
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
            />
            <label>
              Kontextstellen
              <input
                max={10}
                min={1}
                aria-label="Anzahl der Kontextstellen"
                title="Anzahl der relevantesten Textstellen, die Documind für die Antwort nutzt."
                type="number"
                value={topK}
                onChange={(event) => setTopK(Math.min(10, Math.max(1, Number(event.target.value) || 1)))}
              />
            </label>
            <button className="icon-button" disabled={!selectedDocument || !question.trim() || isAsking} type="submit">
              {isAsking ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
              Fragen
            </button>
          </form>
        </section>

        <section className="sources-panel">
          <div className="section-title">
            <FileText size={17} />
            <span>Quellen</span>
            <strong>{answer?.sources.length ?? 0}</strong>
          </div>
          {answer?.sources.length ? (
            <div className="source-grid">
              {answer.sources.map((source, index) => (
                <button
                  className="source-item"
                  key={`${source.chunk_id}-${source.page_number}-${index}`}
                  title={`Quelle öffnen. Interne Quelle: ${source.chunk_id}`}
                  type="button"
                  onClick={() =>
                    setSourceViewer({
                      title: `${source.filename} - Seite ${source.page_number}`,
                      url: getDocumentSourceUrl(answer.document_id, source.page_number),
                    })
                  }
                >
                  <div>
                    <strong>Quelle {index + 1} · Seite {source.page_number}</strong>
                    <span>{source.filename}</span>
                  </div>
                  <p>{source.text_preview}</p>
                  <small>Quelle und PDF-Seite öffnen</small>
                </button>
              ))}
            </div>
          ) : (
            <p className="empty-state">Quellen erscheinen nach einer RAG-Antwort mit Seitenbezug und Chunk-ID.</p>
          )}
        </section>
      </section>

      {sourceViewer ? (
        <div className="source-viewer-backdrop" role="presentation">
          <section aria-label="PDF Quelle" aria-modal="true" className="source-viewer-dialog" role="dialog">
            <header className="source-viewer-header">
              <div>
                <span>Quelle</span>
                <strong>{sourceViewer.title}</strong>
              </div>
              <button aria-label="Quellenansicht schließen" className="source-viewer-close" type="button" onClick={() => setSourceViewer(null)}>
                <X size={18} />
              </button>
            </header>
            <iframe className="source-viewer-frame" src={sourceViewer.url} title={sourceViewer.title} />
          </section>
        </div>
      ) : null}
    </main>
  );
}

function documentSummaryToUiDocument(document: DocumentSummary): StoredUiDocument {
  return {
    document_id: document.document_id,
    filename: document.filename,
    page_count: document.page_count,
    uploadedAt: formatDocumentTime(document.created_at),
  };
}

function formatDocumentTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "lokal";
  }

  return date.toLocaleDateString("de-DE", {
    day: "2-digit",
    month: "2-digit",
  });
}

function renderAnswerContent(text: string): ReactNode[] {
  const elements: ReactNode[] = [];
  const listItems: ReactNode[] = [];
  let activeListType: "ordered" | "unordered" | null = null;
  let listKey = 0;

  function flushList() {
    if (!activeListType || listItems.length === 0) {
      return;
    }

    const ListTag = activeListType === "ordered" ? "ol" : "ul";
    elements.push(
      <ListTag className="answer-list" key={`list-${listKey}`}>
        {listItems.splice(0)}
      </ListTag>,
    );
    activeListType = null;
    listKey += 1;
  }

  text.split(/\r?\n/).forEach((line, index) => {
    const numberedMatch = line.match(/^\s*\d+\.\s+(.*)$/);
    const bulletMatch = line.match(/^\s*[-*]\s+(.*)$/);

    if (!line.trim()) {
      flushList();
      return;
    }

    if (numberedMatch) {
      if (activeListType !== "ordered") {
        flushList();
        activeListType = "ordered";
      }
      listItems.push(<li key={`item-${index}`}>{renderInlineMarkdown(numberedMatch[1])}</li>);
      return;
    }

    if (bulletMatch) {
      if (activeListType !== "unordered") {
        flushList();
        activeListType = "unordered";
      }
      listItems.push(<li key={`item-${index}`}>{renderInlineMarkdown(bulletMatch[1])}</li>);
      return;
    }

    flushList();
    elements.push(<p key={`paragraph-${index}`}>{renderInlineMarkdown(line.trim())}</p>);
  });

  flushList();
  return elements;
}

function renderInlineMarkdown(text: string): ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }

    return part;
  });
}
