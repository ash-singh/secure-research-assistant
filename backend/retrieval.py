import logging
import os
import faiss
import numpy as np
from embeddings import get_embedding
from config import EMBEDDING_DIR, TOP_K
from ingest import build_index

# ---------------------------
# Load or build FAISS index
# ---------------------------
index_path = f"{EMBEDDING_DIR}/document_index.faiss"
meta_path = f"{EMBEDDING_DIR}/chunks_meta.npy"

def check_index_exists() -> bool:
    return os.path.exists(index_path) and os.path.exists(meta_path)

if not check_index_exists():
    try:
        logging.info("FAISS index not found. Building index...")
        build_index()
        logging.info("FAISS index built successfully.")
    except RuntimeWarning as e:
        logging.warning(f"Warning building FAISS index: {e}")
    except Exception as e:
        logging.error(f"Error building FAISS index: {e}")

if check_index_exists():
    index = faiss.read_index(index_path)
    chunks_meta = list(np.load(meta_path, allow_pickle=True))
    logging.info(f"FAISS index built and loaded with {len(chunks_meta)} chunks.")


def retrieve_chunks(query, top_k=TOP_K):
    if not check_index_exists():
        return []

    q_emb = get_embedding(query).reshape(1, -1)
    distances, idxs = index.search(q_emb, top_k)

    results = []
    for i in idxs[0]:
        chunk = chunks_meta[i]
        # results.append({
        #     "source": chunk.get("source", f'retrieved_doc_{i + 1}'),
        #     "text": chunk.get("text", "unknown")
        # })
        results.append(chunk)

    return results
