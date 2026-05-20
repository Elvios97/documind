from pydantic import BaseModel, Field


class TextChunk(BaseModel):
    document_id: str = Field(..., examples=["7ffdb5c4-5a42-4ee3-9aa2-47f317bdca10"])
    chunk_id: str = Field(..., examples=["7ffdb5c4-p0001-c0001"])
    chunk_index: int = Field(..., ge=0, examples=[0])
    page_number: int = Field(..., ge=1, examples=[1])
    text: str = Field(..., min_length=1, examples=["Ein Ausschnitt aus dem PDF-Text."])


class RetrievedChunk(TextChunk):
    score: float | None = Field(default=None, examples=[0.82])


class DocumentIndexResult(BaseModel):
    document_id: str = Field(..., examples=["7ffdb5c4-5a42-4ee3-9aa2-47f317bdca10"])
    chunk_count: int = Field(..., ge=0, examples=[12])
    embedding_model: str = Field(..., examples=["nomic-embed-text"])
