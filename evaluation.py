import json
import secrets
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel
from pydantic_ai import Agent

# ========================= CONFIG =========================
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# ========================= EVALUATION SCHEMA =========================
class EvaluationCheck(BaseModel):
    check_name: str
    justification: str
    check_pass: bool


class EvaluationChecklist(BaseModel):
    checklist: list[EvaluationCheck]
    summary: str


# ========================= LOGGING =========================
def log_entry(agent, messages, source="user"):
    tools = []
    try:
        for ts in getattr(agent, 'toolsets', []):
            if hasattr(ts, 'tools'):
                tools.extend(ts.tools.keys())
    except:
        pass

    system_prompt = getattr(agent, 'instructions', None) or \
                    getattr(agent, 'system_prompt', None) or \
                    "No system prompt found"

    return {
        "agent_name": getattr(agent, 'name', 'faq_agent'),
        "system_prompt": system_prompt,
        "model": getattr(getattr(agent, 'model', None), 'model_name', 'unknown'),
        "tools": tools,
        "messages": messages,
        "source": source
    }


def log_interaction_to_file(agent, messages, source="user"):
    try:
        entry = log_entry(agent, messages, source)

        ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        rand_hex = secrets.token_hex(3)
        filename = f"{getattr(agent, 'name', 'agent')}_{ts_str}_{rand_hex}.json"
        filepath = LOG_DIR / filename

        with filepath.open("w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2, default=str)

        return filepath
    except Exception as e:
        print(f"❌ Log write failed: {e}")
        return None


# ========================= LLM AS A JUDGE =========================
evaluation_prompt = """
You are a strict but fair evaluator for a course FAQ agent.

<INSTRUCTIONS>
{instructions}
</INSTRUCTIONS>

<QUESTION>
{question}
</QUESTION>

<ANSWER>
{answer}
</ANSWER>

Evaluate the answer using this checklist:

1. instructions_follow: Did the agent follow the system instructions? (especially about using context and citing references)
2. answer_relevant: Does the answer directly address the user's question?
3. answer_clear: Is the answer clear, polite, and easy to understand?
4. answer_citations: Does the answer include proper Markdown references/links?
5. completeness: Is the answer complete?
6. no_hallucination: Does the answer stick to the provided context only?

For each check, provide short justification and true/false.
"""

judge_agent = None


def create_judge_agent(model):
    """Create the judge agent - call this from main.py"""
    global judge_agent
    judge_agent = Agent(
        model=model,
        instructions=evaluation_prompt,
        output_type=EvaluationChecklist
    )
    print("✅ Judge agent created successfully")
    return judge_agent


# ========================= UTILITY =========================
def load_log_file(log_file: Path):
    with open(log_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        data['log_file'] = str(log_file.name)
        return data


async def evaluate_log_record(log_record):
    global judge_agent
    if judge_agent is None:
        print("❌ Judge agent not initialized")
        return None

    try:
        messages = log_record.get("messages", [])
        question = str(messages[0]) if messages else "No question"
        answer = str(messages[-1]) if messages else "No answer"

        user_prompt = evaluation_prompt.format(
            instructions=log_record.get("system_prompt", ""),
            question=question[:800],
            answer=answer[:1200]
        )

        result = await judge_agent.run(user_prompt)
        return result.output

    except Exception as e:
        print(f"Judge error: {e}")
        return None


def list_logs():
    logs = sorted(LOG_DIR.glob("*.json"), reverse=True)
    print(f"📁 Found {len(logs)} log files:\n")
    for i, log in enumerate(logs[:10], 1):
        print(f"{i:2d}. {log.name}")
    return logs