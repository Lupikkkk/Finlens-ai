import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "nike_mda_section.txt"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "nike_chunks.json"

with open(INPUT_PATH, encoding="utf-8") as f:
    text = f.read()

CHUNK_SIZE_WORDS = 400
OVERLAP_WORDS = 50

words = text.split()
print(f"Total words in MD&A section: {len(words):,}")

chunks = []
start = 0
chunk_id = 0

while start < len(words):
    end = start + CHUNK_SIZE_WORDS
    chunk_words = words[start:end]
    chunk_text = " ".join(chunk_words)

    if len(chunk_words) < 30:
        break

    chunks.append({
        "chunk_id": f"mda_{chunk_id:03d}",
        "section": "Item 7 — MD&A",
        "text": chunk_text,
        "word_count": len(chunk_words),
    })

    chunk_id += 1
    start += CHUNK_SIZE_WORDS - OVERLAP_WORDS

print(f"Created {len(chunks)} chunks")
print(f"\n--- Sample chunk (first one) ---")
print(chunks[0]["text"][:300])
print(f"\n--- Sample chunk (middle one) ---")
mid = len(chunks) // 2
print(chunks[mid]["text"][:300])

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2)

print(f"\nSaved {len(chunks)} chunks to {OUTPUT_PATH}")