import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


# -----------------------------
# Axis formatter (Billions)
# -----------------------------
def billions(x, pos):
    """
    1.0B -> 1B
    1.2B -> 1.2B
    Avoids duplicated tick labels like 1B 1B 2B 2B...
    """
    b = x / 1_000_000_000
    s = f"{b:.1f}".rstrip("0").rstrip(".")
    return f"{s}B"


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
required_cols = {"year_month", "net_amount"}
missing = required_cols - set(df.columns)
if missing:
    raise KeyError(
        f"Missing required columns: {missing}. "
        f"`year_month` must exist in transactions_clean.csv"
    )

df["year_month"] = pd.PeriodIndex(df["year_month"], freq="M")
df["net_amount"] = pd.to_numeric(df["net_amount"], errors="coerce").fillna(0)

# -------------------------------------------------------------------
# 2. Monthly total top-up volume
# -------------------------------------------------------------------
df_monthly_topup_volume = (
    df.groupby("year_month")["net_amount"]
      .sum()
      .sort_index()
)

print("\n=== 01 - Monthly Platform Usage Volume (net_amount) ===")
print(df_monthly_topup_volume)

# -------------------------------------------------------------------
# 3. Bar chart — Monthly Platform Usage Volume
# -------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5))

df_monthly_topup_volume.plot(
    kind="bar",
    ax=ax,
    rot=45,
    edgecolor="black"
)

ax.yaxis.set_major_formatter(FuncFormatter(billions))

ax.set_title("01 – Monthly Platform Usage Volume (IDR)", fontsize=14)
ax.set_xlabel("Month")
ax.set_ylabel("Top-Up Volume (Billions IDR)")

fig.tight_layout()
plt.show()
