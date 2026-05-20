from pydantic import BaseModel, Field


class RagAskRequest(BaseModel):
    document_id: str = Field(..., examples=["7ffdb5c4-5a42-4ee3-9aa2-47f317bdca10"])
    question: str = Field(..., examples=["Welche Kernaussagen stehen im Dokument?"])
    top_k: int = Field(default=5, ge=1, le=20, examples=[5])


class RagSource(BaseModel):
    filename: str = Field(..., examples=["beispiel.pdf"])
    page_number: int = Field(..., ge=1, examples=[2])
    chunk_id: str = Field(..., examples=["7ffdb5c4-p0002-c0000"])
    score: float | None = Field(default=None, examples=[0.82])
    text_preview: str = Field(..., examples=["Kurzer Auszug aus dem gefundenen Chunk."])


class RagAskResponse(BaseModel):
    document_id: str
    question: str
    answer: str
    model: str
    sources: list[RagSource]
