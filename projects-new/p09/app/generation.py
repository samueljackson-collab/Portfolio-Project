"""LLM generation module with prompt templating and streaming."""

from typing import List, Dict, AsyncGenerator
import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on the provided context.
Always cite your sources using [1], [2], etc. If the context doesn't contain enough information to answer the question, say so clearly."""


def build_prompt(query: str, contexts: List[Dict]) -> str:
    """Build prompt with retrieved context."""
    context_str = "\n\n".join(
        [
            f"[{i+1}] {ctx['text']}\nSource: {ctx['metadata']['source']}"
            for i, ctx in enumerate(contexts)
        ]
    )

    user_prompt = f"""Context:
{context_str}

Question: {query}

Answer the question based on the context above. Cite sources using [1], [2], etc."""

    return user_prompt


async def generate_response(
    query: str, contexts: List[Dict], temperature: float = 0.7, max_tokens: int = 500
) -> tuple[str, Dict]:
    """Generate response using LLM."""
    user_prompt = build_prompt(query, contexts)

    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    answer = response.choices[0].message.content
    tokens_used = response.usage.total_tokens

    # Compute grounding score
    has_citations = any(f"[{i+1}]" in answer for i in range(len(contexts)))
    grounding_score = 1.0 if has_citations else 0.3

    metadata = {
        "tokens_used": tokens_used,
        "grounding_score": grounding_score,
        "model": "gpt-3.5-turbo",
    }

    return answer, metadata


async def stream_response(
    query: str, contexts: List[Dict], temperature: float = 0.7
) -> AsyncGenerator[str, None]:
    """Stream response chunks using LLM."""
    user_prompt = build_prompt(query, contexts)

    stream = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        stream=True,
    )

    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield f"data: {chunk.choices[0].delta.content}\n\n"
