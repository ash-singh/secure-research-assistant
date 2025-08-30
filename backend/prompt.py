
def get_prompt(context_text, user_question, extra_rules=None):
    system_content = """You are a helpful research assistant.
Rules:
1. Only use information provided in the context.
2. Always cite the source using [Source: filename].
3. If the answer is not in the context, say "I don’t know" instead of making up information.
4. Never invent or hallucinate information.
"""
    if extra_rules:
        system_content += "\n" + extra_rules

    prompt = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": f"""
Use the following context to answer the question.

Context:
{context_text}

Question:
{user_question}
"""}
    ]
    return prompt

