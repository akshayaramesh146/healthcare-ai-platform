"""Print what ingestion + chunking produce. Run from project root:
python scripts/inspect_chunks.py"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.chunking import chunk_documents
from app.rag.ingestion import load_documents

docs = load_documents()
chunks = chunk_documents(docs)
print(f"{len(docs)} pages -> {len(chunks)} chunks")
print("Chunks per source:", dict(Counter(c['source'] for c in chunks)))
print("\nSample chunk:")
print(chunks[1])
