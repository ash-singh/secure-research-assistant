import os
import numpy as np
import argparse
from retrieval import retrieve_chunks  # only for retrieval after build
from embeddings import build_embeddings, model
from config import DATA_DIR, EMBEDDING_DIR, CHUNK_SIZE
from PyPDF2 import PdfReader
import docx

# ---------------------------
# Extract text from PDF
# ---------------------------
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text.strip()

# ---------------------------
# Extract text from DOCX
# ---------------------------
def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

# ---------------------------
# Chunk text into smaller pieces
# ---------------------------
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i+chunk_size]))
    return chunks

# ---------------------------
# Build FAISS index
# ---------------------------
def build_index():
    all_chunks = []
    for filename in os.listdir(DATA_DIR):
        path = os.path.join(DATA_DIR, filename)
        if filename.lower().endswith(".pdf"):
            text = extract_text_from_pdf(path)
        elif filename.lower().endswith(".docx"):
            text = extract_text_from_docx(path)
        else:
            continue
        all_chunks.extend(chunk_text(text, CHUNK_SIZE))

    if not all_chunks:
        raise RuntimeError("No documents found in DATA_DIR!")

    index, embeddings = build_embeddings(all_chunks)
    os.makedirs(EMBEDDING_DIR, exist_ok=True)
    import faiss
    faiss.write_index(index, f"{EMBEDDING_DIR}/document_index.faiss")
    np.save(f"{EMBEDDING_DIR}/chunks_meta.npy",
            [{"text": c, "source": "documents"} for c in all_chunks])
    print(f"FAISS index built with {len(all_chunks)} chunks.")

# ---------------------------
# Command-line interface
# ---------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Document ingestion & FAISS index builder")
    parser.add_argument("--preprocess-all", action="store_true",
                        help="Preprocess all documents in DATA_DIR and rebuild FAISS index")
    args = parser.parse_args()

    if args.preprocess_all:
        build_index()
