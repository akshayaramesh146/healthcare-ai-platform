"""Document ingestion: load PDF / TXT / DOCX files and return clean page-level text.

No LLM is involved here. Ingestion is kept separate from AI generation so it can be
tested and changed independently.
"""
import re
from pathlib import Path

from app import config

SUPPORTED = {".pdf", ".txt", ".docx"}


def clean(text: str) -> str:
    """Normalise whitespace and remove common extraction noise."""
    text = text.replace("\x00", "")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)           # re-join hyphenated line breaks
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if not re.fullmatch(r"(page\s*)?\d+", ln, re.I)]  # bare page numbers
    text = "\n".join(lines)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # single newlines inside a paragraph become spaces; blank lines stay as separators
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    return text.strip()


def _topic_for(path: Path) -> str:
    return config.TOPIC_BY_FILE.get(path.stem, "general")


def _read_pdf(path: Path):
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    for page_number, page in enumerate(reader.pages, start=1):
        yield page_number, page.extract_text() or ""


def _read_txt(path: Path):
    yield 1, path.read_text(encoding="utf-8", errors="ignore")


def _read_docx(path: Path):
    from docx import Document  # pip install python-docx
    yield 1, "\n".join(p.text for p in Document(str(path)).paragraphs)


_READERS = {".pdf": _read_pdf, ".txt": _read_txt, ".docx": _read_docx}


def load_documents(directory=None):
    """Return a list of {text, source, page, topic} dicts, one per page."""
    directory = Path(directory or config.DOCUMENTS_DIR)
    docs = []
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() not in SUPPORTED:
            continue
        for page, raw in _READERS[path.suffix.lower()](path):
            text = clean(raw)
            if text:  # skip empty / image-only pages
                docs.append({"text": text, "source": path.name,
                             "page": page, "topic": _topic_for(path)})
    return docs
