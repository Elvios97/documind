from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.ask import router as ask_router
from api.documents import router as documents_router
from api.pdf_routes import router as pdf_router
from api.rag import router as rag_router


app = FastAPI(
    title="Documind Local Backend",
    description="Lokales Backend fuer PDF-Upload, Textextraktion, Ollama-Fragen und RAG.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
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
