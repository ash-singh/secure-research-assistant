from sentence_transformers import SentenceTransformer

# Load your embedding model once
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # light weight
model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# Build FAISS index from chunks
def build_embeddings(chunks, embedding_model_name=EMBEDDING_MODEL_NAME):
    vectors = model.encode(chunks, convert_to_numpy=True, embedding_model_name=embedding_model_name)
    dim = vectors.shape[1]
    import faiss
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    return index, vectors

# Get embedding for a single query
def get_embedding(text, embedding_model_name=EMBEDDING_MODEL_NAME):
    vec = model.encode([text], convert_to_numpy=True, embedding_model_name=embedding_model_name)
    return vec[0]
