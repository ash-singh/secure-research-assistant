FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y build-essential git wget curl && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install --no-cache-dir uv

COPY . .

# Install dependencies using uv
RUN uv sync

# Also install additional packages explicitly
RUN pip install --no-cache-dir streamlit sentence-transformers faiss-cpu requests

EXPOSE 8000 8501

CMD ["sh", "-c", "uv run backend/app.py & python3 -m streamlit run frontend/chat.py --server.port ${STREAMLIT_PORT:-8501} --server.address 0.0.0.0"]

