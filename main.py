import asyncio
import os
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# 1. Load environment variables FIRST
# ─────────────────────────────────────────────
load_dotenv(override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY is not set. Please add it to your .env file."
    )

print(f"✅ GROQ_API_KEY loaded: {GROQ_API_KEY[:15]}...")

# ─────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.providers.groq import GroqProvider

from search import hybrid_search, text_search, vector_search


# ─────────────────────────────────────────────
# 2. Build Groq model
# ─────────────────────────────────────────────
groq_provider = GroqProvider(api_key=GROQ_API_KEY)

model = GroqModel(
    "llama-3.3-70b-versatile",
    provider=groq_provider
)

print("✅ GroqModel initialized successfully")


# ─────────────────────────────────────────────
# 3. System prompt with citation instructions
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """
You are a helpful FAQ assistant for an online course platform.

Use ONLY the provided context to answer the question.
Always include references by citing the source material when possible.
Use Markdown format: [Question Title](https://github.com/DataTalksClub/faq/blob/main/[filename])

If the context does not contain enough information, reply exactly with:
"I'm sorry, I don't have enough information to answer that question."

Be concise, friendly, and accurate.
"""


# ─────────────────────────────────────────────
# 4. Build the Agent
# ─────────────────────────────────────────────
agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
)

# Setup question generator for data generation
from data_generation import setup_question_generator
setup_question_generator(model)

# Create judge agent (for LLM as a Judge)
from evaluation import create_judge_agent
create_judge_agent(model)


# ─────────────────────────────────────────────
# 5. Build context for RAG
# ─────────────────────────────────────────────
def build_context(query: str, search_mode: str = "hybrid") -> str:
    if search_mode == "text":
        results = text_search(query)
    elif search_mode == "vector":
        results = vector_search(query)
    else:
        results = hybrid_search(query)

    if not results:
        return "No relevant documents found."

    context_parts = []
    for i, doc in enumerate(results, start=1):
        q = doc.get("question", "N/A")
        content = doc.get("content", "N/A")
        context_parts.append(f"[{i}] Q: {q}\n    A: {content}")

    return "\n\n".join(context_parts)


# ─────────────────────────────────────────────
# 6. Answer function
# ─────────────────────────────────────────────
async def answer_question(query: str, search_mode: str = "hybrid") -> str:
    context = build_context(query, search_mode)

    full_prompt = f"""Context:
{context}

Question: {query}
"""

    try:
        result = await agent.run(full_prompt)
        return result.output
    except Exception as e:
        error_str = str(e).lower()
        if "401" in error_str or "invalid api key" in error_str:
            return "❌ Authentication error with Groq. Check your API key."
        return f"❌ Error generating answer: {e}"


# ─────────────────────────────────────────────
# 7. Interactive CLI with Logging
# ─────────────────────────────────────────────
async def interactive_loop():
    print("\n📚 Course FAQ Agent (Llama-3.3-70B on Groq)")
    print("Type 'quit', 'exit', or 'q' to stop.\n")

    from evaluation import log_interaction_to_file

    while True:
        query = input("You: ").strip()
        if query.lower() in {"quit", "exit", "q"}:
            print("👋 Goodbye!")
            break
        if not query:
            continue

        print("Thinking...")
        try:
            context = build_context(query)
            full_prompt = f"""Context:
{context}

Question: {query}
"""

            result = await agent.run(full_prompt)
            answer = result.output
            print(f"\nAgent: {answer}\n")

            # === LOGGING ===
            try:
                messages_to_log = result.all_messages()
                log_path = log_interaction_to_file(agent, messages_to_log, source="user")
                
                if log_path:
                    print(f"✅ Interaction logged successfully! → {log_path.name}")
                else:
                    print("⚠️  Log file was not created.")
            except Exception as log_err:
                print(f"⚠️  Logging failed: {log_err}")

        except Exception as e:
            print(f"\n[Agent Error] {e}")
            import traceback
            traceback.print_exc()


# ─────────────────────────────────────────────
# 8. Run the app
# ─────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(interactive_loop())