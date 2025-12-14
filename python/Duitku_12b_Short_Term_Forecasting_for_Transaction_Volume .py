import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# ----------------------------
# Formatter: Billions (B)
# ----------------------------
def billions(x, pos):
    return f"{x / 1_000_000_000:.1f}B"


# ----------------------------
# Load data
# ----------------------------
script_dir      = os.path.dirname(os.path.abspath(__file__))
csv_path        = os.path.join(script_dir, "..", "data", "transactions_clean.csv")
df              = pd.read_csv(csv_path)

df["transaction_date"] = pd.to_datetime(df["transaction_date"])


# ----------------------------
# Monthly volume aggregation
# ----------------------------
df_monthly = (
    df.set_index("transaction_date")
      .resample("MS")
      .agg(monthly_volume=("net_amount", "sum"))
      .reset_index()
)

df_monthly["month_index"] = range(len(df_monthly))


# ----------------------------
# Trend + forecast
# ----------------------------
x = df_monthly["month_index"].values
y = df_monthly["monthly_volume"].values

coeffs = np.polyfit(x, y, deg=1)
trend = np.polyval(coeffs, x)

future_steps = 3
future_x = np.arange(len(x), len(x) + future_steps)
future_y = np.polyval(coeffs, future_x)

future_dates = pd.date_range(
    start=df_monthly["transaction_date"].max() + pd.offsets.MonthBegin(),
    periods=future_steps,
    freq="MS"
)


# ----------------------------
# Plot
# ----------------------------
fig, ax = plt.subplots(figsize=(12, 5))

ax.plot(df_monthly["transaction_date"], y, marker="o", label="Actual volume")
ax.plot(df_monthly["transaction_date"], trend, linestyle="--", label="Trend line (historical)")
ax.plot(future_dates, future_y, marker="o", linestyle="--", label="Forecast (next 1–3 months)")

ax.set_title("Monthly Forecasting for Transaction Volume")
ax.set_xlabel("Month")
ax.set_ylabel("Total top-up volume")
ax.yaxis.set_major_formatter(FuncFormatter(billions))

plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()
