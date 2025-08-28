import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

LMSTUDIO_API_URL = os.getenv("LMSTUDIO_API_URL", "http://localhost:5000/generate")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))  # tokens per chunk
TOP_K = int(os.getenv("TOP_K", 5))              # number of chunks to retrieve

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")

DATA_DIR = os.getenv("DATA_DIR", "../data/documents")
EMBEDDING_DIR = os.getenv("EMBEDDING_DIR", "../data/embeddings")


