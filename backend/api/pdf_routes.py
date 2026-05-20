from fastapi import APIRouter, File, HTTPException, UploadFile

from models.errors import AppError
from models.pdf import PDFUploadResponse
from services.pdf_service import process_uploaded_pdf


router = APIRouter()


@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile | None = File(default=None)) -> PDFUploadResponse:
    """
    Nimmt eine PDF-Datei entgegen, speichert sie lokal und extrahiert Text.

    Es wird keine Cloud, kein Login und keine externe API verwendet.
    """
    try:
        return await process_uploaded_pdf(file)
    except AppError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error
