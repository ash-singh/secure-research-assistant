#!/bin/bash
# Launch the backend API

# Activate virtual environment
source ../.venv/bin/activate

# Run Flask backend
uv run ../backend/api.py
