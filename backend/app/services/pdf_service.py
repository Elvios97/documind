"""
PDF Service - Handelt PDF-Operationen wie Upload und Speicherung
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from app.core.config import UPLOADS_DIR, ALLOWED_EXTENSIONS


async def save_uploaded_pdf(file) -> Dict[str, Any]:
    """
    Speichert eine hochgeladene PDF-Datei im uploads Verzeichnis.
    
    Args:
        file: UploadFile Objekt von FastAPI
        
    Returns:
        Dictionary mit Dateimetadaten:
        {
            "filename": str,
            "original_filename": str,
            "content_type": str,
            "file_path": str,
            "file_size": int,
            "upload_timestamp": str,
            "status": "success" oder "error",
            "message": str
        }
    """
    try:
        # Validiere Dateiendung
        file_extension = Path(file.filename).suffix.lower().lstrip('.')
        if file_extension not in ALLOWED_EXTENSIONS:
            return {
                "status": "error",
                "message": f"Nur PDF-Dateien erlaubt. Erhielt: {file_extension}"
            }
        
        # Erstelle eindeutigen Dateinamen mit Timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        
        # Vollständiger Pfad zur Datei
        file_path = UPLOADS_DIR / safe_filename
        
        # Speichere Datei
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Hole Dateigröße
        file_size = len(content)
        
        return {
            "status": "success",
            "filename": safe_filename,
            "original_filename": file.filename,
            "content_type": file.content_type,
            "file_path": str(file_path),
            "file_size": file_size,
            "upload_timestamp": datetime.now().isoformat(),
            "message": "PDF erfolgreich hochgeladen"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Fehler beim Speichern der Datei: {str(e)}"
        }
