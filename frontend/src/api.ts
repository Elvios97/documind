const API_BASE_URL = import.meta.env.VITE_DOCUMIND_API_URL ?? "http://127.0.0.1:8000";

export type IndexingStatus = "indexing" | "ready" | "failed" | "cancelled";
export type AnalysisMode = "ask" | "compare" | "summarize";

export type UploadResponse = {
  document_id: string;
  filename: string;
  page_count: number;
  full_text: string;
  indexing_status: IndexingStatus;
  indexing_completed_chunks: number;
  indexing_total_chunks: number;
};

export type DocumentSummary = {
  document_id: string;
  filename: string;
  page_count: number;
  created_at: string;
  indexing_status: IndexingStatus;
  indexing_error: string | null;
  indexing_completed_chunks: number;
  indexing_total_chunks: number;
  indexing_queue_position: number | null;
  indexing_active: boolean;
};

export type RagSource = {
  document_id: string;
  source_number: number;
  filename: string;
  page_number: number;
  chunk_id: string;
  score: number | null;
  text_preview: string;
};

export type RagResponse = {
  document_ids: string[];
  question: string;
  answer: string;
  model: string;
  mode: AnalysisMode;
  sources: RagSource[];
};

export type HealthResponse = {
  status: string;
  message: string;
};

export type DeleteDocumentResponse = {
  document_id: string;
  deleted: boolean;
};

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetchApi(`${API_BASE_URL}/`);

  return parseResponse<HealthResponse>(response);
}

export async function listDocuments(): Promise<DocumentSummary[]> {
  const response = await fetchApi(`${API_BASE_URL}/documents`);

  return parseResponse<DocumentSummary[]>(response);
}

export async function deleteDocument(documentId: string): Promise<DeleteDocumentResponse> {
  const response = await fetchApi(`${API_BASE_URL}/documents/${documentId}`, {
    method: "DELETE",
  });

  return parseResponse<DeleteDocumentResponse>(response);
}

export async function retryDocumentIndexing(documentId: string): Promise<DocumentSummary> {
  const response = await fetchApi(`${API_BASE_URL}/documents/${documentId}/index`, { method: "POST" });
  return parseResponse<DocumentSummary>(response);
}

export async function cancelDocumentIndexing(documentId: string): Promise<DocumentSummary> {
  const response = await fetchApi(`${API_BASE_URL}/documents/${documentId}/index/cancel`, { method: "POST" });
  return parseResponse<DocumentSummary>(response);
}

export async function uploadPdf(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetchApi(`${API_BASE_URL}/api/pdf/upload`, {
    method: "POST",
    body: formData,
  });

  return parseResponse<UploadResponse>(response);
}

export async function askWithRag(
  documentIds: string[],
  question: string,
  topK: number,
  mode: AnalysisMode,
): Promise<RagResponse> {
  const response = await fetchApi(`${API_BASE_URL}/rag/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      document_ids: documentIds,
      question,
      top_k: topK,
      mode,
    }),
  });

  return parseResponse<RagResponse>(response);
}

export function getDocumentPdfUrl(documentId: string, pageNumber: number): string {
  return `${API_BASE_URL}/documents/${encodeURIComponent(documentId)}/file#page=${pageNumber}`;
}

export function getDocumentSourceUrl(documentId: string, pageNumber: number, highlight?: string): string {
  const url = new URL(`${API_BASE_URL}/documents/${encodeURIComponent(documentId)}/source/${pageNumber}`);

  if (highlight?.trim()) {
    url.searchParams.set("highlight", highlight.trim());
  }

  return url.toString();
}

async function parseResponse<T>(response: Response): Promise<T> {
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = data?.detail ?? `HTTP ${response.status}`;
    throw new Error(String(detail));
  }

  return data as T;
}

async function fetchApi(input: string, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(input, init);
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error("Das lokale Backend ist nicht erreichbar. Starte Documind erneut oder prüfe Port 8000.");
    }

    throw error;
  }
}
