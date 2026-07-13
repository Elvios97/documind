from typing import Literal

from pydantic import BaseModel, Field


AnalysisMode = Literal["ask", "compare", "summarize"]


class RagAskRequest(BaseModel):
    document_ids: list[str] = Field(..., min_length=1, max_length=5)
    question: str = Field(..., examples=["Welche Kernaussagen stehen im Dokument?"])
    top_k: int = Field(default=5, ge=1, le=20, examples=[5])
    mode: AnalysisMode = "ask"


class RagRetrieveRequest(BaseModel):
    document_ids: list[str] = Field(..., min_length=1, max_length=5)
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class RagSource(BaseModel):
    document_id: str
    source_number: int = Field(..., ge=1)
    filename: str = Field(..., examples=["beispiel.pdf"])
    page_number: int = Field(..., ge=1, examples=[2])
    chunk_id: str = Field(..., examples=["7ffdb5c4-p0002-c0000"])
    score: float | None = Field(default=None, examples=[0.82])
    text_preview: str = Field(..., examples=["Kurzer Auszug aus dem gefundenen Chunk."])


class RagAskResponse(BaseModel):
    document_ids: list[str]
    question: str
    answer: str
    model: str
    mode: AnalysisMode
    sources: list[RagSource]


class RagRetrieveResponse(BaseModel):
    document_ids: list[str]
    question: str
    sources: list[RagSource]
