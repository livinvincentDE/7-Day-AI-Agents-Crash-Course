# data.py
"""
Loads FAQ data from the DataTalksClub/faq GitHub repository.
Falls back to local hardcoded data if the network is unavailable.
"""

import json
import os
from pathlib import Path

# ── GitHub raw content URLs ────────────────────────────────────────────────────
FAQ_GITHUB_BASE = "https://raw.githubusercontent.com/DataTalksClub/faq/main"

# Known FAQ files in the repo (add more as needed)
FAQ_FILES = [
    "docs/01-intro.md",
    "docs/02-workflow.md",
    "docs/03-data-warehouse.md",
    "docs/04-analytics-engineering.md",
    "docs/05-batch.md",
    "docs/06-streaming.md",
    "docs/cohorts.md",
    "docs/homework.md",
    "docs/project.md",
    "docs/slack.md",
]

# ── Fallback data (always available offline) ──────────────────────────────────
FALLBACK_DOCUMENTS = [
    {
        "id": "1",
        "question": "Can I join the course after it starts?",
        "content": "Yes, you can join anytime. The course is self-paced and you can start at any point.",
        "filename": "cohorts.md",
    },
    {
        "id": "2",
        "question": "Is there a deadline to finish the course?",
        "content": "No strict deadline. You can take as long as you need to complete the material.",
        "filename": "cohorts.md",
    },
    {
        "id": "3",
        "question": "Do I need prior experience?",
        "content": "No prior experience is required. The course starts from the basics.",
        "filename": "01-intro.md",
    },
    {
        "id": "4",
        "question": "Is the course free?",
        "content": "Yes, the course is completely free and open to everyone.",
        "filename": "01-intro.md",
    },
    {
        "id": "5",
        "question": "Can I get a certificate?",
        "content": "Yes, certificates are awarded to students who complete all homework and the final project.",
        "filename": "project.md",
    },
    {
        "id": "6",
        "question": "Where can I ask questions?",
        "content": "Join the DataTalksClub Slack workspace. There are dedicated channels for each module.",
        "filename": "slack.md",
    },
    {
        "id": "7",
        "question": "How do I submit homework?",
        "content": "Homework is submitted via Google Forms. Links are posted in Slack and the course repo each week.",
        "filename": "homework.md",
    },
    {
        "id": "8",
        "question": "What tools do I need for the course?",
        "content": "You need Docker, Python 3, and a Google Cloud account. All tools are free or have a free tier.",
        "filename": "01-intro.md",
    },
    {
        "id": "9",
        "question": "Is there a cohort I can join?",
        "content": "Yes, new cohorts start every January. Self-paced learning is available year-round.",
        "filename": "cohorts.md",
    },
    {
        "id": "10",
        "question": "What is the final project about?",
        "content": "The final project involves building an end-to-end data pipeline on a dataset of your choice.",
        "filename": "project.md",
    },
]


# ── Local JSON cache ───────────────────────────────────────────────────────────
CACHE_FILE = Path("faq_cache.json")


def _parse_markdown_faq(text: str, filename: str, id_offset: int) -> list[dict]:
    """
    Parse a simple Q&A markdown file into document dicts.
    Handles headings-as-questions and paragraph-as-answers pattern.
    """
    documents = []
    lines = text.splitlines()
    current_q = None
    current_a_lines = []
    doc_id = id_offset

    for line in lines:
        stripped = line.strip()

        # H2/H3 headings → treat as questions
        if stripped.startswith("## ") or stripped.startswith("### "):
            # Save previous Q&A pair
            if current_q and current_a_lines:
                answer = " ".join(current_a_lines).strip()
                if answer:
                    documents.append({
                        "id": str(doc_id),
                        "question": current_q,
                        "content": answer,
                        "filename": filename,
                    })
                    doc_id += 1

            current_q = stripped.lstrip("#").strip()
            current_a_lines = []

        elif stripped and current_q:
            # Skip markdown formatting lines
            if not stripped.startswith("|") and not stripped.startswith("```"):
                current_a_lines.append(stripped)

    # Flush last pair
    if current_q and current_a_lines:
        answer = " ".join(current_a_lines).strip()
        if answer:
            documents.append({
                "id": str(doc_id),
                "question": current_q,
                "content": answer,
                "filename": filename,
            })

    return documents


def _fetch_from_github() -> list[dict]:
    """Fetch FAQ markdown files from GitHub and parse them."""
    try:
        import urllib.request

        all_docs = []
        id_offset = 1

        for faq_path in FAQ_FILES:
            url = f"{FAQ_GITHUB_BASE}/{faq_path}"
            filename = os.path.basename(faq_path)
            try:
                with urllib.request.urlopen(url, timeout=5) as resp:
                    text = resp.read().decode("utf-8")
                    docs = _parse_markdown_faq(text, filename, id_offset)
                    all_docs.extend(docs)
                    id_offset += len(docs)
            except Exception:
                continue  # Skip files that 404 or timeout

        return all_docs if all_docs else []

    except Exception:
        return []


def load_data(use_cache: bool = True, force_refresh: bool = False) -> list[dict]:
    """
    Load FAQ documents with this priority order:
    1. Local JSON cache (if exists and use_cache=True)
    2. Live fetch from GitHub
    3. Fallback hardcoded data

    Args:
        use_cache:     Read from faq_cache.json if it exists (default: True)
        force_refresh: Re-fetch from GitHub and overwrite cache (default: False)

    Returns:
        List of document dicts with keys: id, question, content, filename
    """

    # ── 1. Try cache ──────────────────────────────────────────────────────────
    if use_cache and not force_refresh and CACHE_FILE.exists():
        try:
            docs = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            if docs:
                print(f"📦 Loaded {len(docs)} FAQ docs from cache ({CACHE_FILE})")
                return docs
        except Exception:
            pass

    # ── 2. Try GitHub ─────────────────────────────────────────────────────────
    print("🌐 Fetching FAQ data from GitHub...")
    github_docs = _fetch_from_github()

    if github_docs:
        print(f"✅ Fetched {len(github_docs)} FAQ docs from GitHub")
        # Save to cache
        try:
            CACHE_FILE.write_text(json.dumps(github_docs, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"💾 Cached to {CACHE_FILE}")
        except Exception:
            pass
        return github_docs

    # ── 3. Fallback ───────────────────────────────────────────────────────────
    print(f"⚠️  GitHub unreachable — using {len(FALLBACK_DOCUMENTS)} fallback FAQ entries")
    return FALLBACK_DOCUMENTS


# ── CLI test ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    docs = load_data(force_refresh=True)
    print(f"\nTotal documents: {len(docs)}\n")
    for d in docs[:5]:
        print(f"[{d['id']}] {d['question']}")
        print(f"     → {d['content'][:80]}...")
        print()
