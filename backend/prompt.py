import tiktoken
from config import LLM_MODEL, LLM_MODEL_MAX_TOKENS


def get_prompt(user_question, context_text, allow_fallback=False, extra_rules=None):
    system_content = """You are a helpful research assistant.
Rules:
1. Use the provided context as the primary source for answers.
2. If the answer is in the context, always cite the source using [Source: filename].
3. If the answer is not in the context:
   - If fallback is allowed, answer from your own knowledge BUT clearly state: 
     "⚠️ This part of the answer is not based on the provided context."
   - If fallback is not allowed, reply: "I don’t know."
4. Never mix hallucinated information with contextual information.
"""
    if extra_rules:
        system_content += "\n" + extra_rules

    user_content = f"""
Question:
{user_question}

Context:
{context_text if context_text.strip() else "No context was provided."}
"""

    if allow_fallback:
        user_content += "\n\nRemember: if the context does not contain the answer, you may use your own knowledge but clearly mark it as ⚠️ not from context."

    prompt = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content.strip()}
    ]
    return prompt


def truncate_context(chunks, user_question, max_tokens=LLM_MODEL_MAX_TOKENS, model=LLM_MODEL):
    """
    Truncate context to fit within max_tokens.
    Always keeps the user_question fully.
    """
    enc = tiktoken.encoding_for_model(model)

    # Start budget with question
    q_tokens = len(enc.encode(user_question))
    budget = max_tokens - q_tokens - 200  # keep 200 tokens for system + safety margin

    context_texts = []
    used_tokens = 0

    for chunk in chunks:
        text = chunk["text"]
        tokens = len(enc.encode(text))
        if used_tokens + tokens <= budget:
            context_texts.append(
                f"[Source: {chunk.get('source', 'unknown')}] {text}"
            )
            used_tokens += tokens
        else:
            break

    return "\n\n".join(context_texts)