"""
search_agent.py
Creates and configures the Pydantic AI agent.
Nothing runs at import time — call init_agent() explicitly.
"""

import os
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider

import search_tools


# ── System prompt template ─────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are a helpful FAQ assistant for an online course platform.

Use ONLY the provided context to answer the question.
Always include references by citing the source material when possible.
Use Markdown format: [Question Title](https://github.com/DataTalksClub/faq/blob/main/[filename])

If the context does not contain enough information, reply exactly with:
"I'm sorry, I don't have enough information to answer that question."

Be concise, friendly, and accurate.
"""


def build_groq_model(api_key: str | None = None) -> GroqModel:
    """
    Build and return a GroqModel.
    Uses GROQ_API_KEY env var if api_key is not provided explicitly.
    """
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. Add it to your .env file or pass it explicitly."
        )
    provider = GroqProvider(api_key=key)
    return GroqModel("llama-3.3-70b-versatile", provider=provider)


def build_context(query: str, search_mode: str = "hybrid") -> str:
    """
    Build a RAG context string from search results.
    Extracted here so both main.py and app.py can call it without importing main.
    """
    tool = search_tools.SearchTool()

    if search_mode == "text":
        results = tool.text_only_search(query)
    elif search_mode == "vector":
        results = tool.vector_only_search(query)
    else:
        results = tool.search(query)

    if not results:
        return "No relevant documents found."

    parts = []
    for i, doc in enumerate(results, start=1):
        q = doc.get("question", "N/A")
        content = doc.get("content", "N/A")
        parts.append(f"[{i}] Q: {q}\n    A: {content}")

    return "\n\n".join(parts)


def init_agent(api_key: str | None = None) -> Agent:
    """
    Create and return a configured Pydantic AI agent.
    Call this once per process (or once per Streamlit session via @st.cache_resource).

    Args:
        api_key: Optional Groq API key. Falls back to GROQ_API_KEY env var.

    Returns:
        A ready-to-use Pydantic AI Agent.
    """
    model = build_groq_model(api_key)

    agent = Agent(
        name="faq_agent",
        model=model,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent
