import requests
from pathlib import Path

# SEC requires a real User-Agent with name and email, otherwise it blocks the request
HEADERS = {
    "User-Agent": "Artem Lubkovskyi artemlyb15@gmail.com"
}

FILING_URL = "https://www.sec.gov/Archives/edgar/data/0000320187/000032018726000088/nke-20260531.htm"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "nike_10k_2026.html"

def fetch_filing(url: str) -> str:
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.text

if __name__ == "__main__":
    html = fetch_filing(FILING_URL)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Done! Filing saved to {OUTPUT_PATH}")
    print(f"File size: {len(html):,} characters")
