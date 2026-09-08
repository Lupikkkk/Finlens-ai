import os
import pickle
from pathlib import Path
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import anthropic

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = PROJECT_ROOT / "data" / "processed" / "nike_faiss.index"
METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "nike_chunks_metadata.pkl"

index = faiss.read_index(str(INDEX_PATH))
with open(METADATA_PATH, "rb") as f:
    chunks = pickle.load(f)

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def retrieve(query: str, k: int = 5):
    query_embedding = embed_model.encode([query]).astype("float32")
    distances, indices = index.search(query_embedding, k)
    return [chunks[idx] for idx in indices[0]]


def explain_change(metric_name: str, prev_value: str, latest_value: str, change_description: str):
    # Build a retrieval query from the metric name and change direction
    query = f"reasons for {metric_name} change: {change_description}"
    retrieved_chunks = retrieve(query, k=5)

    # Build the context block from retrieved chunks, each labeled for citation
    context_blocks = []
    for chunk in retrieved_chunks:
        context_blocks.append(f"[{chunk['chunk_id']}] {chunk['text']}")
    context = "\n\n".join(context_blocks)

    prompt = f"""You are a financial analyst. Explain the identified financial change using ONLY the provided SEC filing excerpts below. Do not use outside knowledge or invent reasons.

Financial change:
{metric_name} changed from {prev_value} to {latest_value} ({change_description}).

Filing excerpts:
{context}

Instructions:
- Explain the change in 2-3 sentences, using only information explicitly supported by the excerpts.
- If the excerpts do not clearly explain this specific change, say so honestly instead of guessing.
- Cite which excerpt(s) you used by their bracketed ID, e.g. [mda_006].
"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


if __name__ == "__main__":
    print("=" * 60)
    print("TEST 1: Operating Margin")
    print("=" * 60)
    result1 = explain_change(
        metric_name="Operating Margin",
        prev_value="7.99%",
        latest_value="8.18%",
        change_description="increased by 0.19 percentage points",
    )
    print(result1)

    print("\n" + "=" * 60)
    print("TEST 2: Net Income")
    print("=" * 60)
    result2 = explain_change(
        metric_name="Net Income",
        prev_value="$3,219 million",
        latest_value="$3,108 million",
        change_description="decreased by 3.45%",
    )
    print(result2)