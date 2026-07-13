from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.ask import router as ask_router
from api.documents import router as documents_router
from api.pdf_routes import router as pdf_router
from api.rag import router as rag_router
from services.indexing_queue import indexing_queue
from services.pdf_service import index_uploaded_document
from storage.document_store import list_documents


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Setzt nach einem Neustart unterbrochene Indexierungen fort."""
    pending_document_ids = [
        document.document_id
        for document in reversed(list_documents())
        if document.indexing_status == "indexing"
    ]
    indexing_queue.start(index_uploaded_document, pending_document_ids)
    try:
        yield
    finally:
        await indexing_queue.stop()


app = FastAPI(
    title="Documind Local Backend",
    description="Lokales Backend fuer PDF-Upload, Textextraktion, Ollama-Fragen und RAG.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5174",
        "http://localhost:5174",
        "http://tauri.localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def healthcheck() -> dict[str, str]:
    """Ein einfacher lokaler Healthcheck fuer die Entwicklung."""
    return {
        "status": "ok",
        "message": "Documind Backend laeuft lokal.",
    }


app.include_router(pdf_router, prefix="/api/pdf", tags=["PDF"])
app.include_router(documents_router, tags=["Documents"])
app.include_router(ask_router, tags=["Ask"])
app.include_router(rag_router, tags=["RAG"])


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
