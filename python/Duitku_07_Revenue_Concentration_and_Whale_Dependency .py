import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


# -----------------------------
# Helper formatter
# -----------------------------
def as_percent(x, pos):
    return f"{x:.0f}%"


# 0) Load data
# -------------------------------------------------------------------
script_directory = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.normpath(os.path.join(script_directory, "..", "data", "transactions_clean.csv"))

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

df = pd.read_csv(csv_file_path)

# 1) Safety: enforce types + keep only valid rows
# -------------------------------------------------------------------
required_cols = ["customer_id", "fee_internal_amount"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

df["fee_internal_amount"] = pd.to_numeric(df["fee_internal_amount"], errors="coerce")
df = df.dropna(subset=["customer_id", "fee_internal_amount"]).copy()

# Normalize customer_id (avoid "123.0")
df["customer_id"] = df["customer_id"].astype(str).str.replace(r"\.0$", "", regex=True)

# 2) Build Pareto table (Revenue Concentration)
# -------------------------------------------------------------------
srs_fee_per_customer = (
    df.groupby("customer_id")["fee_internal_amount"]
      .sum()
      .sort_values(ascending=False)
)

df_pareto = srs_fee_per_customer.reset_index(name="total_internal_fee")
df_pareto["customer_rank"] = np.arange(1, len(df_pareto) + 1)
df_pareto["customer_pct"] = df_pareto["customer_rank"] / len(df_pareto)

total_fee = df_pareto["total_internal_fee"].sum()
if total_fee <= 0:
    raise ValueError("Total internal fee is 0 or negative. Cannot compute Pareto shares.")

df_pareto["cum_fee"] = df_pareto["total_internal_fee"].cumsum()
df_pareto["cum_share"] = df_pareto["cum_fee"] / total_fee

# 3) Key dependency metrics
# -------------------------------------------------------------------
first_80_row = df_pareto.loc[df_pareto["cum_share"] >= 0.80].iloc[0]
top_80_rank = int(first_80_row["customer_rank"])
top_80_pct = float(first_80_row["customer_pct"] * 100)

top_5_count = max(1, int(np.ceil(len(df_pareto) * 0.05)))
top_5_share = df_pareto.iloc[:top_5_count]["total_internal_fee"].sum() / total_fee * 100

top_1_count = max(1, int(np.ceil(len(df_pareto) * 0.01)))
top_1_share = df_pareto.iloc[:top_1_count]["total_internal_fee"].sum() / total_fee * 100

print("\n=== 07 - Revenue Concentration and Whale Dependency ===")
print(f"Customers in dataset: {len(df_pareto):,}")
print(f"Total internal fee revenue: {total_fee:,.0f}")

print("\n=== Top 10 Customers by Internal Fee (Revenue) ===")
print(df_pareto.head(10))

print(f"\nCustomers needed to reach 80% of revenue: {top_80_rank:,} ({top_80_pct:.1f}% of customers)")
print(f"Top 5% (Whales) revenue share: {top_5_share:.1f}%")
print(f"Top 1% revenue share: {top_1_share:.1f}%")

# 4) Pareto curve chart
# -------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5))

x_values = df_pareto["customer_pct"] * 100
y_values = df_pareto["cum_share"] * 100

ax.plot(x_values, y_values, marker="o", markersize=2, linewidth=2)

ax.axhline(80, color="gray", linestyle="--", linewidth=1)
ax.axvline(top_80_pct, color="gray", linestyle="--", linewidth=1)

ax.text(
    top_80_pct,
    80,
    f"  {top_80_pct:.1f}% of customers → 80% of revenue",
    va="bottom",
    ha="left",
    fontsize=11,
    fontweight="bold"
)

ax.xaxis.set_major_formatter(FuncFormatter(as_percent))
ax.yaxis.set_major_formatter(FuncFormatter(as_percent))

ax.set_title("07 – Revenue Concentration (Pareto Curve) and Whale Dependency", fontsize=14)
ax.set_xlabel("Cumulative % of Customers")
ax.set_ylabel("Cumulative % of Internal Fee Revenue")

fig.tight_layout()
plt.show()
