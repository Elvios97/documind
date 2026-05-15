"""
Configuration for documind backend
"""
import os
from pathlib import Path

# Basis Pfade
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"

# Stelle sicher, dass der uploads Ordner existiert
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# FastAPI Settings
API_V1_STR = "/api"
PROJECT_NAME = "documind - PDF AI App"

# PDF Upload Settings
ALLOWED_EXTENSIONS = {"pdf"}
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB
