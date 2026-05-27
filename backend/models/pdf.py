from pydantic import BaseModel, Field


class PDFPageText(BaseModel):
    page_number: int = Field(..., examples=[1])
    text: str = Field(..., examples=["Text der ersten Seite"])


class PDFUploadResponse(BaseModel):
    document_id: str = Field(..., examples=["7ffdb5c4-5a42-4ee3-9aa2-47f317bdca10"])
    filename: str = Field(..., examples=["rechnung.pdf"])
    page_count: int = Field(..., examples=[3])
    pages: list[PDFPageText]
    full_text: str = Field(..., examples=["Gesamter extrahierter Text"])
