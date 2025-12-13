import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


# 0. Load data
# -------------------------------------------------------------------
script_directory = os.path.dirname(os.path.abspath(__file__))
csv_file_path    = os.path.join(script_directory, "..", "data", "transactions_clean.csv")
csv_file_path    = os.path.normpath(csv_file_path)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

df = pd.read_csv(csv_file_path)


# 1. Monthly load + platform revenue
# -------------------------------------------------------------------
df_monthly = (
    df.groupby("year_month", as_index=False)
      .agg({
          "net_amount": "sum",
          "fee_internal_amount": "sum"
      })
      .rename(columns={
          "net_amount": "monthly_load_amount",
          "fee_internal_amount": "monthly_platform_revenue"
      })
      .sort_values("year_month")
)

srs_month  = df_monthly["year_month"]
srs_load   = df_monthly["monthly_load_amount"]
srs_rev    = df_monthly["monthly_platform_revenue"]


# 2. Plot: Customer Load (bars) vs Platform Revenue (line)
# -------------------------------------------------------------------
fig, ax1 = plt.subplots(figsize=(10, 5))

# Blue bars: customer load
ax1.bar(
    srs_month,
    srs_load,
    color="tab:blue",
    label="Customer Load Amount (net_amount)"
)
ax1.set_xlabel("Month")
ax1.set_ylabel("Customer Load Amount (IDR)", color="tab:blue")
ax1.tick_params(axis='y', labelcolor="tab:blue")
ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:,.0f}"))

plt.xticks(rotation=45)

# Orange line: platform revenue
ax2 = ax1.twinx()
ax2.plot(
    srs_month,
    srs_rev,
    marker="o",
    color="tab:orange",
    label="Platform Revenue (fee_internal_amount)"
)
ax2.set_ylabel("Platform Revenue (IDR)", color="tab:orange")
ax2.tick_params(axis='y', labelcolor="tab:orange")
ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:,.0f}"))

plt.title("Revenue vs Transaction Volume", fontsize=14)


fig.tight_layout()

plt.show()
