"""Split page-level documents into overlapping chunks, keeping source metadata."""
from app import config

SEPARATORS = ["\n\n", ". ", " "]  # try paragraph, then sentence, then word boundaries


def _split(text: str, size: int, overlap: int):
    """Split text into pieces of at most `size` characters with `overlap` between them."""
    if len(text) <= size:
        return [text]
    pieces, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            # back up to the last natural boundary in the second half of the window
            window = text[start:end]
            for sep in SEPARATORS:
                cut = window.rfind(sep)
                if cut > size // 2:
                    end = start + cut + len(sep)
                    break
        pieces.append(text[start:end].strip())
        if end >= len(text):
            break
        next_start = max(end - overlap, start + 1)  # always move forward
        # don't begin the next chunk mid-word: skip ahead to the next space
        space = text.find(" ", next_start, end)
        start = space + 1 if space != -1 else next_start
    return [p for p in pieces if p]


def chunk_documents(docs, chunk_size=None, overlap=None):
    """Return chunk dicts: {chunk_id, text, source, page, topic}."""
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = config.CHUNK_OVERLAP if overlap is None else overlap
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    chunks = []
    for doc in docs:
        for i, piece in enumerate(_split(doc["text"], chunk_size, overlap)):
            chunks.append({
                "chunk_id": f"{doc['source']}::p{doc['page']}::c{i}",
                "text": piece,
                "source": doc["source"],
                "page": doc["page"],
                "topic": doc["topic"],
            })
    return chunks
