from html import escape

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from models.document import DeleteDocumentResponse, DocumentDetail, DocumentSummary
from models.errors import AppError
from services.document_service import delete_document, get_document
from storage.document_store import list_documents
from storage.file_storage import get_pdf_file_for_document


router = APIRouter()


@router.get("/documents", response_model=list[DocumentSummary])
async def get_documents() -> list[DocumentSummary]:
    """Liefert lokal gespeicherte Dokumente fuer die Frontend-Sidebar."""
    return list_documents()


@router.get("/documents/{document_id}", response_model=DocumentDetail)
async def get_document_by_id(document_id: str) -> DocumentDetail:
    """Liefert Detaildaten zu einem lokal gespeicherten Dokument."""
    try:
        return get_document(document_id)
    except AppError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error


@router.get("/documents/{document_id}/file")
async def get_document_file(document_id: str) -> FileResponse:
    """Oeffnet die lokal gespeicherte PDF-Datei im Browser oder in Tauri."""
    try:
        document = get_document(document_id)
        pdf_path = get_pdf_file_for_document(document_id)
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=document.filename,
            content_disposition_type="inline",
        )
    except AppError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error


@router.get("/documents/{document_id}/source/{page_number}", response_class=HTMLResponse)
async def get_document_source_view(document_id: str, page_number: int) -> HTMLResponse:
    """Zeigt eine Quellenansicht mit PDF-Embed und extrahiertem Seitentext."""
    try:
        document = get_document(document_id)
        get_pdf_file_for_document(document_id)
    except AppError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    if page_number < 1 or page_number > document.page_count:
        raise HTTPException(status_code=400, detail="Ungueltige Seitenzahl.")

    page_text = next((page.text for page in document.pages if page.page_number == page_number), "")
    pdf_url = f"/documents/{document_id}/file#page={page_number}"

    return HTMLResponse(
        content=_build_source_view_html(
            filename=document.filename,
            page_number=page_number,
            page_count=document.page_count,
            page_text=page_text,
            pdf_url=pdf_url,
        )
    )


@router.delete("/documents/{document_id}", response_model=DeleteDocumentResponse)
async def delete_document_by_id(document_id: str) -> DeleteDocumentResponse:
    """Loescht ein Dokument lokal inklusive Upload und RAG-Chunks."""
    try:
        return delete_document(document_id)
    except AppError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error


def _build_source_view_html(
    filename: str,
    page_number: int,
    page_count: int,
    page_text: str,
    pdf_url: str,
) -> str:
    safe_filename = escape(filename)
    safe_page_text = escape(page_text or "Für diese Seite wurde kein extrahierbarer Text gefunden.")
    safe_pdf_url = escape(pdf_url, quote=True)

    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Documind Quelle - Seite {page_number}</title>
  <style>
    :root {{
      color: #172233;
      background: #eef3f7;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; }}
    .shell {{
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
      min-height: 100vh;
    }}
    header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 22px;
      border-bottom: 1px solid #d7e1e8;
      background: #ffffff;
    }}
    h1 {{
      margin: 0;
      font-size: 1.1rem;
    }}
    p {{ margin: 6px 0 0; color: #607086; }}
    a {{
      color: #1f7568;
      font-weight: 800;
      text-decoration: none;
    }}
    main {{
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(340px, 0.65fr);
      gap: 16px;
      min-height: 0;
      padding: 16px;
    }}
    iframe, section {{
      min-height: 0;
      border: 1px solid #d7e1e8;
      border-radius: 8px;
      background: #ffffff;
      box-shadow: 0 18px 44px rgba(23, 34, 51, 0.06);
    }}
    iframe {{
      width: 100%;
      height: calc(100vh - 104px);
    }}
    section {{
      height: calc(100vh - 104px);
      overflow: auto;
      padding: 18px;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 0.95rem;
    }}
    pre {{
      margin: 0;
      color: #253142;
      font: inherit;
      line-height: 1.6;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }}
    @media (max-width: 980px) {{
      main {{ grid-template-columns: 1fr; }}
      iframe, section {{ height: 72vh; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <header>
      <div>
        <h1>{safe_filename}</h1>
        <p>Quelle: Seite {page_number} von {page_count}</p>
      </div>
      <a href="{safe_pdf_url}" target="_blank" rel="noreferrer">PDF direkt öffnen</a>
    </header>
    <main>
      <iframe src="{safe_pdf_url}" title="PDF Seite {page_number}"></iframe>
      <section>
        <h2>Extrahierter Text dieser Seite</h2>
        <pre>{safe_page_text}</pre>
      </section>
    </main>
  </div>
</body>
</html>"""
