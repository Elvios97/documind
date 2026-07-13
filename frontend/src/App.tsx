import { DragEvent, FormEvent, ReactNode, useEffect, useMemo, useRef, useState } from "react";
import {
  AlertCircle,
  CheckCircle2,
  Database,
  FileText,
  Loader2,
  LockKeyhole,
  MessageSquare,
  RotateCcw,
  Search,
  SearchCheck,
  Send,
  ShieldCheck,
  Sparkles,
  Square,
  Trash2,
  UploadCloud,
  X,
} from "lucide-react";
import {
  AnalysisMode,
  DocumentSummary,
  RagResponse,
  UploadResponse,
  askWithRag,
  cancelDocumentIndexing,
  deleteDocument,
  getDocumentSourceUrl,
  getHealth,
  listDocuments,
  retryDocumentIndexing,
  uploadPdf,
} from "./api";

type StoredUiDocument = Pick<UploadResponse, "document_id" | "filename" | "page_count"> & {
  createdAt: string;
  uploadedAt: string;
  indexingStatus: UploadResponse["indexing_status"];
  indexingError: string | null;
  indexingCompletedChunks: number;
  indexingTotalChunks: number;
  indexingQueuePosition: number | null;
  indexingActive: boolean;
};

type SourceViewer = {
  title: string;
  url: string;
};

type ErrorContext = "documents" | "ask" | "upload" | "index" | "general";

const SUGGESTED_QUESTIONS: Record<AnalysisMode, string[]> = {
  ask: [
    "Fasse die wichtigsten Aussagen in 5 Stichpunkten zusammen.",
    "Welche wichtigsten Entscheidungen oder Risiken stehen in den Dokumenten?",
    "Welche Quellenstellen belegen die Antwort?",
  ],
  compare: [
    "Welche Gemeinsamkeiten und Unterschiede gibt es?",
    "Wo widersprechen sich die ausgewählten Dokumente?",
    "Welche Entwicklung ist zwischen den Dokumenten erkennbar?",
  ],
  summarize: [
    "Fasse jedes Dokument kurz zusammen und ziehe ein Gesamtfazit.",
    "Welche fünf Kernaussagen ergeben sich insgesamt?",
    "Welche Themen kommen in mehreren Dokumenten vor?",
  ],
};
const MAX_SELECTED_DOCUMENTS = 5;
const SELECTION_STORAGE_KEY = "documind:selected-documents:v1";
const PREFERENCES_STORAGE_KEY = "documind:analysis-preferences:v1";

export function App() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [documents, setDocuments] = useState<StoredUiDocument[]>([]);
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>(readPersistedDocumentIds);
  const [preferences, setPreferences] = useState(readPersistedPreferences);
  const { mode, topK } = preferences;
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<RagResponse | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const [isAsking, setIsAsking] = useState(false);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(true);
  const [deletingDocumentId, setDeletingDocumentId] = useState("");
  const [indexActionDocumentId, setIndexActionDocumentId] = useState("");
  const [documentQuery, setDocumentQuery] = useState("");
  const [documentSort, setDocumentSort] = useState<"newest" | "name" | "pages">("newest");
  const [documentStatusFilter, setDocumentStatusFilter] = useState<"all" | "ready" | "indexing" | "attention">("all");
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const [sourceViewer, setSourceViewer] = useState<SourceViewer | null>(null);
  const [error, setError] = useState("");
  const [errorContext, setErrorContext] = useState<ErrorContext>("general");

  const selectedDocumentIdSet = useMemo(() => new Set(selectedDocumentIds), [selectedDocumentIds]);
  const selectedDocuments = useMemo(
    () => documents.filter((document) => selectedDocumentIdSet.has(document.document_id)),
    [documents, selectedDocumentIdSet],
  );
  const selectedDocumentsReady =
    selectedDocuments.length > 0 && selectedDocuments.every((document) => document.indexingStatus === "ready");
  const selectedPageCount = selectedDocuments.reduce((sum, document) => sum + document.page_count, 0);
  const totalPageCount = useMemo(
    () => documents.reduce((sum, document) => sum + document.page_count, 0),
    [documents],
  );
  const sourceGroups = useMemo(() => {
    const groups = new Map<string, NonNullable<RagResponse["sources"]>>();
    for (const source of answer?.sources ?? []) {
      const sources = groups.get(source.document_id) ?? [];
      sources.push(source);
      groups.set(source.document_id, sources);
    }
    return [...groups.entries()].map(([documentId, sources]) => ({
      documentId,
      filename: sources[0].filename,
      sources,
    }));
  }, [answer]);
  const visibleDocuments = useMemo(() => {
    const normalizedQuery = documentQuery.trim().toLocaleLowerCase("de-DE");
    const filteredDocuments = documents.filter((document) => {
      const matchesQuery = !normalizedQuery || document.filename.toLocaleLowerCase("de-DE").includes(normalizedQuery);
      const matchesStatus = documentStatusFilter === "all"
        || document.indexingStatus === documentStatusFilter
        || (documentStatusFilter === "attention" && ["failed", "cancelled"].includes(document.indexingStatus));
      return matchesQuery && matchesStatus;
    });
    return [...filteredDocuments].sort((first, second) => {
      if (documentSort === "name") {
        return first.filename.localeCompare(second.filename, "de");
      }
      if (documentSort === "pages") {
        return second.page_count - first.page_count;
      }
      return second.createdAt.localeCompare(first.createdAt);
    });
  }, [documentQuery, documentSort, documentStatusFilter, documents]);

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
        setSelectedDocumentIds((currentIds) => {
          const availableIds = new Set(uiDocuments.map((document) => document.document_id));
          const restoredIds = currentIds.filter((documentId) => availableIds.has(documentId)).slice(0, MAX_SELECTED_DOCUMENTS);
          return restoredIds.length > 0 ? restoredIds : uiDocuments[0] ? [uiDocuments[0].document_id] : [];
        });
      })
      .catch(() => {
        if (isMounted) {
          setError("Dokumentenliste konnte nicht geladen werden.");
          setErrorContext("documents");
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

  useEffect(() => {
    persistDocumentIds(selectedDocumentIds);
  }, [selectedDocumentIds]);

  useEffect(() => {
    persistPreferences(preferences);
  }, [preferences]);

  useEffect(() => {
    if (!documents.some((document) => document.indexingStatus === "indexing")) {
      return;
    }

    let isMounted = true;
    const intervalId = window.setInterval(() => {
      listDocuments()
        .then((loadedDocuments) => {
          if (!isMounted) {
            return;
          }
          const updatedDocuments = loadedDocuments.map(documentSummaryToUiDocument);
          const completedDocument = updatedDocuments.find(
            (document) =>
              document.indexingStatus === "ready" &&
              documents.some(
                (currentDocument) =>
                  currentDocument.document_id === document.document_id &&
                  currentDocument.indexingStatus === "indexing",
              ),
          );
          const failedDocument = updatedDocuments.find(
            (document) =>
              document.indexingStatus === "failed" &&
              documents.some(
                (currentDocument) =>
                  currentDocument.document_id === document.document_id &&
                  currentDocument.indexingStatus === "indexing",
              ),
          );

          if (completedDocument) {
            setUploadStatus(`${completedDocument.filename} ist jetzt bereit.`);
          }
          if (failedDocument) {
            setUploadStatus("");
            setError(failedDocument.indexingError ?? "Die Indexierung ist fehlgeschlagen.");
            setErrorContext("index");
          }
          setDocuments(updatedDocuments);
        })
        .catch(() => {
          // Der globale Offline-Status bleibt die zentrale Fehlerrückmeldung.
        });
    }, 2000);

    return () => {
      isMounted = false;
      window.clearInterval(intervalId);
    };
  }, [documents]);

  async function handleUpload(file: File | null) {
    if (!file) {
      return;
    }

    setError("");
    setIsUploading(true);
    setUploadStatus("PDF wird lokal verarbeitet und indexiert...");

    try {
      const result = await uploadPdf(file);
      const uploadedDocument = {
        document_id: result.document_id,
        filename: result.filename,
        page_count: result.page_count,
        createdAt: new Date().toISOString(),
        uploadedAt: new Date().toLocaleTimeString("de-DE", {
          hour: "2-digit",
          minute: "2-digit",
        }),
        indexingStatus: result.indexing_status,
        indexingError: null,
        indexingCompletedChunks: result.indexing_completed_chunks,
        indexingTotalChunks: result.indexing_total_chunks,
        indexingQueuePosition: null,
        indexingActive: false,
      };

      setDocuments((currentDocuments) => [uploadedDocument, ...currentDocuments]);
      setSelectedDocumentIds((currentIds) =>
        currentIds.includes(result.document_id) || currentIds.length >= MAX_SELECTED_DOCUMENTS
          ? currentIds
          : [...currentIds, result.document_id],
      );
      setAnswer(null);
      setSourceViewer(null);
      setUploadStatus(`${result.filename} wurde gespeichert. Die Indexierung läuft im Hintergrund.`);
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Upload fehlgeschlagen.");
      setErrorContext("upload");
      setUploadStatus("");
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
    await submitQuestion();
  }

  async function submitQuestion() {
    if (!selectedDocumentsReady || !question.trim()) {
      return;
    }

    setError("");
    setIsAsking(true);

    try {
      const result = await askWithRag(selectedDocumentIds, question.trim(), topK, mode);
      setAnswer(result);
      setSourceViewer(null);
    } catch (askError) {
      setError(askError instanceof Error ? askError.message : "Frage konnte nicht beantwortet werden.");
      setErrorContext("ask");
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

      if (selectedDocumentIdSet.has(documentId)) {
        setSelectedDocumentIds((currentIds) => currentIds.filter((id) => id !== documentId));
        setAnswer(null);
        setQuestion("");
        setSourceViewer(null);
      }
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Dokument konnte nicht gelöscht werden.");
      setErrorContext("index");
    } finally {
      setDeletingDocumentId("");
    }
  }

  async function handleRetryIndexing(documentId: string) {
    setError("");
    setIndexActionDocumentId(documentId);
    try {
      const updatedDocument = await retryDocumentIndexing(documentId);
      replaceDocument(updatedDocument);
      setUploadStatus(`${updatedDocument.filename} wurde erneut zur Indexierung eingereiht.`);
    } catch (actionError) {
      setError(actionError instanceof Error ? actionError.message : "Indexierung konnte nicht gestartet werden.");
      setErrorContext("index");
    } finally {
      setIndexActionDocumentId("");
    }
  }

  async function handleCancelIndexing(documentId: string) {
    setError("");
    setIndexActionDocumentId(documentId);
    try {
      const updatedDocument = await cancelDocumentIndexing(documentId);
      replaceDocument(updatedDocument);
      setUploadStatus(`${updatedDocument.filename}: Indexierung abgebrochen.`);
      setAnswer(null);
      setSourceViewer(null);
    } catch (actionError) {
      setError(actionError instanceof Error ? actionError.message : "Indexierung konnte nicht abgebrochen werden.");
      setErrorContext("index");
    } finally {
      setIndexActionDocumentId("");
    }
  }

  function replaceDocument(updatedDocument: DocumentSummary) {
    setDocuments((currentDocuments) =>
      currentDocuments.map((document) =>
        document.document_id === updatedDocument.document_id
          ? documentSummaryToUiDocument(updatedDocument)
          : document,
      ),
    );
  }

  async function refreshWorkspaceStatus() {
    setBackendStatus("checking");
    try {
      const [, loadedDocuments] = await Promise.all([getHealth(), listDocuments()]);
      const uiDocuments = loadedDocuments.map(documentSummaryToUiDocument);
      const availableIds = new Set(uiDocuments.map((document) => document.document_id));
      setDocuments(uiDocuments);
      setSelectedDocumentIds((currentIds) => currentIds.filter((documentId) => availableIds.has(documentId)));
      setBackendStatus("online");
      setError("");
    } catch {
      setBackendStatus("offline");
      setError("Das lokale Backend ist nicht erreichbar.");
      setErrorContext("documents");
    }
  }

  function handleErrorAction() {
    if (errorContext === "ask") {
      void submitQuestion();
      return;
    }
    if (errorContext === "upload") {
      fileInputRef.current?.click();
      return;
    }
    void refreshWorkspaceStatus();
  }

  function toggleDocumentSelection(documentId: string) {
    setError("");
    setSelectedDocumentIds((currentIds) => {
      if (currentIds.includes(documentId)) {
        return currentIds.filter((id) => id !== documentId);
      }
      if (currentIds.length >= MAX_SELECTED_DOCUMENTS) {
        setError(`Du kannst hoechstens ${MAX_SELECTED_DOCUMENTS} Dokumente gleichzeitig auswaehlen.`);
        setErrorContext("general");
        return currentIds;
      }
      return [...currentIds, documentId];
    });
    setAnswer(null);
    setSourceViewer(null);
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

        <section className={documents.length > 0 ? "upload-panel compact" : "upload-panel"} aria-label="PDF Upload">
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
          {uploadStatus ? <p className="upload-status" role="status">{uploadStatus}</p> : null}
          <p>Textextraktion, Chunks, Embeddings und ChromaDB laufen lokal.</p>
        </section>

        <details className="privacy-panel">
          <summary>
            <LockKeyhole size={16} />
            Datenschutz & lokale Verarbeitung
          </summary>
          <div className="privacy-content">
            <div className="privacy-item">
              <LockKeyhole size={16} />
              <span>Keine Cloud, kein Login, keine Synchronisation.</span>
            </div>
            <div className="privacy-item">
              <ShieldCheck size={16} />
              <span>Ollama wird nur lokal über localhost genutzt.</span>
            </div>
          </div>
        </details>

        <section className="document-list" aria-label="Dokumente">
          <div className="section-title">
            <FileText size={17} />
            <span>Dokumente</span>
            <strong title={`${selectedDocuments.length} von ${MAX_SELECTED_DOCUMENTS} ausgewaehlt`}>
              {selectedDocuments.length}/{MAX_SELECTED_DOCUMENTS}
            </strong>
          </div>

          {documents.length > 0 ? (
            <div className="document-toolbar">
              <label className="document-search">
                <Search size={15} />
                <input
                  aria-label="Dokumente durchsuchen"
                  placeholder="PDF suchen"
                  type="search"
                  value={documentQuery}
                  onChange={(event) => setDocumentQuery(event.target.value)}
                />
              </label>
              <div className="document-filter-row">
                <select
                  aria-label="Dokumente sortieren"
                  value={documentSort}
                  onChange={(event) => setDocumentSort(event.target.value as typeof documentSort)}
                >
                  <option value="newest">Neueste</option>
                  <option value="name">Name</option>
                  <option value="pages">Seitenzahl</option>
                </select>
                <select
                  aria-label="Dokumentstatus filtern"
                  value={documentStatusFilter}
                  onChange={(event) => setDocumentStatusFilter(event.target.value as typeof documentStatusFilter)}
                >
                  <option value="all">Alle Status</option>
                  <option value="ready">Bereit</option>
                  <option value="indexing">Indexierung</option>
                  <option value="attention">Fehler/Abbruch</option>
                </select>
              </div>
            </div>
          ) : null}

          {isLoadingDocuments ? (
            <p className="empty-state">Dokumente werden geladen...</p>
          ) : documents.length === 0 ? (
            <p className="empty-state">Noch keine lokal gespeicherten PDFs.</p>
          ) : visibleDocuments.length === 0 ? (
            <p className="empty-state">Keine Dokumente für diesen Filter gefunden.</p>
          ) : (
            <div className="document-items">
              {visibleDocuments.map((document) => (
                <article
                  className={selectedDocumentIdSet.has(document.document_id) ? "document-item active" : "document-item"}
                  key={document.document_id}
                >
                  <button
                    aria-pressed={selectedDocumentIdSet.has(document.document_id)}
                    className="document-select"
                    type="button"
                    onClick={() => toggleDocumentSelection(document.document_id)}
                  >
                    <span>{document.filename}</span>
                    <small>
                      {document.page_count} Seiten · {document.uploadedAt}
                    </small>
                    <small className={`document-status ${document.indexingStatus}`}>
                      {getIndexingStatusText(document)}
                    </small>
                  </button>
                  <div className="document-actions">
                    {document.indexingStatus === "indexing" ? (
                      <button
                        aria-label={`${document.filename} Indexierung abbrechen`}
                        className="document-action-button"
                        disabled={indexActionDocumentId === document.document_id}
                        title="Indexierung abbrechen"
                        type="button"
                        onClick={() => void handleCancelIndexing(document.document_id)}
                      >
                        {indexActionDocumentId === document.document_id ? <Loader2 className="spin" size={15} /> : <Square size={14} />}
                      </button>
                    ) : null}
                    {document.indexingStatus === "failed" || document.indexingStatus === "cancelled" ? (
                      <button
                        aria-label={`${document.filename} erneut indexieren`}
                        className="document-action-button"
                        disabled={indexActionDocumentId === document.document_id}
                        title="Erneut indexieren"
                        type="button"
                        onClick={() => void handleRetryIndexing(document.document_id)}
                      >
                        {indexActionDocumentId === document.document_id ? <Loader2 className="spin" size={15} /> : <RotateCcw size={15} />}
                      </button>
                    ) : null}
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
                  </div>
                  {selectedDocumentIdSet.has(document.document_id) ? <em>Ausgewählt</em> : null}
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
            <div className="error-copy">
              <strong>{error}</strong>
              <small>{getErrorGuidance(error, errorContext)}</small>
            </div>
            <div className="error-actions">
              {errorContext !== "general" ? (
                <button type="button" onClick={handleErrorAction}>
                  {getErrorActionLabel(errorContext)}
                </button>
              ) : null}
              <button aria-label="Fehlermeldung schließen" type="button" onClick={() => setError("")}>
                <X size={15} />
              </button>
            </div>
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
              <strong>
                {selectedDocuments.length === 0
                  ? "Bereit für deine PDFs"
                  : selectedDocuments.length === 1
                    ? selectedDocuments[0].filename
                    : `${selectedDocuments.length} Dokumente ausgewählt`}
              </strong>
              <p>
                {selectedDocuments.length === 0
                  ? "Wähle bis zu fünf PDFs aus, um sie gemeinsam zu analysieren."
                  : selectedDocumentsReady
                    ? "Stelle eine Frage über alle ausgewählten Dokumente. Die relevantesten Quellen werden gemeinsam ermittelt."
                    : "Mindestens eines der ausgewählten Dokumente ist noch nicht bereit."}
              </p>
            </div>
          )}
        </section>

        <section className="question-panel" aria-label="Frage stellen">
          <div className="analysis-mode-switch" aria-label="Analysemodus">
            {([
              ["ask", "Fragen"],
              ["compare", "Vergleichen"],
              ["summarize", "Zusammenfassen"],
            ] as const).map(([value, label]) => (
              <button
                aria-pressed={mode === value}
                className={mode === value ? "active" : ""}
                key={value}
                type="button"
                onClick={() => {
                  setPreferences((current) => ({ ...current, mode: value }));
                  setQuestion("");
                  setAnswer(null);
                }}
              >
                {label}
              </button>
            ))}
          </div>
          <div className="selected-document">
            <div className="selected-document-heading">
              <div>
                <span>Ausgewählte Dokumente</span>
                <strong>
                  {selectedDocuments.length > 0
                    ? `${selectedDocuments.length} von ${MAX_SELECTED_DOCUMENTS}`
                    : "Noch kein PDF ausgewählt"}
                </strong>
              </div>
              {selectedDocuments.length > 0 ? (
                <button className="clear-selection-button" type="button" onClick={() => setSelectedDocumentIds([])}>
                  Auswahl aufheben
                </button>
              ) : null}
            </div>
            {selectedDocuments.length > 0 ? (
              <div className="selection-chips" aria-label="Ausgewählte PDFs">
                {selectedDocuments.map((document) => (
                  <button
                    aria-label={`${document.filename} aus Auswahl entfernen`}
                    className="selection-chip"
                    key={document.document_id}
                    title={document.filename}
                    type="button"
                    onClick={() => toggleDocumentSelection(document.document_id)}
                  >
                    <span>{document.filename}</span>
                    <X size={14} />
                  </button>
                ))}
              </div>
            ) : null}
            <small>
              {selectedDocuments.length > 0
                ? `${selectedPageCount} Seiten · ${selectedDocumentsReady ? "bereit für Fragen" : "Auswahl noch nicht vollständig bereit"}`
                : "Dokumentkarten anklicken, um RAG zu nutzen"}
            </small>
          </div>

          <div className="suggestion-row">
            {SUGGESTED_QUESTIONS[mode].map((suggestedQuestion) => (
              <button
                key={suggestedQuestion}
                disabled={!selectedDocumentsReady || isAsking}
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
              disabled={!selectedDocumentsReady || isAsking}
              placeholder={selectedDocumentsReady ? "Frage zu den ausgewählten Dokumenten" : selectedDocuments.length > 0 ? "Indexierung abwarten" : "Zuerst PDFs auswählen"}
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
                onChange={(event) =>
                  setPreferences((current) => ({
                    ...current,
                    topK: Math.min(10, Math.max(1, Number(event.target.value) || 1)),
                  }))
                }
              />
            </label>
            <button
              aria-label="Frage absenden"
              className="icon-button"
              disabled={!selectedDocumentsReady || !question.trim() || isAsking}
              type="submit"
            >
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
            <div className="source-groups">
              {sourceGroups.map((group) => (
                <div className="source-group" key={group.documentId}>
                  <div className="source-group-heading">
                    <strong title={group.filename}>{group.filename}</strong>
                    <span>{group.sources.length} {group.sources.length === 1 ? "Quelle" : "Quellen"}</span>
                  </div>
                  <div className="source-grid">
                    {group.sources.map((source) => (
                      <button
                        className="source-item"
                        key={`${source.chunk_id}-${source.page_number}-${source.source_number}`}
                        title={`Quelle öffnen. Interne Quelle: ${source.chunk_id}`}
                        type="button"
                        onClick={() =>
                          setSourceViewer({
                            title: `${source.filename} - Seite ${source.page_number}`,
                            url: getDocumentSourceUrl(source.document_id, source.page_number, source.text_preview),
                          })
                        }
                      >
                        <div>
                          <strong>Quelle {source.source_number} · Seite {source.page_number}</strong>
                        </div>
                        <p>{source.text_preview}</p>
                        <small>Quelle und PDF-Seite öffnen</small>
                      </button>
                    ))}
                  </div>
                </div>
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
    createdAt: document.created_at,
    uploadedAt: formatDocumentTime(document.created_at),
    indexingStatus: document.indexing_status,
    indexingError: document.indexing_error,
    indexingCompletedChunks: document.indexing_completed_chunks,
    indexingTotalChunks: document.indexing_total_chunks,
    indexingQueuePosition: document.indexing_queue_position,
    indexingActive: document.indexing_active,
  };
}

function getIndexingStatusText(document: StoredUiDocument): string {
  if (document.indexingStatus === "ready") {
    return "Bereit";
  }
  if (document.indexingStatus === "failed") {
    return "Indexierung fehlgeschlagen";
  }
  if (document.indexingStatus === "cancelled") {
    return "Indexierung abgebrochen";
  }
  if (document.indexingActive) {
    return document.indexingTotalChunks > 0
      ? `Wird indexiert: ${document.indexingCompletedChunks} / ${document.indexingTotalChunks} Chunks`
      : "Indexierung wird vorbereitet...";
  }
  if (document.indexingQueuePosition !== null) {
    return `Wartet · Position ${document.indexingQueuePosition}`;
  }
  return "Wartet auf Indexierung...";
}

function getErrorActionLabel(context: ErrorContext): string {
  if (context === "ask") {
    return "Frage erneut senden";
  }
  if (context === "upload") {
    return "Datei erneut auswählen";
  }
  if (context === "index") {
    return "Status aktualisieren";
  }
  return "Verbindung prüfen";
}

function getErrorGuidance(error: string, context: ErrorContext): string {
  const normalizedError = error.toLocaleLowerCase("de-DE");
  if (normalizedError.includes("ollama")) {
    return "Prüfe, ob Ollama läuft und die benötigten Modelle lokal installiert sind.";
  }
  if (normalizedError.includes("keine relevanten") || normalizedError.includes("textstellen")) {
    return "Formuliere die Frage konkreter oder erhöhe die Anzahl der Kontextstellen.";
  }
  if (normalizedError.includes("index")) {
    return "Aktualisiere den Status oder starte die Indexierung an der Dokumentkarte erneut.";
  }
  if (context === "upload") {
    return "Prüfe Dateityp, Dateigröße und ob die PDF extrahierbaren Text enthält.";
  }
  if (context === "ask") {
    return "Die Auswahl und Frage bleiben erhalten. Du kannst die Anfrage direkt wiederholen.";
  }
  if (context === "documents") {
    return "Prüfe den lokalen Backend-Prozess auf Port 8000 und versuche die Verbindung erneut.";
  }
  return "Passe die Auswahl an oder schließe die Meldung und versuche es erneut.";
}

function readPersistedDocumentIds(): string[] {
  try {
    const rawValue = window.localStorage.getItem(SELECTION_STORAGE_KEY);
    if (!rawValue) {
      return [];
    }
    const parsedValue = JSON.parse(rawValue) as { version?: unknown; documentIds?: unknown };
    if (parsedValue.version !== 1 || !Array.isArray(parsedValue.documentIds)) {
      return [];
    }
    return parsedValue.documentIds
      .filter((documentId): documentId is string => typeof documentId === "string" && documentId.length > 0)
      .slice(0, MAX_SELECTED_DOCUMENTS);
  } catch {
    return [];
  }
}

function persistDocumentIds(documentIds: string[]) {
  try {
    window.localStorage.setItem(
      SELECTION_STORAGE_KEY,
      JSON.stringify({ version: 1, documentIds: documentIds.slice(0, MAX_SELECTED_DOCUMENTS) }),
    );
  } catch {
    // Die Auswahl funktioniert auch ohne verfuegbaren Browser-Speicher.
  }
}

type AnalysisPreferences = {
  mode: AnalysisMode;
  topK: number;
};

function readPersistedPreferences(): AnalysisPreferences {
  try {
    const rawValue = window.localStorage.getItem(PREFERENCES_STORAGE_KEY);
    if (!rawValue) {
      return { mode: "ask", topK: 5 };
    }
    const parsedValue = JSON.parse(rawValue) as { version?: unknown; mode?: unknown; topK?: unknown };
    const mode = ["ask", "compare", "summarize"].includes(String(parsedValue.mode))
      ? parsedValue.mode as AnalysisMode
      : "ask";
    const topK = typeof parsedValue.topK === "number"
      ? Math.min(10, Math.max(1, Math.round(parsedValue.topK)))
      : 5;
    return parsedValue.version === 1 ? { mode, topK } : { mode: "ask", topK: 5 };
  } catch {
    return { mode: "ask", topK: 5 };
  }
}

function persistPreferences(preferences: AnalysisPreferences) {
  try {
    window.localStorage.setItem(
      PREFERENCES_STORAGE_KEY,
      JSON.stringify({ version: 1, ...preferences }),
    );
  } catch {
    // Standardwerte bleiben ohne Browser-Speicher nutzbar.
  }
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
