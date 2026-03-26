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
        # Fallback to content hash if no 'id' field exists
        key = r.get("id") or hash(r["question"])
        if key not in seen:
            seen.add(key)
            combined.append(r)

    return combined


# ▶️ MAIN EXECUTION
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