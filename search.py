# search.py

from minsearch import Index
from data import load_data
from sentence_transformers import SentenceTransformer
import numpy as np

# Step 1: Load data
documents = load_data()

# Step 2: Create text index
text_index = Index(
    text_fields=["question", "content"],
    keyword_fields=[]
)
text_index.fit(documents)

# Step 3: Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Step 4: Create embeddings
doc_embeddings = np.array([
    model.encode(doc["question"] + " " + doc["content"])
    for doc in documents
])


# 🔍 TEXT SEARCH
def text_search(query: str) -> list:
    return text_index.search(query, num_results=3)


# 🧠 VECTOR SEARCH
def vector_search(query: str) -> list:
    q_emb = model.encode(query)
    scores = doc_embeddings.dot(q_emb)
    top_idx = np.argsort(scores)[-3:][::-1]
    return [documents[i] for i in top_idx]


# 🔄 HYBRID SEARCH
def hybrid_search(query: str) -> list:
    text_results = text_search(query)
    vector_results = vector_search(query)

    seen = set()
    combined = []

    for r in text_results + vector_results:
        key = r.get("id") or hash(r["question"])
        if key not in seen:
            seen.add(key)
            combined.append(r)

    return combined


# ─────────────────────────────────────────────
# 📊 SEARCH QUALITY EVALUATION (Hit Rate + MRR)
# ─────────────────────────────────────────────
def evaluate_search_quality(search_function, test_queries: list) -> dict:
    """
    Evaluate search function using Hit Rate and MRR.

    Args:
        search_function : one of text_search, vector_search, hybrid_search
        test_queries    : list of (query_str, expected_ids_set)
                          e.g. [("Can I join late?", {"1"}), ...]

    Returns:
        dict with hit_rate, mrr, and per-query details list
    """
    results = []

    for query, expected_ids in test_queries:
        # ✅ Fix 1 — no num_results arg (functions only accept query)
        search_results = search_function(query)

        # ✅ Fix 2 — use "id" field (matches data.py schema, not "filename")
        relevant_found = any(
            doc.get("id") in expected_ids for doc in search_results
        )

        mrr = 0
        for i, doc in enumerate(search_results):
            if doc.get("id") in expected_ids:
                mrr = 1 / (i + 1)
                break

        results.append({
            "query": query,
            "hit":   relevant_found,
            "mrr":   mrr
        })

    # ✅ Fix 3 — return results (not returnresults)
    hit_rate = sum(r["hit"] for r in results) / len(results) if results else 0
    mean_mrr = sum(r["mrr"] for r in results) / len(results) if results else 0

    print("\n" + "=" * 45)
    print("🔍  SEARCH QUALITY METRICS")
    print("=" * 45)
    print(f"  Hit Rate : {hit_rate:.2%}")
    print(f"  MRR      : {mean_mrr:.4f}")
    print("=" * 45)

    return {
        "hit_rate": hit_rate,
        "mrr":      mean_mrr,
        "details":  results
    }


# ─────────────────────────────────────────────
# ▶️ MAIN EXECUTION
# ─────────────────────────────────────────────
if __name__ == "__main__":
    query = "Can I enroll in the course?"

    print("\n🔍 TEXT SEARCH:\n")
    for r in text_search(query):
        print(f"{r['question']} -> {r['content']}")

    print("\n🧠 VECTOR SEARCH:\n")
    for r in vector_search(query):
        print(f"{r['question']} -> {r['content']}")

    print("\n🔄 HYBRID SEARCH:\n")
    for r in hybrid_search(query):
        print(f"{r['question']} -> {r['content']}")

    # ── Evaluate all 3 search modes ──────────────
    print("\n\n📊 EVALUATING SEARCH QUALITY...\n")

    # Test queries matched to your data.py ids: "1", "2", "3"
    test_queries = [
        ("Can I join after the course starts?", {"1"}),
        ("Is there a deadline to finish?",      {"2"}),
        ("Do I need prior experience?",         {"3"}),
    ]

    print("▶ Text Search:")
    evaluate_search_quality(text_search, test_queries)

    print("\n▶ Vector Search:")
    evaluate_search_quality(vector_search, test_queries)

    print("\n▶ Hybrid Search:")
    evaluate_search_quality(hybrid_search, test_queries)