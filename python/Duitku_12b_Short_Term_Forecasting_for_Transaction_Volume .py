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


# -------------------------------------------------------------------
# 0. Setup paths and load CSV
# -------------------------------------------------------------------
script_directory = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(script_directory, "..", "data", "transactions_clean.csv")
csv_file_path = os.path.normpath(csv_file_path)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

df = pd.read_csv(csv_file_path)

print(df)

# -------------------------------------------------------------------
# 3b. Monthly Transaction Volume Forecasting
# Forecast monthly total net_amount (top-up volume) using historical
# monthly totals and a simple linear trend (next 1–3 months).
# -------------------------------------------------------------------

# 3b.1 Ensure transaction_date is datetime
df["transaction_date"] = pd.to_datetime(df["transaction_date"])

# 3b.2 Monthly transaction volume (sum of net_amount per month)
df_monthly_volume = (
    df.set_index("transaction_date")
      .resample("MS")  # MS = Month Start
      .agg(monthly_net_amount=("net_amount", "sum"))
      .reset_index()
)

print("\n=== Monthly transaction volume (head) ===")
print(df_monthly_volume)

# 3b.3 Add month index for linear trend
df_monthly_volume["month_index"] = range(len(df_monthly_volume))

srs_x_month_index_vol = df_monthly_volume["month_index"].values
srs_y_monthly_volume = df_monthly_volume["monthly_net_amount"].values

# 3b.4 Fit simple linear trend: volume = a * month_index + b
srs_coeffs_volume = np.polyfit(srs_x_month_index_vol, srs_y_monthly_volume, deg=1)
srs_volume_trend_fitted = np.polyval(srs_coeffs_volume, srs_x_month_index_vol)
df_monthly_volume["volume_trend"] = srs_volume_trend_fitted

# 3b.5 Forecast next 1–3 months
forecast_steps = 3
srs_future_index_vol = np.arange(
    len(srs_x_month_index_vol),
    len(srs_x_month_index_vol) + forecast_steps
)
srs_future_forecast_vol = np.polyval(srs_coeffs_volume, srs_future_index_vol)

srs_future_dates_vol = pd.date_range(
    start=df_monthly_volume["transaction_date"].max() + pd.offsets.MonthBegin(),
    periods=forecast_steps,
    freq="MS"
)

df_volume_forecast = pd.DataFrame({
    "transaction_date": srs_future_dates_vol,
    "monthly_net_amount_forecast": srs_future_forecast_vol,
})

print("\n=== Forecasted transaction volume (next months) ===")
print(df_volume_forecast)

# 3b.6 Plot: Actual monthly volume + trend + forecast
fig, ax = plt.subplots(figsize=(12, 5))

# Historical actual volume
ax.plot(
    df_monthly_volume["transaction_date"],
    df_monthly_volume["monthly_net_amount"],
    marker="o",
    linestyle="-",
    label="Actual volume",
)

# Historical trend line
ax.plot(
    df_monthly_volume["transaction_date"],
    df_monthly_volume["volume_trend"],
    linestyle="--",
    label="Trend line (historical)",
)

# Forecasted volume (next 1–3 months)
ax.plot(
    df_volume_forecast["transaction_date"],
    df_volume_forecast["monthly_net_amount_forecast"],
    marker="o",
    linestyle="--",
    label="Forecast (next 1–3 months)",
)

ax.set_xlabel("Month")
ax.set_ylabel("Total top-up volume (net_amount)")
ax.yaxis.set_major_formatter(FuncFormatter(thousands))
plt.title("Monthly Forecasting For Transaction Volume")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()
