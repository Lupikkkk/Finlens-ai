from pathlib import Path
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "nike_10k_2026.html"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "nike_10k_text.txt"

with open(INPUT_PATH, encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# Extract all visible text, collapsing extra whitespace
raw_text = soup.get_text(separator="\n")
lines = [line.strip() for line in raw_text.split("\n")]
lines = [line for line in lines if line]  # drop empty lines
full_text = "\n".join(lines)

print(f"Total characters after cleaning: {len(full_text):,}")
print(f"Total lines: {len(lines):,}")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"Saved cleaned text to {OUTPUT_PATH}")

# Extract the real MD&A section: from the second "ITEM 7." occurrence
# (the first one is just the Table of Contents) up to "ITEM 7A."
mda_start = full_text.find("ITEM 7. MANAGEMENT'S DISCUSSION")
mda_end = full_text.find("ITEM 7A.", mda_start)

if mda_start == -1 or mda_end == -1:
    print("Could not locate MD&A boundaries — inspect manually.")
else:
    mda_text = full_text[mda_start:mda_end]
    print(f"\nMD&A section length: {len(mda_text):,} characters")
    print("\n--- First 500 characters ---")
    print(mda_text[:500])
    print("\n--- Last 500 characters ---")
    print(mda_text[-500:])

    MDA_OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "nike_mda_section.txt"
    with open(MDA_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(mda_text)
    print(f"\nSaved MD&A section to {MDA_OUTPUT_PATH}")