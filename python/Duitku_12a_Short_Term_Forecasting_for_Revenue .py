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
# 3a. Monthly Revenue Forecasting
# Forecast monthly internal fee revenue using historical monthly totals
# and a simple linear trend to project the next 1–3 months.
# -------------------------------------------------------------------

# 3a.1 Ensure transaction_date is datetime
df["transaction_date"] = pd.to_datetime(df["transaction_date"])

# 3a.2 Monthly internal fee revenue (sum of fee_internal_amount per month)
df_monthly_revenue = (
    df.set_index("transaction_date")
      .resample("MS")  # MS = Month Start
      .agg(internal_fee_revenue=("fee_internal_amount", "sum"))
      .reset_index()
)

print("\n=== Monthly internal fee revenue (head) ===")
print(df_monthly_revenue)

# 3a.3 Add month index for linear trend
df_monthly_revenue["month_index"] = range(len(df_monthly_revenue))

srs_x_month_index = df_monthly_revenue["month_index"].values
srs_y_revenue = df_monthly_revenue["internal_fee_revenue"].values

# 3a.4 Fit simple linear trend: revenue = a * month_index + b
# Using NumPy polyfit (no external time-series libraries needed)
srs_coeffs = np.polyfit(srs_x_month_index, srs_y_revenue, deg=1)
srs_trend_fitted = np.polyval(srs_coeffs, srs_x_month_index)
df_monthly_revenue["revenue_trend"] = srs_trend_fitted

# 3a.5 Forecast next 1–3 months
forecast_steps = 3
srs_future_index = np.arange(len(srs_x_month_index), len(srs_x_month_index) + forecast_steps)
srs_future_forecast = np.polyval(srs_coeffs, srs_future_index)

srs_future_dates = pd.date_range(
    start=df_monthly_revenue["transaction_date"].max() + pd.offsets.MonthBegin(),
    periods=forecast_steps,
    freq="MS"
)

df_revenue_forecast = pd.DataFrame({
    "transaction_date": srs_future_dates,
    "internal_fee_revenue_forecast": srs_future_forecast,
})

print("\n=== Forecasted internal fee revenue (next months) ===")
print(df_revenue_forecast)

# 3a.6 Plot: Actual monthly revenue + trend + forecast
fig, ax = plt.subplots(figsize=(12, 5))

# Historical actual revenue
ax.plot(
    df_monthly_revenue["transaction_date"],
    df_monthly_revenue["internal_fee_revenue"],
    marker="o",
    linestyle="-",
    label="Actual revenue",
)

# Historical trend line
ax.plot(
    df_monthly_revenue["transaction_date"],
    df_monthly_revenue["revenue_trend"],
    linestyle="--",
    label="Trend line (historical)",
)

# Forecasted revenue (next 1–3 months)
ax.plot(
    df_revenue_forecast["transaction_date"],
    df_revenue_forecast["internal_fee_revenue_forecast"],
    marker="o",
    linestyle="--",
    label="Forecast (next 1–3 months)",
)

ax.set_xlabel("Month")
ax.set_ylabel("Internal fee revenue")
ax.yaxis.set_major_formatter(FuncFormatter(thousands))
plt.title("Monthly Forecasting for Revenue")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()
