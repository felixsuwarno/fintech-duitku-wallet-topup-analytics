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
# 3c. Monthly Active User Forecasting
# Estimate future engagement by tracking monthly unique active
# customers and projecting the next 1–3 months using a simple trend.
# -------------------------------------------------------------------

# 3c.1 Ensure transaction_date is datetime
df["transaction_date"] = pd.to_datetime(df["transaction_date"])

# 3c.2 Monthly active customers (unique customer_id per month)
df_monthly_mau = (
    df.set_index("transaction_date")
      .resample("MS")  # MS = Month Start
      .agg(monthly_active_customers=("customer_id", "nunique"))
      .reset_index()
)

print("\n=== Monthly active customers (head) ===")
print(df_monthly_mau)

# 3c.3 Add month index for linear trend
df_monthly_mau["month_index"] = range(len(df_monthly_mau))

srs_x_month_index_mau = df_monthly_mau["month_index"].values
srs_y_mau = df_monthly_mau["monthly_active_customers"].values

# 3c.4 Fit simple linear trend: MAU = a * month_index + b
srs_coeffs_mau = np.polyfit(srs_x_month_index_mau, srs_y_mau, deg=1)
srs_mau_trend_fitted = np.polyval(srs_coeffs_mau, srs_x_month_index_mau)
df_monthly_mau["mau_trend"] = srs_mau_trend_fitted

# 3c.5 Forecast next 1–3 months
forecast_steps = 3
srs_future_index_mau = np.arange(
    len(srs_x_month_index_mau),
    len(srs_x_month_index_mau) + forecast_steps
)
srs_future_forecast_mau = np.polyval(srs_coeffs_mau, srs_future_index_mau)

srs_future_dates_mau = pd.date_range(
    start=df_monthly_mau["transaction_date"].max() + pd.offsets.MonthBegin(),
    periods=forecast_steps,
    freq="MS"
)

df_mau_forecast = pd.DataFrame({
    "transaction_date": srs_future_dates_mau,
    "monthly_active_customers_forecast": srs_future_forecast_mau,
})

print("\n=== Forecasted monthly active customers (next months) ===")
print(df_mau_forecast)

# 3c.6 Plot: Actual MAU + trend + forecast
fig, ax = plt.subplots(figsize=(12, 5))

# Historical MAU
ax.plot(
    df_monthly_mau["transaction_date"],
    df_monthly_mau["monthly_active_customers"],
    marker="o",
    linestyle="-",
    label="Actual MAU",
)

# Historical trend line
ax.plot(
    df_monthly_mau["transaction_date"],
    df_monthly_mau["mau_trend"],
    linestyle="--",
    label="Trend line (historical)",
)

# Forecasted MAU (next 1–3 months)
ax.plot(
    df_mau_forecast["transaction_date"],
    df_mau_forecast["monthly_active_customers_forecast"],
    marker="o",
    linestyle="--",
    label="Forecast (next 1–3 months)",
)

ax.set_xlabel("Month")
ax.set_ylabel("Monthly active customers (unique)")
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:,.0f}"))
plt.title("Monthly Forecasting For Active Users")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()
