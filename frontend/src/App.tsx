import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { AlertCircle, CheckCircle2, FileText, Loader2, MessageSquare, Send, Trash2, UploadCloud } from "lucide-react";
import {
  DocumentSummary,
  RagResponse,
  UploadResponse,
  askWithRag,
  deleteDocument,
  getHealth,
  listDocuments,
  uploadPdf,
} from "./api";

type StoredUiDocument = Pick<UploadResponse, "document_id" | "filename" | "page_count"> & {
  uploadedAt: string;
};

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
  const [error, setError] = useState("");

  const selectedDocument = useMemo(
    () => documents.find((document) => document.document_id === selectedDocumentId) ?? null,
    [documents, selectedDocumentId],
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
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Upload fehlgeschlagen.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
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

    const confirmed = window.confirm(`Dokument "${documentToDelete.filename}" lokal loeschen?`);
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
      }
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Dokument konnte nicht geloescht werden.");
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
            <p>Lokal. Privat. RAG-basiert.</p>
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
          <button className="primary-button" type="button" onClick={() => fileInputRef.current?.click()}>
            {isUploading ? <Loader2 className="spin" size={18} /> : <UploadCloud size={18} />}
            PDF hochladen
          </button>
          <p>Upload indexiert automatisch mit ChromaDB und Ollama Embeddings.</p>
        </section>

        <section className="document-list" aria-label="Dokumente">
          <div className="section-title">
            <FileText size={17} />
            <span>Dokumente</span>
          </div>

          {isLoadingDocuments ? (
            <p className="empty-state">Dokumente werden geladen.</p>
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
                    }}
                  >
                    <span>{document.filename}</span>
                    <small>
                      {document.page_count} Seiten - {document.uploadedAt}
                    </small>
                  </button>
                  <button
                    aria-label={`${document.filename} loeschen`}
                    className="delete-document-button"
                    disabled={deletingDocumentId === document.document_id}
                    title="Loeschen"
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
            <h2>{selectedDocument ? selectedDocument.filename : "Dokument auswaehlen"}</h2>
          </div>
          <div className={`status-pill ${backendStatus}`}>
            {backendStatus === "checking" ? <Loader2 className="spin" size={15} /> : null}
            {backendStatus === "online" ? <CheckCircle2 size={15} /> : null}
            {backendStatus === "offline" ? <AlertCircle size={15} /> : null}
            Backend {backendStatus === "online" ? "online" : backendStatus === "offline" ? "offline" : "pruefen"}
          </div>
        </header>

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
              <p className="answer-text">{answer.answer}</p>
            </>
          ) : (
            <div className="placeholder">
              <MessageSquare size={24} />
              <p>Nach dem Upload kannst du eine Frage zum ausgewaehlten PDF stellen.</p>
            </div>
          )}
        </section>

        <form className="question-bar" onSubmit={(event) => void handleAsk(event)}>
          <input
            aria-label="Frage"
            disabled={!selectedDocument || isAsking}
            placeholder={selectedDocument ? "Frage zum Dokument stellen" : "Zuerst PDF hochladen"}
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
          />
          <label>
            Top-K
            <input
              max={10}
              min={1}
              type="number"
              value={topK}
              onChange={(event) => setTopK(Number(event.target.value))}
            />
          </label>
          <button className="icon-button" disabled={!selectedDocument || !question.trim() || isAsking} type="submit">
            {isAsking ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
            Fragen
          </button>
        </form>

        <section className="sources-panel">
          <div className="section-title">
            <FileText size={17} />
            <span>Quellen</span>
          </div>
          {answer?.sources.length ? (
            <div className="source-grid">
              {answer.sources.map((source) => (
                <article className="source-item" key={`${source.chunk_id}-${source.page_number}`}>
                  <div>
                    <strong>Seite {source.page_number}</strong>
                    <span>{source.filename}</span>
                  </div>
                  <p>{source.text_preview}</p>
                  <small>
                    {source.chunk_id}
                    {source.score === null ? "" : ` - Score ${source.score.toFixed(2)}`}
                  </small>
                </article>
              ))}
            </div>
          ) : (
            <p className="empty-state">Quellen erscheinen nach einer RAG-Antwort.</p>
          )}
        </section>
      </section>
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
