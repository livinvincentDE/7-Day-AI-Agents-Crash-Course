"""
logs.py
Handles logging of agent interactions to JSON files.
No globals, no side effects on import.
"""

import json
import os
import secrets
from datetime import datetime
from pathlib import Path


# ── Log directory — configurable via env var for deployment ───────────────────
LOG_DIR = Path(os.getenv("LOGS_DIRECTORY", "logs"))
LOG_DIR.mkdir(exist_ok=True)


# ── Internal helpers ───────────────────────────────────────────────────────────
def _serializer(obj):
    """JSON serializer for objects not serializable by default."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)   # graceful fallback for any other type


def _build_log_entry(agent, messages, source: str = "user") -> dict:
    """Construct the log dict from an agent and its messages."""
    system_prompt = (
        getattr(agent, "instructions", None)
        or getattr(agent, "system_prompt", None)
        or "No system prompt"
    )

    tools = []
    for ts in getattr(agent, "toolsets", []):
        if hasattr(ts, "tools"):
            tools.extend(ts.tools.keys())

    return {
        "agent_name": getattr(agent, "name", "faq_agent"),
        "system_prompt": system_prompt,
        "model": getattr(getattr(agent, "model", None), "model_name", "unknown"),
        "tools": tools,
        "messages": messages,
        "source": source,
        "logged_at": datetime.now().isoformat(),
    }


# ── Public API ─────────────────────────────────────────────────────────────────
def log_interaction_to_file(agent, messages, source: str = "user") -> Path | None:
    """
    Serialize an agent interaction to a timestamped JSON file in LOG_DIR.

    Args:
        agent:    The Pydantic AI agent that ran the interaction.
        messages: The list returned by result.all_messages().
        source:   Tag to identify the log origin ("user", "ai-generated", etc.).

    Returns:
        Path to the written file, or None if logging failed.
    """
    try:
        entry = _build_log_entry(agent, messages, source)

        ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        rand_hex = secrets.token_hex(3)
        agent_name = getattr(agent, "name", "agent")
        filename = f"{agent_name}_{ts_str}_{rand_hex}.json"
        filepath = LOG_DIR / filename

        with filepath.open("w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2, default=_serializer)

        return filepath

    except Exception as exc:
        print(f"⚠️  Logging failed: {exc}")
        return None


def list_logs(limit: int = 20) -> list[Path]:
    """Return the latest log files, newest first."""
    return sorted(LOG_DIR.glob("*.json"), reverse=True)[:limit]


def load_log_file(log_file: Path) -> dict:
    """Load and return a single log file as a dict."""
    with open(log_file, encoding="utf-8") as f:
        data = json.load(f)
    data["log_file"] = log_file.name
    return data
