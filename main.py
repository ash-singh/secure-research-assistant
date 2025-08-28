import requests

LMSTUDIO_API_URL = "http://localhost:1234/v1/chat/completions"

def get_answer(prompt):
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 50
    }

    try:
        response = requests.post(LMSTUDIO_API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        print("LM Studio Response:\n", data.get("text", "No text returned"))
    except Exception as e:
        print("Error contacting LM Studio:", e)

def main():
    print("Hello from secure-research-assistant!")

    prompt = "Hello, LM Studio! Can you summarize the following in one sentence: 'Artificial intelligence is transforming the world.'"
    get_answer(prompt)

if __name__ == "__main__":
    main()
