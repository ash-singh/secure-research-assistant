#!/bin/bash
# Optional batch preprocessing of documents

# Activate virtual environment
source ../.venv/bin/activate

# Run preprocessing script in backend
python ../backend/ingest.py --preprocess-all
