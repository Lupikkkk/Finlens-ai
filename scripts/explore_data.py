import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "nike_facts.json"

with open(INPUT_PATH) as f:
    data = json.load(f)

us_gaap_tags = data["facts"]["us-gaap"].keys()
print(f"Total tags in us-gaap: {len(us_gaap_tags)}")
print()

# Search for tags containing certain keywords, to find the right name
def search_tags(keyword: str):
    matches = [tag for tag in us_gaap_tags if keyword.lower() in tag.lower()]
    print(f"Tags containing '{keyword}':")
    for match in matches:
        print(f"  - {match}")
    print()

search_tags("SellingGeneral")
search_tags("CostsAndExpenses")
search_tags("IncomeLossFromContinuing")
