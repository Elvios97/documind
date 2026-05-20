from fastapi import FastAPI

from api.ask import router as ask_router
from api.pdf_routes import router as pdf_router
from api.rag import router as rag_router


app = FastAPI(
    title="Documind Local Backend",
    description="Lokales Backend fuer PDF-Upload, Textextraktion, Ollama-Fragen und RAG.",
    version="0.1.0",
)


@app.get("/")
async def healthcheck() -> dict[str, str]:
    """Ein einfacher lokaler Healthcheck fuer die Entwicklung."""
    return {
        "status": "ok",
        "message": "Documind Backend laeuft lokal.",
    }


app.include_router(pdf_router, prefix="/api/pdf", tags=["PDF"])
app.include_router(ask_router, tags=["Ask"])
app.include_router(rag_router, tags=["RAG"])
