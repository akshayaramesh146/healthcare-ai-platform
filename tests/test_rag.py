"""Phase 2a tests: ingestion + chunking. Run from project root: python tests/test_rag.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import config
from app.rag.chunking import chunk_documents
from app.rag.ingestion import clean, load_documents


def test_clean():
    raw = "Blood pres-\nsure is   high.\n\n\n\n12\nNext   paragraph\nline two."
    out = clean(raw)
    assert "pressure" in out
    assert "\n12\n" not in out and not out.endswith("12")
    assert "  " not in out
    assert "Next paragraph line two." in out


def test_load_documents():
    docs = load_documents()
    sources = {d["source"] for d in docs}
    assert len(sources) == 7, sources
    assert all({"text", "source", "page", "topic"} <= d.keys() for d in docs)
    assert any(d["page"] > 1 for d in docs), "expected multi-page documents"
    topics = {d["source"]: d["topic"] for d in docs}
    assert topics["diabetes_guidelines.pdf"] == "diabetes"
    assert topics["hypertension_guidelines.pdf"] == "hypertension"


def test_chunk_sizes_and_metadata():
    docs = load_documents()
    chunks = chunk_documents(docs, chunk_size=500, overlap=80)
    assert len(chunks) > len(docs)
    assert all(len(c["text"]) <= 500 for c in chunks)
    assert len({c["chunk_id"] for c in chunks}) == len(chunks)
    assert all(c["source"] and c["page"] >= 1 and c["topic"] for c in chunks)


def test_chunk_overlap_and_coverage():
    text = ". ".join(f"Sentence number {i} about health" for i in range(60))
    doc = [{"text": text, "source": "x.txt", "page": 1, "topic": "general"}]
    chunks = chunk_documents(doc, chunk_size=300, overlap=60)
    assert len(chunks) > 1
    for a, b in zip(chunks, chunks[1:]):          # consecutive chunks share text
        assert a["text"][-20:] in b["text"] or b["text"][:20] in a["text"]
    assert chunks[0]["text"].startswith("Sentence number 0")
    assert "Sentence number 59" in chunks[-1]["text"]


def test_bad_overlap_rejected():
    try:
        chunk_documents([{"text": "a", "source": "x", "page": 1, "topic": "g"}], 100, 100)
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_content_present():
    chunks = chunk_documents(load_documents())
    joined = " ".join(c["text"] for c in chunks).lower()
    for phrase in ("increased thirst", "family history", "130 to 139"):
        assert phrase in joined, phrase


def test_chunks_do_not_start_mid_word():
    for doc in load_documents():
        for c in chunk_documents([doc], chunk_size=300, overlap=60):
            pos = doc["text"].find(c["text"])
            assert pos != -1
            assert pos == 0 or doc["text"][pos - 1].isspace(), c["text"][:40]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
