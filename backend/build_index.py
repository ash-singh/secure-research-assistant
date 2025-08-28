import os
import numpy as np
from utils import extract_text_from_pdf, extract_text_from_docx, chunk_text
from embeddings import build_embeddings
from config import DATA_DIR, EMBEDDING_DIR

chunks_list = []

for filename in os.listdir(DATA_DIR):
    path = os.path.join(DATA_DIR, filename)
    if filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(path)
    elif filename.lower().endswith(".docx"):
        text = extract_text_from_docx(path)
    else:
        continue
    chunks_list.extend(chunk_text(text))

if not chunks_list:
    print("No document chunks found. Add PDFs or DOCX to data/documents/")
    exit()

# Build FAISS index
index, _ = build_embeddings(chunks_list)

# Save chunks metadata for retrieval
import numpy as np
chunks_meta = [{"text": chunk, "source": "uploaded_docs"} for chunk in chunks_list]
np.save(f"{EMBEDDING_DIR}/chunks_meta.npy", chunks_meta)

print(f"FAISS index built with {len(chunks_list)} chunks.")
