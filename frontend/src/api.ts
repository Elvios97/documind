const API_BASE_URL = import.meta.env.VITE_DOCUMIND_API_URL ?? "http://127.0.0.1:8000";

export type UploadResponse = {
  document_id: string;
  filename: string;
  page_count: number;
  full_text: string;
};

export type DocumentSummary = {
  document_id: string;
  filename: string;
  page_count: number;
  created_at: string;
};

export type RagSource = {
  filename: string;
  page_number: number;
  chunk_id: string;
  score: number | null;
  text_preview: string;
};

export type RagResponse = {
  document_id: string;
  question: string;
  answer: string;
  model: string;
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
  const response = await fetch(`${API_BASE_URL}/`);

  return parseResponse<HealthResponse>(response);
}

export async function listDocuments(): Promise<DocumentSummary[]> {
  const response = await fetch(`${API_BASE_URL}/documents`);

  return parseResponse<DocumentSummary[]>(response);
}

export async function deleteDocument(documentId: string): Promise<DeleteDocumentResponse> {
  const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    method: "DELETE",
  });

  return parseResponse<DeleteDocumentResponse>(response);
}

export async function uploadPdf(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/pdf/upload`, {
    method: "POST",
    body: formData,
  });

  return parseResponse<UploadResponse>(response);
}

export async function askWithRag(documentId: string, question: string, topK: number): Promise<RagResponse> {
  const response = await fetch(`${API_BASE_URL}/rag/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      document_id: documentId,
      question,
      top_k: topK,
    }),
  });

  return parseResponse<RagResponse>(response);
}

export function getDocumentPdfUrl(documentId: string, pageNumber: number): string {
  return `${API_BASE_URL}/documents/${encodeURIComponent(documentId)}/file#page=${pageNumber}`;
}

export function getDocumentSourceUrl(documentId: string, pageNumber: number): string {
  return `${API_BASE_URL}/documents/${encodeURIComponent(documentId)}/source/${pageNumber}`;
}

async function parseResponse<T>(response: Response): Promise<T> {
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = data?.detail ?? `HTTP ${response.status}`;
    throw new Error(String(detail));
  }

  return data as T;
}
