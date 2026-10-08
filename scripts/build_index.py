"""Build and save the vector index. Run from project root:
python scripts/build_index.py            (real model; downloads it on first run)
python scripts/build_index.py --hash     (offline test embedder)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import config
from app.rag.retrieval import build_index, faiss

kind = "hash" if "--hash" in sys.argv else "sentence-transformer"
store = build_index(kind)
print(f"Indexed {len(store.chunks)} chunks with '{store.embedder.name}' "
      f"({'FAISS' if faiss else 'numpy fallback'}) -> {config.VECTOR_STORE_PATH}")
