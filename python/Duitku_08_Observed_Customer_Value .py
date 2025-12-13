import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


# -----------------------------
# Helper formatters
# -----------------------------
def thousands(x, pos):
    return f"{x/1_000:.0f}K"


# 0) Load data
# -------------------------------------------------------------------
script_directory = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.normpath(os.path.join(script_directory, "..", "data", "transactions_clean.csv"))

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

df = pd.read_csv(csv_file_path)

# 1) Safety: enforce required columns + types
# -------------------------------------------------------------------
required_cols = ["id", "customer_id", "fee_internal_amount"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

df["fee_internal_amount"] = pd.to_numeric(df["fee_internal_amount"], errors="coerce")
df = df.dropna(subset=["customer_id", "fee_internal_amount"]).copy()

# Normalize customer_id (avoid "123.0" strings)
df["customer_id"] = df["customer_id"].astype(str).str.replace(r"\.0$", "", regex=True)

# 2) Compute Observed LTV per customer (within dataset window)
# -------------------------------------------------------------------
df_ltv = (
    df.groupby("customer_id", as_index=False)
      .agg(
          observed_ltv=("fee_internal_amount", "sum"),
          transaction_count=("id", "count")
      )
)

# Remove non-positive LTV if any (usually shouldn't exist, but protects plots/stats)
df_ltv = df_ltv[df_ltv["observed_ltv"] > 0].copy()

if df_ltv.empty:
    raise ValueError("No customers with positive observed_ltv found after cleaning.")

# 3) Summary statistics (Observed customer value)
# -------------------------------------------------------------------
mean_ltv = df_ltv["observed_ltv"].mean()
median_ltv = df_ltv["observed_ltv"].median()

p90 = df_ltv["observed_ltv"].quantile(0.90)
p95 = df_ltv["observed_ltv"].quantile(0.95)
p99 = df_ltv["observed_ltv"].quantile(0.99)

print("\n=== 08 - Observed Customer Value ===")
print("Observed LTV is computed as total platform internal fee per customer within the dataset window.")
print(f"Customers: {df_ltv.shape[0]:,}")
print(f"Mean observed LTV   : IDR {mean_ltv:,.0f}")
print(f"Median observed LTV : IDR {median_ltv:,.0f}")
print(f"P90 observed LTV    : IDR {p90:,.0f}")
print(f"P95 observed LTV    : IDR {p95:,.0f}")
print(f"P99 observed LTV    : IDR {p99:,.0f}")

# Optional: show top customers by observed LTV for quick sanity check
print("\nTop 10 customers by observed LTV:")
print(df_ltv.sort_values("observed_ltv", ascending=False).head(10))

# 4) Plot distribution (histogram)
# -------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5))

ax.hist(
    df_ltv["observed_ltv"],
    bins=40,
    edgecolor="black",
    alpha=0.85
)

ax.axvline(mean_ltv, color="red", linestyle="--", linewidth=1.5, label=f"Mean: {mean_ltv:,.0f}")
ax.axvline(median_ltv, color="green", linestyle="--", linewidth=1.5, label=f"Median: {median_ltv:,.0f}")
ax.axvline(p90, color="gray", linestyle="--", linewidth=1.0, label=f"P90: {p90:,.0f}")

ax.set_title("08 – Observed Customer Value (Observed LTV Distribution)", fontsize=14)
ax.set_xlabel("Observed LTV per Customer (Internal Fee Revenue, IDR)")
ax.set_ylabel("Number of Customers")

ax.xaxis.set_major_formatter(FuncFormatter(thousands))
ax.legend()

fig.tight_layout()
plt.show()
