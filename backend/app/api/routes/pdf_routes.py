"""
PDF Routes - API Endpunkte für PDF-Operationen
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.services.pdf_service import save_uploaded_pdf

router = APIRouter()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload-Endpunkt für PDF-Dateien.
    
    Erwartet:
    - file: PDF-Datei
    
    Gibt zurück:
    - Dateiinformationen und Speicherpfad
    """
    if not file:
        raise HTTPException(status_code=400, detail="Keine Datei hochgeladen")
    
    result = await save_uploaded_pdf(file)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return JSONResponse(content=result, status_code=200)
