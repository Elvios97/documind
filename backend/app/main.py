"""
FastAPI Hauptanwendung für documind Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import PROJECT_NAME, API_V1_STR
from app.api.routes import pdf_routes

# Erstelle FastAPI App
app = FastAPI(title=PROJECT_NAME)

# CORS Middleware - erlaubt später Frontend-Zugriff
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Später einschränken auf localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Healthcheck Endpunkt
@app.get("/")
async def healthcheck():
    """
    Healthcheck Endpunkt
    """
    return JSONResponse(
        content={"message": "PDF AI App Backend läuft"},
        status_code=200
    )


# Registriere PDF Routes
app.include_router(
    pdf_routes.router,
    prefix=f"{API_V1_STR}/pdf",
    tags=["pdf"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
