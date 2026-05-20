from models.chunk import TextChunk
from models.errors import AppError
from models.pdf import PDFPageText


DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150


def chunk_document_pages(
    document_id: str,
    pages: list[PDFPageText],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[TextChunk]:
    """Teilt PDF-Seitentexte in ueberlappende Chunks mit Seitenbezug."""
    _validate_chunk_settings(chunk_size, chunk_overlap)

    chunks: list[TextChunk] = []
    chunk_index = 0

    for page in pages:
        page_text = page.text.strip()
        if not page_text:
            continue

        page_chunk_index = 0
        for chunk_text in _split_text(page_text, chunk_size, chunk_overlap):
            chunks.append(
                TextChunk(
                    document_id=document_id,
                    chunk_id=_build_chunk_id(document_id, page.page_number, page_chunk_index),
                    chunk_index=chunk_index,
                    page_number=page.page_number,
                    text=chunk_text,
                )
            )
            chunk_index += 1
            page_chunk_index += 1

    return chunks


def _validate_chunk_settings(chunk_size: int, chunk_overlap: int) -> None:
    if chunk_size <= 0:
        raise AppError(400, "chunk_size muss groesser als 0 sein.")

    if chunk_overlap < 0:
        raise AppError(400, "chunk_overlap darf nicht negativ sein.")

    if chunk_overlap >= chunk_size:
        raise AppError(400, "chunk_overlap muss kleiner als chunk_size sein.")


def _split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    chunks: list[str] = []
    step = chunk_size - chunk_overlap
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(chunk_text)

        if end >= len(text):
            break

        start += step

    return chunks


def _build_chunk_id(document_id: str, page_number: int, page_chunk_index: int) -> str:
    return f"{document_id}-p{page_number:04d}-c{page_chunk_index:04d}"
