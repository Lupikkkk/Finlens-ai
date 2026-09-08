import json
import pickle
from pathlib import Path
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHUNKS_PATH = PROJECT_ROOT / "data" / "processed" / "nike_chunks.json"
INDEX_PATH = PROJECT_ROOT / "data" / "processed" / "nike_faiss.index"
METADATA_PATH = PROJECT_ROOT / "data" / "processed" / "nike_chunks_metadata.pkl"

with open(CHUNKS_PATH, encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} chunks")

# Load a small, fast, local embedding model (no API key needed)
print("Loading embedding model (this may take a moment on first run)...")
model = SentenceTransformer("all-MiniLM-L6-v2")

texts = [chunk["text"] for chunk in chunks]
embeddings = model.encode(texts, show_progress_bar=True)
embeddings = np.array(embeddings).astype("float32")

print(f"Embeddings shape: {embeddings.shape}")

# Build a simple flat FAISS index (fine for a few hundred chunks)
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

print(f"FAISS index built with {index.ntotal} vectors")

# Save the index and the chunk metadata (so we can map results back to text)
faiss.write_index(index, str(INDEX_PATH))
with open(METADATA_PATH, "wb") as f:
    pickle.dump(chunks, f)

print(f"Saved index to {INDEX_PATH}")
print(f"Saved metadata to {METADATA_PATH}")