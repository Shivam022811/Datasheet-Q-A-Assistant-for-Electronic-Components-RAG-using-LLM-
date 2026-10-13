import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "datasheets"
DB_DIR = ROOT / "chroma_db"
COLLECTION = "datasheets"

# Embedding model (runs locally, downloaded on first use)
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Chunking
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

# Retrieval
TOP_K = 6               # chunks when no specific component is named
TOP_K_PER_COMPONENT = 4  # chunks per component when components are named

# LLM (change in .env if you want a different model)
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-5-5")
