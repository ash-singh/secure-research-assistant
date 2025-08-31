import logging
import os

import faiss
import numpy as np
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from config import LMSTUDIO_API_URL, DATA_DIR, LLM_MODEL, CHUNK_SIZE, EMBEDDING_DIR
from embeddings import build_embeddings
from ingest import chunk_text, extract_text_from_pdf, extract_text_from_docx
from prompt import get_prompt
from retrieval import retrieve_chunks
from utils import extract_text_from_pdf, extract_text_from_docx, chunk_text, allowed_file, extract_sources

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

# ---------------------------
# Ensure directories
# ---------------------------
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EMBEDDING_DIR, exist_ok=True)

@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    user_question = data.get("question")
    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    print(f"Received question: {user_question}")

    # Retrieve context chunks
    context_chunks = retrieve_chunks(user_question)

    # Build context text for LLM
    context_text = "\n\n".join(
        f"[Source: {chunk.get('source', f'retrieved_doc_{i + 1}')}]"
        f"\n{chunk['text']}"
        for i, chunk in enumerate(context_chunks)
    )

    print(f"Context text: {context_text}")

    messages = get_prompt(context_text, user_question)

    logging.info(f"Sending messages to LM Studio: {messages}")
    #print(f"Sending messages to LM Studio: {messages}")

    # Call LM Studio API
    try:
        response = requests.post(
            LMSTUDIO_API_URL,
            json={
                "model": LLM_MODEL,
                "messages": messages,
                "max_tokens": 10000
            },
            timeout=120
        )
        response.raise_for_status()
        lm_data = response.json()

        choice = lm_data["choices"][0]["message"]
        answer = choice.get("content", "")
        reasoning = choice.get("reasoning", "")

        # Extract cited sources
        cited_sources = extract_sources(answer)

        # Fallback: if no valid sources found or LLM used 'unknown', return actual retrieved docs
        if not cited_sources or "unknown" in cited_sources:
            seen = set()
            cited_sources = []
            for chunk in context_chunks:
                doc = chunk['source']
                if doc not in seen:
                    cited_sources.append(doc)
                    seen.add(doc)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    logging.info(f"Received answer: reasoning: sources {answer} {reasoning} {cited_sources}")
    return jsonify({
        "answer": answer,
        "reasoning": reasoning,
        "sources": cited_sources
    })

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return {"error": "No file part"}, 400

    file = request.files["file"]
    if file.filename == "":
        return {"error": "No selected file"}, 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(DATA_DIR, exist_ok=True)
        file_path = os.path.join(DATA_DIR, filename)
        file.save(file_path)

        # Extract text
        if filename.lower().endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif filename.lower().endswith(".docx"):
            text = extract_text_from_docx(file_path)
        else:
            return {"error": "Unsupported file type"}, 400

        # Chunk text
        chunks = chunk_text(text, CHUNK_SIZE)
        if not chunks:
            return {"error": "No text extracted from file"}, 400

        # Save chunks metadata
        os.makedirs(EMBEDDING_DIR, exist_ok=True)
        chunks_meta_path = os.path.join(EMBEDDING_DIR, "chunks_meta.npy")
        existing_chunks = []
        if os.path.exists(chunks_meta_path):
            existing_chunks = list(np.load(chunks_meta_path, allow_pickle=True))
        # Append new chunks
        all_chunks_meta = existing_chunks + [{"text": c, "source": filename} for c in chunks]
        np.save(chunks_meta_path, all_chunks_meta)

        # Rebuild FAISS index
        all_texts = [c["text"] for c in all_chunks_meta]
        index, _ = build_embeddings(all_texts)
        faiss.write_index(index, os.path.join(EMBEDDING_DIR, "document_index.faiss"))

        return {"message": f"File '{filename}' uploaded and index updated successfully.", "chunks_added": len(chunks)}

    return {"error": "File type not allowed"}, 400


if __name__ == "__main__":
    app.run(port=8000)
