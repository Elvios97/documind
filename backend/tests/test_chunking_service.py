import pytest

from models.errors import AppError
from models.pdf import PDFPageText
from services.chunking_service import chunk_document_pages


def test_chunk_document_pages_creates_chunks_with_page_reference() -> None:
    pages = [
        PDFPageText(page_number=1, text="abcdef"),
        PDFPageText(page_number=2, text="ghijkl"),
    ]

    chunks = chunk_document_pages(
        document_id="doc-test",
        pages=pages,
        chunk_size=3,
        chunk_overlap=0,
    )

    assert [chunk.text for chunk in chunks] == ["abc", "def", "ghi", "jkl"]
    assert [chunk.page_number for chunk in chunks] == [1, 1, 2, 2]
    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2, 3]
    assert chunks[0].chunk_id == "doc-test-p0001-c0000"
    assert chunks[2].chunk_id == "doc-test-p0002-c0000"


def test_chunk_document_pages_supports_overlap() -> None:
    pages = [PDFPageText(page_number=1, text="abcdefghij")]

    chunks = chunk_document_pages(
        document_id="doc-test",
        pages=pages,
        chunk_size=4,
        chunk_overlap=2,
    )

    assert [chunk.text for chunk in chunks] == ["abcd", "cdef", "efgh", "ghij"]


def test_chunk_document_pages_skips_empty_pages() -> None:
    pages = [
        PDFPageText(page_number=1, text="   "),
        PDFPageText(page_number=2, text="Inhalt"),
    ]

    chunks = chunk_document_pages(
        document_id="doc-test",
        pages=pages,
        chunk_size=20,
        chunk_overlap=0,
    )

    assert len(chunks) == 1
    assert chunks[0].page_number == 2
    assert chunks[0].text == "Inhalt"


def test_chunk_document_pages_rejects_invalid_settings() -> None:
    pages = [PDFPageText(page_number=1, text="abcdef")]

    with pytest.raises(AppError, match="chunk_size"):
        chunk_document_pages("doc-test", pages, chunk_size=0)

    with pytest.raises(AppError, match="chunk_overlap"):
        chunk_document_pages("doc-test", pages, chunk_size=10, chunk_overlap=-1)

    with pytest.raises(AppError, match="kleiner"):
        chunk_document_pages("doc-test", pages, chunk_size=10, chunk_overlap=10)
