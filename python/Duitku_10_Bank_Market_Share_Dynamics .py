import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


# -----------------------------
# Helper formatter
# -----------------------------
def percent(x, pos):
    return f"{x * 100:.0f}%"


# -------------------------------------------------------------------
# 0. Load data
# -------------------------------------------------------------------
script_directory = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.normpath(
    os.path.join(script_directory, "..", "data", "transactions_clean.csv")
)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

df = pd.read_csv(csv_file_path)

# -------------------------------------------------------------------
# 1. Validate required fields
# -------------------------------------------------------------------
required_cols = {"year_month", "category", "net_amount"}
missing = required_cols - set(df.columns)
if missing:
    raise KeyError(
        f"Missing required columns: {missing}. "
        f"`year_month` must exist in transactions_clean.csv"
    )

df["year_month"] = pd.PeriodIndex(df["year_month"], freq="M")
df["net_amount"] = pd.to_numeric(df["net_amount"], errors="coerce").fillna(0)
df["bank"] = df["category"].astype(str).str.strip()

# -------------------------------------------------------------------
# 2. Monthly volume per bank
# -------------------------------------------------------------------
df_monthly_bank = (
    df.groupby(["year_month", "bank"], as_index=False)
      .agg(monthly_volume=("net_amount", "sum"))
)

# -------------------------------------------------------------------
# 3. Monthly total + volume share
# -------------------------------------------------------------------
df_month_total = (
    df_monthly_bank.groupby("year_month", as_index=False)
                   .agg(month_total=("monthly_volume", "sum"))
)

df_share = df_monthly_bank.merge(df_month_total, on="year_month", how="left")
df_share["volume_share"] = df_share["monthly_volume"] / df_share["month_total"]

# -------------------------------------------------------------------
# 4. Pivot for plotting (rows = month, cols = bank)
# -------------------------------------------------------------------
df_share_pivot = (
    df_share.pivot(index="year_month", columns="bank", values="volume_share")
            .fillna(0)
            .sort_index()
)

# -------------------------------------------------------------------
# 5. Plot — Bank market share dynamics
# -------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))

for bank in df_share_pivot.columns:
    ax.plot(
        df_share_pivot.index.astype(str),
        df_share_pivot[bank],
        marker="o",
        linewidth=2,
        label=bank
    )

ax.set_title("10 – Bank Market Share Dynamics (Monthly Volume Share)", fontsize=14)
ax.set_xlabel("Month")
ax.set_ylabel("Share of Total Top-Up Volume")
ax.yaxis.set_major_formatter(FuncFormatter(percent))

plt.xticks(rotation=45)
ax.legend(title="Bank")
fig.tight_layout()
plt.show()
