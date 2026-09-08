import pickle
from pathlib import Path
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = PROJECT_ROOT / "data" / "processed" / "nike_faiss.index"
METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "nike_chunks_metadata.pkl"

index = faiss.read_index(str(INDEX_PATH))
with open(METADATA_PATH, "rb") as f:
    chunks = pickle.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve(query: str, k: int = 3):
    query_embedding = model.encode([query]).astype("float32")
    distances, indices = index.search(query_embedding, k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        chunk = chunks[idx]
        results.append({
            "chunk_id": chunk["chunk_id"],
            "distance": float(dist),
            "text": chunk["text"],
        })
    return results


test_queries = [
    "reasons for operating margin change, cost increases, pricing",
    "reasons for net income decline",
    "cash and liquidity position",
]

for query in test_queries:
    print(f"\n{'=' * 60}")
    print(f"QUERY: {query}")
    print('=' * 60)
    results = retrieve(query, k=2)
    for r in results:
        print(f"\n[{r['chunk_id']}] (distance: {r['distance']:.3f})")
        print(r["text"][:300])
