import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


# -----------------------------
# Helpers
# -----------------------------
def thousands(x, pos):
    """
    Format axis labels:
    - >= 1,000 -> show in K (e.g., 1.2K, 12K)
    - <  1,000 -> show as integer (e.g., 120)
    """
    if x < 1000:
        return f"{int(x):d}"
    return f"{x/1000:.1f}K".rstrip("0").rstrip(".")


# 0) Load data
# -------------------------------------------------------------------
script_directory = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.normpath(os.path.join(script_directory, "..", "data", "transactions_clean.csv"))

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

df = pd.read_csv(csv_file_path)

# 1) Validate + parse
# -------------------------------------------------------------------
required_cols = ["customer_id", "transaction_date"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
bad_dates = int(df["transaction_date"].isna().sum())
if bad_dates > 0:
    print(f"Warning: dropping {bad_dates:,} rows with unparseable transaction_date.")
    df = df.dropna(subset=["transaction_date"]).copy()

df["customer_id"] = df["customer_id"].astype(str).str.replace(r"\.0$", "", regex=True)

# 2) Snapshot date (as-of latest transaction in dataset)
# -------------------------------------------------------------------
snapshot_date = df["transaction_date"].max()
snapshot_month = snapshot_date.to_period("M")

print("\n=== 11 - Current Customer Engagement Health ===")
print(f"Snapshot date (as-of): {snapshot_date.date()} ({snapshot_month})")

# 3) Recency per customer
# -------------------------------------------------------------------
df_recency = (
    df.groupby("customer_id", as_index=False)
      .agg(last_tx_date=("transaction_date", "max"))
)

df_recency["recency_days"] = (snapshot_date - df_recency["last_tx_date"]).dt.days

# 4) Segment rules
# -------------------------------------------------------------------
conditions = [
    df_recency["recency_days"] <= 7,
    (df_recency["recency_days"] >= 8) & (df_recency["recency_days"] <= 30),
    df_recency["recency_days"] > 30,
]
labels = ["Active (≤7 days)", "At-risk (8–30 days)", "Inactive (>30 days)"]

df_recency["recency_segment"] = np.select(conditions, labels, default="Unknown")

segment_order = ["Active (≤7 days)", "At-risk (8–30 days)", "Inactive (>30 days)"]

# 5) Segment summary (counts + shares)
# -------------------------------------------------------------------
df_segment = (
    df_recency.groupby("recency_segment", as_index=False)
              .agg(customer_count=("customer_id", "count"))
)

df_segment = (
    df_segment.set_index("recency_segment")
              .reindex(segment_order, fill_value=0)
              .reset_index()
)

total_customers = int(df_segment["customer_count"].sum())
df_segment["customer_share"] = df_segment["customer_count"] / total_customers

active_7d_rate = float(df_segment.loc[df_segment["recency_segment"] == "Active (≤7 days)", "customer_share"].iloc[0])
active_30d_rate = float(
    df_segment.loc[df_segment["recency_segment"].isin(["Active (≤7 days)", "At-risk (8–30 days)"]), "customer_share"].sum()
)

avg_recency = df_recency["recency_days"].mean()
median_recency = df_recency["recency_days"].median()

print("\nEngagement KPIs:")
print(f"- Unique customers      : {total_customers:,}")
print(f"- 7-day active rate     : {active_7d_rate*100:.1f}%")
print(f"- 30-day active rate    : {active_30d_rate*100:.1f}%")
print(f"- Avg recency (days)    : {avg_recency:.1f}")
print(f"- Median recency (days) : {median_recency:.0f}")

print("\nRecency segment distribution:")
print(df_segment)

# 6) One chart: bars = counts, labels = %
# -------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5))

bars = ax.bar(df_segment["recency_segment"], df_segment["customer_count"])

for bar, share in zip(bars, df_segment["customer_share"]):
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{share*100:.1f}%",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
    )

ax.set_title(f"11 – Current Customer Engagement Health (As of {snapshot_month})", fontsize=14)
ax.set_xlabel("Recency segment")
ax.set_ylabel("Number of customers")
ax.yaxis.set_major_formatter(FuncFormatter(thousands))

plt.xticks(rotation=15)
fig.tight_layout()
plt.show()
