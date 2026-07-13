from pydantic import BaseModel, Field

from models.indexing import IndexingStatus
from models.pdf import PDFPageText

class StoredDocument(BaseModel):
    document_id: str
    file_name: str
    page_count: int
    pages: list[PDFPageText]
    full_text: str = Field(..., min_length=1)
    created_at: str
    indexing_status: IndexingStatus = "ready"
    indexing_error: str | None = None
    indexing_completed_chunks: int = Field(default=0, ge=0)
    indexing_total_chunks: int = Field(default=0, ge=0)


class DocumentSummary(BaseModel):
    document_id: str
    filename: str
    page_count: int
    created_at: str
    indexing_status: IndexingStatus
    indexing_error: str | None = None
    indexing_completed_chunks: int = Field(default=0, ge=0)
    indexing_total_chunks: int = Field(default=0, ge=0)
    indexing_queue_position: int | None = Field(default=None, ge=0)
    indexing_active: bool = False


class DocumentDetail(DocumentSummary):
    pages: list[PDFPageText]
    full_text: str


class DeleteDocumentResponse(BaseModel):
    document_id: str
    deleted: bool
