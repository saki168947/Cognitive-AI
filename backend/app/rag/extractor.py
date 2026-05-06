"""Document text extraction with format-aware parsing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass
class PageText:
    """Extracted text from a single page/section."""

    page_number: int
    text: str


def extract_pdf(file_path: str) -> list[PageText]:
    """Extract text page-by-page from a PDF file."""
    reader = PdfReader(file_path)
    pages: list[PageText] = []
    for i, page in enumerate(reader.pages):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(PageText(page_number=i + 1, text=text))
    return pages


def extract_text_file(file_path: str) -> list[PageText]:
    """Extract text from plain text files (.txt, .md, etc.)."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read().strip()
    return [PageText(page_number=1, text=text)] if text else []


def extract(file_path: str) -> list[PageText]:
    """Route to the appropriate extractor based on file extension."""
    ext = Path(file_path).suffix.lower().lstrip(".")
    if ext == "pdf":
        return extract_pdf(file_path)
    if ext in ("txt", "md", "markdown", "rst"):
        return extract_text_file(file_path)
    # Fallback: try as text
    return extract_text_file(file_path)
