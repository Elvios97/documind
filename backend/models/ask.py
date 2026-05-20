from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    document_id: str = Field(..., examples=["7ffdb5c4-5a42-4ee3-9aa2-47f317bdca10"])
    question: str = Field(..., examples=["Worum geht es in diesem Dokument?"])


class AskResponse(BaseModel):
    document_id: str
    question: str
    answer: str
    model: str
    used_context_length: int
