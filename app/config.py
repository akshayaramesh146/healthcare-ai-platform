"""Central configuration, loaded from environment variables / .env."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # python-dotenv is optional for a bare smoke test
    pass

ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = ROOT / "data" / "documents"
SYNTHETIC_DIR = ROOT / "data" / "synthetic"

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
VECTOR_STORE_PATH = ROOT / os.getenv("VECTOR_STORE_PATH", "vector_store")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{SYNTHETIC_DIR / 'healthcare.db'}")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

SAFETY_DISCLAIMER = (
    "This assistant provides general educational information only. It cannot "
    "diagnose conditions or recommend personal treatment or medication. Please "
    "consult a qualified healthcare professional for personal medical decisions."
)
