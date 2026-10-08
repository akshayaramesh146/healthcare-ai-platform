"""Embedding models. Every embedder returns L2-normalised float32 vectors, so
inner product equals cosine similarity.

- SentenceTransformerEmbedder: the real model (downloads ~90 MB on first use).
- HashEmbedder: tiny deterministic bag-of-words embedder used for offline tests.
"""
import hashlib
import re

import numpy as np

from app import config

_STOP = {"a", "an", "the", "of", "and", "or", "to", "in", "is", "are", "what", "which",
         "for", "on", "with", "do", "does", "how", "i", "my", "can", "be", "by", "as", "it"}


def _normalise(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (vectors / norms).astype("float32")


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str | None = None):
        self.name = model_name or config.EMBEDDING_MODEL
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer  # lazy: heavy import
            self._model = SentenceTransformer(self.name)
        return self._model

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = self._load().encode(list(texts), convert_to_numpy=True,
                                      show_progress_bar=False)
        return _normalise(vectors)


class HashEmbedder:
    """Deterministic hashed bag-of-words. Lexical only; for tests, not production."""
    name = "hash-512"

    def __init__(self, dim: int = 512):
        self.dim = dim

    def embed(self, texts: list[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.dim), dtype="float32")
        for i, text in enumerate(texts):
            for tok in re.findall(r"[a-z0-9]+", text.lower()):
                if tok in _STOP:
                    continue
                h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
                out[i, h % self.dim] += 1.0
        return _normalise(out)


def get_embedder(kind: str = "sentence-transformer"):
    if kind == "hash":
        return HashEmbedder()
    return SentenceTransformerEmbedder()
