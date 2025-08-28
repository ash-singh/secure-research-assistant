import faiss
import numpy as np
from embeddings import get_embedding
from config import EMBEDDING_DIR, TOP_K

# Load FAISS index and metadata
index = faiss.read_index(f"{EMBEDDING_DIR}/document_index.faiss")
chunks_meta = np.load(f"{EMBEDDING_DIR}/chunks_meta.npy", allow_pickle=True)
# Each element: {"text": chunk_text, "source": filename}

def retrieve_chunks(query, top_k=TOP_K):
    q_emb = get_embedding(query).reshape(1, -1)
    distances, idxs = index.search(q_emb, top_k)
    return [chunks_meta[i]["text"] for i in idxs[0]]
