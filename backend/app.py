import logging
import os

import faiss
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import DATA_DIR, CHUNK_SIZE, EMBEDDING_DIR
from db import init_db, add_doc, remove_doc, list_docs, reset_db, get_all_chunks
from embeddings import build_embeddings
from llm import query_llm
from prompt import get_prompt
from retrieval import retrieve_chunks
from utils import (
    extract_text_from_pdf,
    extract_text_from_docx,
    chunk_text,
    allowed_file,
    extract_sources,
)

logging.basicConfig(level=logging.INFO)
logging.info("🔍 Logging configured and working!")

# ---------------------------
# Flask app
# ---------------------------
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EMBEDDING_DIR, exist_ok=True)

init_db()

INDEX_PATH = os.path.join(EMBEDDING_DIR, "document_index.faiss")


# ---------------------------
# Helpers
# ---------------------------
def rebuild_index():
    """Rebuild FAISS index from all chunks in DB."""
    chunks = get_all_chunks()
    if not chunks:
        if os.path.exists(INDEX_PATH):
            os.remove(INDEX_PATH)
        return None

    texts = [c["text"] for c in chunks]
    index, _ = build_embeddings(texts)
    faiss.write_index(index, INDEX_PATH)
    return index


# ---------------------------
# Routes
# ---------------------------
@app.route("/ask", methods=["GET", "POST"])
def ask():
    allow_fallback = False
    # Support GET (for Streamlit) or POST (future API clients)
    if request.method == "POST":
        data = request.get_json()
        user_question = data.get("question")
        allow_fallback = data.get("allow_fallback", False)
    else:
        user_question = request.args.get("q")

    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    logging.info(f"Received question: {user_question} allow_fallback: {allow_fallback} ")

    try:
        # Retrieve context chunks
        context_chunks = retrieve_chunks(user_question)

        # Build context text for LLM
        context_text = "\n\n".join(
            f"[Source: {chunk.get('source', f'retrieved_doc_{i + 1}')}]"
            f"\n{chunk['text']}"
            for i, chunk in enumerate(context_chunks)
        )

        # Build prompt
        prompt = get_prompt(context_text, user_question, allow_fallback=allow_fallback)

        # Query local LLM
        choice = query_llm(prompt)
        answer = choice.get("content", "")
        reasoning = choice.get("reasoning", "")

        # Extract cited sources from LLM answer
        cited_sources = extract_sources(answer)

        # Fallback: include actual retrieved docs
        if not cited_sources or "unknown" in cited_sources:
            seen = set()
            cited_sources = []
            for chunk in context_chunks:
                doc = chunk["source"]
                if doc not in seen:
                    cited_sources.append(doc)
                    seen.add(doc)

        # Format sources for frontend
        sources_formatted = []
        for doc in cited_sources:
            snippet = ""
            confidence = 1.0  # For MVP, set 1.0 or calculate similarity later
            for chunk in context_chunks:
                if chunk["source"] == doc:
                    snippet = chunk["text"][:300]  # short preview
                    break
            sources_formatted.append(
                {"doc": doc, "snippet": snippet, "confidence": confidence}
            )

    except Exception as e:
        logging.error(f"Query error: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "question": user_question,
        "answer": answer,
        "reasoning": reasoning,
        "sources": sources_formatted
    })


@app.route("/docs", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "No text extracted from file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(DATA_DIR, filename)
    file.save(file_path)

    # Extract text
    if filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif filename.lower().endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        return jsonify({"error": "Unsupported file type"}), 400

    # Chunk text
    chunks = list(chunk_text(text, CHUNK_SIZE))
    if not chunks:
        return jsonify({"error": "No text extracted from file"}), 400

    # Save to DB
    add_doc(filename, chunks)

    # Rebuild index
    rebuild_index()

    message = f"File '{filename}' uploaded and index updated successfully."
    logging.info(message)
    print(message)
    return jsonify({
        "message": message,
        "chunks_added": len(chunks),
    })


@app.route("/docs", methods=["GET"])
def list_all():
    docs = list_docs()
    return jsonify(docs)


@app.route("/docs/<filename>", methods=["DELETE"])
def remove(filename):
    remove_doc(filename)
    rebuild_index()
    return jsonify({"message": f"File '{filename}' removed and index rebuilt."}), 200


@app.route("/docs/reset", methods=["POST"])
def reset():
    reset_db()
    # Clear files
    for f in os.listdir(DATA_DIR):
        path = os.path.join(DATA_DIR, f)
        if os.path.isfile(path):
            os.remove(path)
    # Rebuild an empty index
    rebuild_index()

    return jsonify({"message": "All docs, chunks, and index reset."}), 200


if __name__ == "__main__":
    app.run(port=8000, debug=True)
