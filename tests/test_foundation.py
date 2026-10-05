"""Phase 1 smoke test: project layout and config load."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import config

EXPECTED = [
    "app/agents/supervisor.py", "app/agents/rag_agent.py", "app/agents/analytics_agent.py",
    "app/rag/ingestion.py", "app/rag/chunking.py", "app/rag/embeddings.py", "app/rag/retrieval.py",
    "app/data/database.py", "app/data/analytics.py", "app/guardrails/validation.py",
    "app/api/routes.py", "data/documents", "data/synthetic",
    "requirements.txt", ".env.example", ".gitignore", "Dockerfile",
]


def test_layout():
    missing = [p for p in EXPECTED if not (config.ROOT / p).exists()]
    assert not missing, f"missing: {missing}"


def test_config():
    assert config.DOCUMENTS_DIR.exists()
    assert "diagnose" in config.SAFETY_DISCLAIMER


def test_env_not_committed():
    ignore = (config.ROOT / ".gitignore").read_text()
    assert ".env" in ignore.splitlines()


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("PASS", name)
