"""Vector store + retriever.

Uses FAISS (IndexFlatIP over normalised vectors = cosine similarity) when it is
installed, and falls back to a plain numpy search otherwise, so the logic can be
tested anywhere. Metadata filtering (topic / source) is applied to the results.
"""
import json
from pathlib import Path

import numpy as np

from app import config
from app.rag.chunking import chunk_documents
from app.rag.embeddings import get_embedder
from app.rag.ingestion import load_documents

try:
    import faiss
except ImportError:  # numpy fallback
    faiss = None


class VectorStore:
    def __init__(self, embedder):
        self.embedder = embedder
        self.chunks: list[dict] = []
        self.vectors: np.ndarray | None = None
        self._index = None

    # ---- build / search ------------------------------------------------
    def build(self, chunks: list[dict]):
        self.chunks = list(chunks)
        self.vectors = self.embedder.embed([c["text"] for c in self.chunks])
        self._make_index()
        return self

    def _make_index(self):
        if faiss is not None:
            self._index = faiss.IndexFlatIP(self.vectors.shape[1])
            self._index.add(self.vectors)

    def _scores(self, query_vec: np.ndarray, n: int):
        """Return (indices, scores) of the top-n chunks."""
        if self._index is not None:
            scores, idx = self._index.search(query_vec, n)
            return idx[0], scores[0]
        sims = (self.vectors @ query_vec[0])
        idx = np.argsort(-sims)[:n]
        return idx, sims[idx]

    def search(self, query: str, k: int | None = None, topic: str | None = None,
               source: str | None = None) -> list[dict]:
        k = k or config.TOP_K
        filtering = topic is not None or source is not None
        # With a filter, rank every chunk then filter. Fine for a small corpus;
        # at scale use pre-filtering or over-fetch (or a store with native filters).
        n = len(self.chunks) if filtering else min(k, len(self.chunks))
        idx, scores = self._scores(self.embedder.embed([query]), n)
        results = []
        for i, score in zip(idx, scores):
            if i < 0:
                continue
            chunk = self.chunks[int(i)]
            if topic and chunk["topic"] != topic:
                continue
            if source and chunk["source"] != source:
                continue
            results.append({**chunk, "score": float(score)})
            if len(results) == k:
                break
        return results

    # ---- persistence ---------------------------------------------------
    def save(self, directory=None):
        directory = Path(directory or config.VECTOR_STORE_PATH)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "chunks.json").write_text(json.dumps(self.chunks), encoding="utf-8")
        np.save(directory / "vectors.npy", self.vectors)
        (directory / "meta.json").write_text(
            json.dumps({"embedder": self.embedder.name, "count": len(self.chunks)}))
        if faiss is not None:
            faiss.write_index(self._index, str(directory / "index.faiss"))

    @classmethod
    def load(cls, embedder, directory=None):
        directory = Path(directory or config.VECTOR_STORE_PATH)
        meta = json.loads((directory / "meta.json").read_text())
        if meta["embedder"] != embedder.name:
            raise ValueError(f"Index was built with '{meta['embedder']}', "
                             f"but embedder is '{embedder.name}'. Rebuild the index.")
        store = cls(embedder)
        store.chunks = json.loads((directory / "chunks.json").read_text(encoding="utf-8"))
        store.vectors = np.load(directory / "vectors.npy")
        if faiss is not None and (directory / "index.faiss").exists():
            store._index = faiss.read_index(str(directory / "index.faiss"))
        else:
            store._make_index()
        return store


def build_index(embedder_kind="sentence-transformer", directory=None) -> VectorStore:
    """ingest -> chunk -> embed -> index -> save."""
    chunks = chunk_documents(load_documents())
    store = VectorStore(get_embedder(embedder_kind)).build(chunks)
    store.save(directory)
    return store


def load_retriever(embedder_kind="sentence-transformer", directory=None) -> VectorStore:
    return VectorStore.load(get_embedder(embedder_kind), directory)
