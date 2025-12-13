import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# -------------------------------------------------
# Helper formatters
# -------------------------------------------------
def thousands(x, pos):
    return f"{x/1_000:,.0f}K"

def percent(x, pos):
    return f"{x:.0f}%"


# -------------------------------------------------
# 0. Load data
# -------------------------------------------------
script_directory = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.normpath(
    os.path.join(script_directory, "..", "data", "transactions_clean.csv")
)

df = pd.read_csv(csv_file_path)

# -------------------------------------------------
# 1. Validate and normalize
# -------------------------------------------------
required_cols = {"year_month", "fee_internal_amount"}
missing = required_cols - set(df.columns)
if missing:
    raise KeyError(f"Missing required columns: {missing}")

df["year_month"] = pd.PeriodIndex(df["year_month"], freq="M")
df["fee_internal_amount"] = pd.to_numeric(
    df["fee_internal_amount"], errors="coerce"
)

df = df.dropna(subset=["year_month", "fee_internal_amount"]).copy()

# -------------------------------------------------
# 2. Monthly revenue
# -------------------------------------------------
df_monthly = (
    df.groupby("year_month", as_index=False)["fee_internal_amount"]
      .sum()
      .sort_values("year_month")
      .rename(columns={"fee_internal_amount": "revenue"})
)

# -------------------------------------------------
# 3. MoM growth — BUSINESS-CORRECT DEFINITION
# -------------------------------------------------
df_monthly["mom_growth_pct"] = (
    df_monthly["revenue"].pct_change() * 100
)

# First month = baseline, define growth as 0%
df_monthly.loc[df_monthly.index[0], "mom_growth_pct"] = 0.0

# -------------------------------------------------
# 4. Plot
# -------------------------------------------------
fig, ax1 = plt.subplots(figsize=(10, 6))

# Revenue bars
ax1.bar(
    df_monthly["year_month"].astype(str),
    df_monthly["revenue"],
    width=0.6
)

ax1.set_xlabel("Month")
ax1.set_ylabel("Platform Revenue (Thousands IDR)")
ax1.yaxis.set_major_formatter(FuncFormatter(thousands))

# MoM growth line
ax2 = ax1.twinx()
ax2.plot(
    df_monthly["year_month"].astype(str),
    df_monthly["mom_growth_pct"],
    color="tab:orange",
    marker="o",
    linewidth=2
)

ax2.axhline(0, linestyle="--", linewidth=1, alpha=0.6)
ax2.set_ylabel("MoM Revenue Growth (%)")
ax2.yaxis.set_major_formatter(FuncFormatter(percent))

# -------------------------------------------------
# 5. Title & layout
# -------------------------------------------------
plt.title("02 — Monthly Revenue and Performance Growth")
plt.xticks(rotation=45)

fig.tight_layout()
plt.show()
