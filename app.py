import sys
from pathlib import Path

# Make sure we can import from scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

import streamlit as st
import pandas as pd
from explain_change import explain_change

PROJECT_ROOT = Path(__file__).resolve().parent
CHANGES_PATH = PROJECT_ROOT / "data" / "processed" / "nike_changes.csv"

st.set_page_config(page_title="FinLens AI", layout="wide")

st.title("FinLens AI")
st.caption("Detect what changed. Understand why. Verify the evidence.")

st.header("Nike — FY2025 vs FY2026")

changes_df = pd.read_csv(CHANGES_PATH)

# Rename columns for display
prev_col = changes_df.columns[1]
latest_col = changes_df.columns[2]

st.subheader("Overview")
st.dataframe(changes_df, use_container_width=True)

st.subheader("What Changed?")
st.caption("Material changes only — click Explain to see the evidence-backed reason.")

material_changes = changes_df[changes_df["is_material"]]

for _, row in material_changes.iterrows():
    metric = row["metric"]
    prev_val = row[prev_col]
    latest_val = row[latest_col]
    change = row["change"]
    change_type = row["change_type"]

    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    with col1:
        st.write(f"**{metric}**")
    with col2:
        st.write(f"{prev_val:,.2f} → {latest_val:,.2f}")
    with col3:
        sign = "+" if change > 0 else ""
        st.write(f"{sign}{change}{change_type}")
    with col4:
        explain_clicked = st.button("Explain", key=f"explain_{metric}")

    if explain_clicked:
        change_description = f"{'increased' if change > 0 else 'decreased'} by {abs(change)}{change_type}"
        with st.spinner("Retrieving evidence and generating explanation..."):
            try:
                explanation = explain_change(
                    metric_name=metric,
                    prev_value=f"{prev_val:,.2f}",
                    latest_value=f"{latest_val:,.2f}",
                    change_description=change_description,
                )
                st.info(explanation)
            except Exception as e:
                st.error(f"Could not generate explanation: {e}")

    st.divider()