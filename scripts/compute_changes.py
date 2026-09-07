import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "nike_metrics.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "nike_changes.csv"

df = pd.read_csv(INPUT_PATH)

# The CSV has 3 columns: metric, previous (...), latest (...)
# Let's grab the actual column names dynamically since they contain dates
metric_col = df.columns[0]
prev_col = df.columns[1]
latest_col = df.columns[2]

# Metrics that are already expressed as ratios (margins) -> compare in percentage points (pp)
# Everything else -> compare as a percentage change
ratio_metrics = {"Operating Margin", "Net Margin"}

# Materiality thresholds (tuned for a relatively calm fiscal year with small swings)
PP_THRESHOLD = 0.15           # percentage points, for margin metrics
PCT_THRESHOLD_DEFAULT = 2.0   # % change, for Revenue / Net Income
PCT_THRESHOLD_BALANCE = 1.0   # % change, for Cash / Total Debt (balance sheet items)
balance_sheet_metrics = {"Cash", "Total Debt"}

results = []

for _, row in df.iterrows():
    metric = row[metric_col]
    prev_val = row[prev_col]
    latest_val = row[latest_col]

    if metric in ratio_metrics:
        # Values are stored as decimals (e.g. 0.08), convert to percentage points
        change = (latest_val - prev_val) * 100
        change_type = "pp"
        threshold = PP_THRESHOLD
    else:
        change = ((latest_val - prev_val) / prev_val) * 100
        change_type = "%"
        threshold = PCT_THRESHOLD_BALANCE if metric in balance_sheet_metrics else PCT_THRESHOLD_DEFAULT

    is_material = abs(change) >= threshold

    results.append({
        "metric": metric,
        prev_col: prev_val,
        latest_col: latest_val,
        "change": round(change, 2),
        "change_type": change_type,
        "is_material": is_material,
    })

changes_df = pd.DataFrame(results)
print(changes_df.to_string(index=False))

changes_df.to_csv(OUTPUT_PATH, index=False)
print(f"\nSaved to {OUTPUT_PATH}")

print("\nMaterial changes only:")
print(changes_df[changes_df["is_material"]].to_string(index=False))
