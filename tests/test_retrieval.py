"""Phase 2b tests (offline, using the hash embedder).
Run from project root: python tests/test_retrieval.py
Real-model quality is checked with scripts/search.py instead."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from app.rag.chunking import chunk_documents
from app.rag.embeddings import HashEmbedder
from app.rag.ingestion import load_documents
from app.rag.retrieval import VectorStore


def _store():
    return VectorStore(HashEmbedder()).build(chunk_documents(load_documents()))


def test_embedder_shape_and_norm():
    v = HashEmbedder().embed(["blood pressure", "diabetes symptoms"])
    assert v.shape == (2, 512) and v.dtype == np.float32
    assert np.allclose(np.linalg.norm(v, axis=1), 1.0, atol=1e-5)


def test_retrieves_right_document():
    store = _store()
    top = [r["source"] for r in store.search("symptoms of type 2 diabetes", k=3)]
    assert top[0] == "diabetes_guidelines.pdf", top
    top = [r["source"] for r in store.search("risk factors for hypertension", k=3)]
    assert "hypertension_guidelines.pdf" in top, top


def test_scores_sorted_and_k_respected():
    res = _store().search("blood pressure categories", k=4)
    assert len(res) == 4
    assert [r["score"] for r in res] == sorted((r["score"] for r in res), reverse=True)
    assert all({"text", "source", "page", "topic", "score"} <= r.keys() for r in res)


def test_topic_filter():
    res = _store().search("what should I eat", k=5, topic="nutrition")
    assert res and all(r["topic"] == "nutrition" for r in res)
    res = _store().search("anything", k=5, source="heart_health.pdf")
    assert res and all(r["source"] == "heart_health.pdf" for r in res)


def test_save_load_roundtrip():
    store = _store()
    with tempfile.TemporaryDirectory() as d:
        store.save(d)
        loaded = VectorStore.load(HashEmbedder(), d)
    q = "medication side effects allergies"
    assert [r["chunk_id"] for r in store.search(q)] == [r["chunk_id"] for r in loaded.search(q)]


def test_embedder_mismatch_rejected():
    class Other(HashEmbedder):
        name = "other"
    with tempfile.TemporaryDirectory() as d:
        _store().save(d)
        try:
            VectorStore.load(Other(), d)
        except ValueError:
            return
    raise AssertionError("expected ValueError")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
