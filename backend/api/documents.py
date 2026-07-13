from html import escape

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse

from models.document import DeleteDocumentResponse, DocumentDetail, DocumentSummary
from models.errors import AppError
from services.document_service import delete_document, get_document
from services.indexing_queue import indexing_queue
from storage.document_store import (
    list_documents,
    update_document_indexing_progress,
    update_document_indexing_status,
)
from storage.file_storage import get_pdf_file_for_document


router = APIRouter()


@router.get("/documents", response_model=list[DocumentSummary])
async def get_documents() -> list[DocumentSummary]:
    """Liefert lokal gespeicherte Dokumente fuer die Frontend-Sidebar."""
    return [_with_queue_state(document) for document in list_documents()]


@router.get("/documents/{document_id}", response_model=DocumentDetail)
async def get_document_by_id(document_id: str) -> DocumentDetail:
    """Liefert Detaildaten zu einem lokal gespeicherten Dokument."""
    try:
        return _with_queue_state(get_document(document_id))
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
async def get_document_source_view(
    document_id: str,
    page_number: int,
    highlight: str | None = Query(default=None, max_length=500),
) -> HTMLResponse:
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
            highlight=highlight,
        )
    )


@router.delete("/documents/{document_id}", response_model=DeleteDocumentResponse)
async def delete_document_by_id(document_id: str) -> DeleteDocumentResponse:
    """Loescht ein Dokument lokal inklusive Upload und RAG-Chunks."""
    try:
        await indexing_queue.cancel(document_id)
        return delete_document(document_id)
    except AppError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error


@router.post("/documents/{document_id}/index", response_model=DocumentDetail)
async def retry_document_indexing(document_id: str) -> DocumentDetail:
    """Stellt ein Dokument erneut in die lokale Indexierungsqueue."""
    try:
        get_document(document_id)
        if indexing_queue.contains(document_id):
            raise AppError(409, "Das Dokument befindet sich bereits in der Indexierungsqueue.")
        update_document_indexing_progress(document_id, 0, 0)
        update_document_indexing_status(document_id, "indexing")
        indexing_queue.enqueue(document_id)
        return _with_queue_state(get_document(document_id))
    except AppError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error
    except RuntimeError as error:
        update_document_indexing_status(document_id, "failed", "Indexierungsqueue ist nicht gestartet.")
        raise HTTPException(status_code=503, detail="Indexierungsqueue ist nicht gestartet.") from error


@router.post("/documents/{document_id}/index/cancel", response_model=DocumentDetail)
async def cancel_document_indexing(document_id: str) -> DocumentDetail:
    """Bricht eine aktive oder wartende Indexierung ab."""
    try:
        document = get_document(document_id)
        if document.indexing_status != "indexing":
            raise AppError(409, "Das Dokument wird aktuell nicht indexiert.")
        await indexing_queue.cancel(document_id)
        update_document_indexing_status(document_id, "cancelled")
        return _with_queue_state(get_document(document_id))
    except AppError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error


def _with_queue_state(document: DocumentSummary | DocumentDetail):
    return document.model_copy(
        update={
            "indexing_queue_position": indexing_queue.get_position(document.document_id),
            "indexing_active": indexing_queue.is_active(document.document_id),
        }
    )


def _build_source_view_html(
    filename: str,
    page_number: int,
    page_count: int,
    page_text: str,
    pdf_url: str,
    highlight: str | None = None,
) -> str:
    safe_filename = escape(filename)
    highlighted_page_text = _highlight_page_text(
        page_text or "Fuer diese Seite wurde kein extrahierbarer Text gefunden.",
        highlight,
    )
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
      grid-template-columns: minmax(0, 1fr) 10px minmax(320px, var(--text-width, 430px));
      gap: 0;
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
    .splitter {{
      position: relative;
      width: 10px;
      height: calc(100vh - 104px);
      cursor: col-resize;
    }}
    .splitter::after {{
      content: "";
      position: absolute;
      inset: 0 4px;
      border-radius: 999px;
      background: #c8d3dd;
    }}
    .splitter:hover::after,
    .splitter.dragging::after {{
      background: #1f7568;
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
    mark {{
      padding: 2px 3px;
      color: inherit;
      border-radius: 4px;
      background: #fff2a8;
      box-shadow: 0 0 0 1px rgba(174, 125, 0, 0.18);
    }}
    @media (max-width: 980px) {{
      main {{ grid-template-columns: 1fr; gap: 12px; }}
      iframe, section {{ height: 72vh; }}
      .splitter {{ display: none; }}
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
      <div aria-hidden="true" class="splitter"></div>
      <section>
        <h2>Extrahierter Text dieser Seite</h2>
        <pre>{highlighted_page_text}</pre>
      </section>
    </main>
  </div>
  <script>
    const splitter = document.querySelector(".splitter");
    const main = document.querySelector("main");
    let isDragging = false;

    document.querySelectorAll("a[target]").forEach((link) => {{
      link.removeAttribute("target");
      link.removeAttribute("rel");
      link.textContent = "Nur PDF anzeigen";
    }});

    splitter?.addEventListener("pointerdown", (event) => {{
      isDragging = true;
      splitter.classList.add("dragging");
      splitter.setPointerCapture(event.pointerId);
    }});

    splitter?.addEventListener("pointermove", (event) => {{
      if (!isDragging || !main) {{
        return;
      }}

      const bounds = main.getBoundingClientRect();
      const textWidth = Math.min(Math.max(bounds.right - event.clientX, 320), bounds.width * 0.7);
      main.style.setProperty("--text-width", `${{textWidth}}px`);
    }});

    splitter?.addEventListener("pointerup", (event) => {{
      isDragging = false;
      splitter.classList.remove("dragging");
      splitter.releasePointerCapture(event.pointerId);
    }});

    document.querySelector("mark")?.scrollIntoView({{ block: "center", inline: "nearest" }});
  </script>
</body>
</html>"""


def _highlight_page_text(page_text: str, highlight: str | None) -> str:
    if not highlight:
        return escape(page_text)

    normalized_highlight = " ".join(highlight.split()).removesuffix("...")
    if len(normalized_highlight) < 12:
        return escape(page_text)

    match = _find_fuzzy_text_match(page_text, normalized_highlight)
    if match is None:
        return escape(page_text)

    start, end = match
    return f"{escape(page_text[:start])}<mark>{escape(page_text[start:end])}</mark>{escape(page_text[end:])}"


def _find_fuzzy_text_match(page_text: str, highlight: str) -> tuple[int, int] | None:
    compact_page, page_mapping = _compact_with_mapping(page_text)
    compact_page = compact_page.casefold()
    compact_highlight = " ".join(highlight.split()).casefold()

    match_index = compact_page.find(compact_highlight)
    if match_index == -1:
        compact_highlight = compact_highlight[:160].strip()
        match_index = compact_page.find(compact_highlight)

    if match_index == -1:
        return None

    end_index = match_index + len(compact_highlight) - 1
    if match_index >= len(page_mapping) or end_index >= len(page_mapping):
        return None

    return page_mapping[match_index], page_mapping[end_index] + 1


def _compact_with_mapping(value: str) -> tuple[str, list[int]]:
    chars: list[str] = []
    mapping: list[int] = []
    previous_was_space = True

    for index, char in enumerate(value):
        if char.isspace():
            if not previous_was_space:
                chars.append(" ")
                mapping.append(index)
            previous_was_space = True
            continue

        chars.append(char)
        mapping.append(index)
        previous_was_space = False

    if chars and chars[-1] == " ":
        chars.pop()
        mapping.pop()

    return "".join(chars), mapping
