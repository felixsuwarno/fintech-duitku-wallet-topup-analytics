import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def thousands(x, pos):
    value = x / 1000
    rounded = round(value, 1)
    return str(rounded) + "K"

def billions(x, pos):
    value = x / 1_000_000_000
    rounded = round(value, 1)
    return str(rounded) + "B"


# 0. Setup paths and load CSV
# -------------------------------------------------------------------
script_directory    = os.path.dirname(os.path.abspath(__file__))
csv_file_path       = os.path.join(script_directory, "..", "data", "transactions_clean.csv")
csv_file_path       = os.path.normpath(csv_file_path)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

df = pd.read_csv(csv_file_path)



# 1b. Monthly Platform Revenue + MoM % Growth (cleaned for execs)
# -------------------------------------------------------------------

# Monthly platform revenue (IDR)
srs_monthly_revenue = df.groupby("year_month")["fee_internal_amount"].sum().sort_index()

# Raw MoM growth % (current vs previous month)
srs_mom_growth_pct_raw = srs_monthly_revenue.pct_change() * 100

# hide first MoM point (meaningless when base is tiny)
srs_mom_growth_pct_clean            = srs_mom_growth_pct_raw.copy()
srs_mom_growth_pct_clean.iloc[0]    = np.nan

# cap extreme MoM % to ±200% for readability
srs_mom_growth_pct_clean = srs_mom_growth_pct_clean.clip(lower=-200, upper=200)

# debug table to inspect numbers
df_mom_debug = pd.DataFrame({"revenue": srs_monthly_revenue, "mom_growth_raw_pct": srs_mom_growth_pct_raw, "mom_growth_capped_pct": srs_mom_growth_pct_clean})

print("\n=== Revenue + MoM Growth Debug Table ===")
print(df_mom_debug)



# 2. Dual-Axis Chart — Revenue (bars) + Clean MoM % (line)
# -------------------------------------------------------------------
fig, ax_revenue = plt.subplots(figsize=(10, 5))



# Left axis: revenue in thousands (bars)
srs_monthly_revenue.plot(kind="bar", ax=ax_revenue, rot=45, edgecolor="black", color="tab:blue")

ax_revenue.yaxis.set_major_formatter(FuncFormatter(thousands))
ax_revenue.set_xlabel("Month")
ax_revenue.set_ylabel("Platform Revenue (Thousands IDR)")



# Right axis: MoM % growth (cleaned) as line
ax_mom = ax_revenue.twinx()

srs_mom_growth_pct_clean.plot(kind="line", ax=ax_mom, marker="o", color="tab:orange")

ax_mom.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:.1f}%"))
ax_mom.set_ylabel("MoM Revenue Growth (%)  [capped at ±200%]")



# Zero reference line
ax_mom.axhline(0, linewidth=1, linestyle="--", color="gray")



# Window + title
fig.canvas.manager.set_window_title("Figure 1b")
plt.title("Monthly Revenue and Performance Growth", fontsize=14)




fig.tight_layout()
plt.show()
