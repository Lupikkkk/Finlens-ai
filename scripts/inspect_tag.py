import json
from pathlib import Path
from datetime import date

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "nike_facts.json"

with open(INPUT_PATH) as f:
    data = json.load(f)

tag_data = data["facts"]["us-gaap"]["NetIncomeLoss"]
entries = tag_data["units"]["USD"]

def period_days(entry):
    start = date.fromisoformat(entry["start"])
    end = date.fromisoformat(entry["end"])
    return (end - start).days

# Keep only 10-K filings with a full-year period (350-380 days, to allow for slight calendar variation)
annual_entries = [
    e for e in entries
    if e["form"] == "10-K" and 350 <= period_days(e) <= 380
]

# Deduplicate by end date
seen_end_dates = {}
for e in annual_entries:
    seen_end_dates[e["end"]] = e

sorted_years = sorted(seen_end_dates.values(), key=lambda e: e["end"], reverse=True)

print("Clean annual figures, most recent first:")
for e in sorted_years[:5]:
    print(f"  {e['start']} to {e['end']} = ${e['val']:,}  (filed {e['filed']})")

print()
print("=> These two will be our comparison periods:")
latest, previous = sorted_years[0], sorted_years[1]
print(f"  Latest:   {latest['start']} to {latest['end']} = ${latest['val']:,}")
print(f"  Previous: {previous['start']} to {previous['end']} = ${previous['val']:,}")