import os
import logging
import faiss
from config import EMBEDDING_DIR, TOP_K
from embeddings import get_embedding
from db import get_all_chunks

index_path = f"{EMBEDDING_DIR}/document_index.faiss"


def check_index_exists() -> bool:
    return os.path.exists(index_path)


def load_index():
    if not check_index_exists():
        return None
    return faiss.read_index(index_path)


def retrieve_chunks(query: str, top_k: int = TOP_K):
    """
    Search FAISS index for the most relevant chunks.
    Returns a list of dicts: {text, source, score}.
    """
    if not check_index_exists():
        logging.warning("No FAISS index found.")
        return []

    index = load_index()
    if index is None:
        return []

    # Encode query → vector
    q_emb = get_embedding(query).reshape(1, -1).astype("float32")

    # FAISS search
    distances, idxs = index.search(q_emb, top_k)

    # Load all chunks from DB
    chunks = get_all_chunks()

    results = []
    for dist, idx in zip(distances[0], idxs[0]):
        if idx < 0 or idx >= len(chunks):
            continue
        results.append({
            "text": chunks[idx]["text"],
            "source": chunks[idx]["source"],
            "score": float(dist)  # smaller = closer match
        })

    return results
