# Secure Research Assistant

Secure offline research assistant leveraging a 20B LLM and retrieval-augmented generation (RAG) for local document search and question answering.

---

## 1. Core Components

### A. LLM Backend 
https://lmstudio.ai/
- **Model:** 20B LLM running in LM Studio  
- **Role:** Handles text generation, summarization, and Q&A  
- **Access:** Exposes a local API endpoint for frontend communication  

### B. Document Storage
- **Storage:** Store PDFs, Word docs, and text files locally  
- **Preprocessing:**  
  - Split documents into chunks (500–1000 tokens each)  
  - Remove irrelevant formatting for cleaner embeddings  

### C. Embeddings & Vector Database
- **Embeddings:** Open-source embedding model (e.g., `sentence-transformers`) to vectorize document chunks  
- **Vector DB Options:**  
  - FAISS (lightweight, local)  
  - Milvus (advanced, heavier)  
- **Role:** Fast retrieval of relevant chunks to feed the model contextually  

### D. Retrieval-Augmented Generation (RAG)
**Workflow:**
1. User asks a question  
2. Query vector DB → retrieve top-K relevant chunks  
3. Construct a prompt with context + user question  
4. Send to LM Studio for answer generation  

**Benefit:** Allows a 20B model to answer long-document questions without exceeding the context window  

### E. Frontend / UI
- **Framework**: Streamlit (offline, Python-based)
- **Features:**  
  - Upload documents (PDF, DOCX, TXT)
  - Search & query interface
  - Display answers with reference snippets
  - Optional toggle to allow fallback to LLM knowledge if context is insufficient
  - Show total response time for each query
  - Notebook/history for past queries 

```scss
       ┌───────────────┐
       │   User (You)  │
       └───────┬───────┘
               │
               ▼
      ┌─────────────────┐
      │ Streamlit UI     │
      │ - Upload docs    │
      │ - Ask questions  │
      │ - View answers   │
      │ - Response time  │
      └───────┬─────────┘
              │
              ▼
     ┌─────────────────────┐
     │ Local Backend API    │
     │ - /docs              │
     │ - /ask               │
     │ - Manage FAISS index │
     └───────┬─────────────┘
             │
             ▼
    ┌───────────────────────┐
    │ FAISS Vector DB        │
    │ - Embeddings via       │
    │   all-MiniLM-L6-v2    │
    │ - Retrieve top-K chunks│
    └───────┬───────────────┘
             │
             ▼
    ┌───────────────────────┐
    │ LM Studio 20B LLM     │
    │ - Receives prompt:    │
    │   "Question + Context"│
    │ - Generates answer     │
    │ - Optionally fallback │
    │   to own knowledge    │
    └──────────────┬────────┘
                   │
                   ▼
          ┌────────────────┐
          │ Answer + Sources│
          │ + Response Time │
          └────────────────┘
                   │
                   ▼
            Streamlit UI displays


```
---

## Setup Instructions

## 1: Set Up LM Studio
1. Run your 20B model locally and expose a local API  
2. Download LM Studio and load your 20B model  
3. Enable the API server (LM Studio supports a local REST endpoint)  

---

### 2: Clone the repository
```bash
git clone <your-repo-url>
cd secure-research-assistant
````
```scss
secure-research-assistant/
│
├── backend/
│   ├── api.py
│   ├── ingest.py
│   ├── embeddings.py
│   ├── retrieval.py
│   ├── config.py
│   └── utils.py
│
├── frontend/
│   └── chat.py          # Streamlit UI
│
├── models/
│   └── 20B_model/       # LM Studio model directory
│
├── data/
│   ├── documents/       # Uploaded documents
│   └── embeddings/      # FAISS index files
│
├── scripts/
│   ├── start_backend.sh
│   └── preprocess_docs.sh
│
├── README.md
└── requirements.txt


```
### 3. Create virtual environment & install dependencies

```bash
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp config.example.env .env
```

Update `.env` with your local settings:

```env
LMSTUDIO_API_URL=http://127.0.0.1:1234/v1/chat/completions
LLM_MODEL=openai/gpt-oss-20b
CHUNK_SIZE=500
TOP_K=5
EMBEDDING_MODEL=all-MiniLM-L6-v2
DATA_DIR=data/documents
EMBEDDING_DIR=data/embeddings
```

### 5. Run the backend server

```bash
uv run backend/api.py
```

**Optional:** Run with Gunicorn for production:

```bash
gunicorn -w 4 backend.api:app
```

---

## Launch Streamlit Frontend


```bash
streamlit run frontend/chat.py
```
