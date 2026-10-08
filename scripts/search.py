"""Try retrieval from the command line. Run from project root:
python scripts/search.py "What are the risk factors for hypertension?"
python scripts/search.py "symptoms" --topic diabetes
Add --hash if you built the index with --hash."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.retrieval import load_retriever

p = argparse.ArgumentParser()
p.add_argument("query")
p.add_argument("--topic")
p.add_argument("--k", type=int, default=3)
p.add_argument("--hash", action="store_true")
a = p.parse_args()

store = load_retriever("hash" if a.hash else "sentence-transformer")
for r in store.search(a.query, k=a.k, topic=a.topic):
    print(f"\n[{r['score']:.3f}] {r['source']} (page {r['page']}, topic: {r['topic']})")
    print(r["text"][:300] + ("..." if len(r["text"]) > 300 else ""))
