server:
	uv run backend/app.py

chat:
	streamlit run frontend/chat.py

start:
	uv run backend/app.py & streamlit run frontend/chat.py
