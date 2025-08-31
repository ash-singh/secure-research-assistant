import requests

from config import LMSTUDIO_API_URL, LLM_MODEL

def query_llm(prompt: str):
    response = requests.post(
        LMSTUDIO_API_URL,
        json={
            "model": LLM_MODEL,
            "messages": prompt,
            "max_tokens": 10000
        },
        timeout=120
    )
    response.raise_for_status()
    response.json()
    lm_data = response.json()
    choice = lm_data["choices"][0]["message"]
    return choice
