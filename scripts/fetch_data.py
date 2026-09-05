import requests
import json
from pathlib import Path

# SEC requires a User-Agent with your name and email, otherwise it blocks the request
HEADERS = {
    "User-Agent": "Artem Lubkovskyi artemlyb15@gmail.com"
}

# Nike's CIK (Central Index Key) — the company's unique SEC identifier
CIK = "0000320187"

# Project root = one level above scripts/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "nike_facts.json"

def fetch_company_facts(cik: str) -> dict:
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    data = fetch_company_facts(CIK)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f)
    print(f"Done! Data saved to {OUTPUT_PATH}")
