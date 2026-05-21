from pydantic import BaseModel, Field

from models.pdf import PDFPageText


class StoredDocument(BaseModel):
    document_id: str
    file_name: str
    page_count: int
    pages: list[PDFPageText]
    full_text: str = Field(..., min_length=1)
    created_at: str


class DocumentSummary(BaseModel):
    document_id: str
    filename: str
    page_count: int
    created_at: str


class DocumentDetail(DocumentSummary):
    pages: list[PDFPageText]
    full_text: str


class DeleteDocumentResponse(BaseModel):
    document_id: str
    deleted: bool
