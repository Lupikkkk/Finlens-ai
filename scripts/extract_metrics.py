import json
from pathlib import Path
from datetime import date
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "nike_facts.json"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "nike_metrics.csv"

with open(INPUT_PATH) as f:
    data = json.load(f)

us_gaap = data["facts"]["us-gaap"]


def period_days(entry):
    start = date.fromisoformat(entry["start"])
    end = date.fromisoformat(entry["end"])
    return (end - start).days


def get_latest_two_annual_values(tag: str):
    """For income-statement items (Revenue, Net Income) which have both 'start' and 'end'."""
    entries = us_gaap[tag]["units"]["USD"]
    annual_entries = [
        e for e in entries
        if e["form"] == "10-K" and 350 <= period_days(e) <= 380
    ]

    seen_end_dates = {}
    for e in annual_entries:
        seen_end_dates[e["end"]] = e

    sorted_years = sorted(seen_end_dates.values(), key=lambda e: e["end"], reverse=True)

    latest = sorted_years[0]
    previous = sorted_years[1]
    return latest["val"], previous["val"], latest["end"], previous["end"]


def get_latest_two_instant_values(tag: str):
    """For balance-sheet items (Cash, Debt) which only have an 'end' date, no 'start'."""
    entries = us_gaap[tag]["units"]["USD"]
    annual_entries = [e for e in entries if e["form"] == "10-K"]

    seen_end_dates = {}
    for e in annual_entries:
        seen_end_dates[e["end"]] = e

    sorted_dates = sorted(seen_end_dates.values(), key=lambda e: e["end"], reverse=True)

    latest = sorted_dates[0]
    previous = sorted_dates[1]
    return latest["val"], previous["val"], latest["end"], previous["end"]


# Fetch raw tags
revenue_latest, revenue_prev, latest_end, prev_end = get_latest_two_annual_values(
    "RevenueFromContractWithCustomerExcludingAssessedTax"
)
gross_profit_latest, gross_profit_prev, _, _ = get_latest_two_annual_values("GrossProfit")
sga_latest, sga_prev, _, _ = get_latest_two_annual_values("SellingGeneralAndAdministrativeExpense")
net_income_latest, net_income_prev, _, _ = get_latest_two_annual_values("NetIncomeLoss")

cash_latest, cash_prev, _, _ = get_latest_two_instant_values("CashAndCashEquivalentsAtCarryingValue")
debt_noncurrent_latest, debt_noncurrent_prev, _, _ = get_latest_two_instant_values("LongTermDebtNoncurrent")
debt_current_latest, debt_current_prev, _, _ = get_latest_two_instant_values("LongTermDebtCurrent")

# Derived metrics
operating_income_latest = gross_profit_latest - sga_latest
operating_income_prev = gross_profit_prev - sga_prev

operating_margin_latest = operating_income_latest / revenue_latest
operating_margin_prev = operating_income_prev / revenue_prev

net_margin_latest = net_income_latest / revenue_latest
net_margin_prev = net_income_prev / revenue_prev

total_debt_latest = debt_noncurrent_latest + debt_current_latest
total_debt_prev = debt_noncurrent_prev + debt_current_prev

# Build a DataFrame: rows = metrics, columns = periods
df = pd.DataFrame({
    "metric": [
        "Revenue", "Operating Income", "Operating Margin",
        "Net Income", "Net Margin", "Cash", "Total Debt"
    ],
    f"previous ({prev_end})": [
        revenue_prev, operating_income_prev, operating_margin_prev,
        net_income_prev, net_margin_prev, cash_prev, total_debt_prev
    ],
    f"latest ({latest_end})": [
        revenue_latest, operating_income_latest, operating_margin_latest,
        net_income_latest, net_margin_latest, cash_latest, total_debt_latest
    ],
})

print(df.to_string(index=False))

df.to_csv(OUTPUT_PATH, index=False)
print(f"\nSaved to {OUTPUT_PATH}")
