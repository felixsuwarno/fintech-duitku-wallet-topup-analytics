import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


# -----------------------------
# Helper formatter
# -----------------------------
def idr(x, pos):
    return f"{x:,.0f}"


# 0) Load data
# -------------------------------------------------------------------
script_directory = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.normpath(
    os.path.join(script_directory, "..", "data", "transactions_clean.csv")
)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

df = pd.read_csv(csv_file_path)

# 1) Validate required fields (year_month is REQUIRED)
# -------------------------------------------------------------------
required_cols = {"customer_id", "year_month", "fee_internal_amount"}
missing = required_cols - set(df.columns)
if missing:
    raise KeyError(
        f"Missing required columns: {missing}. "
        f"`year_month` must already exist in transactions_clean.csv"
    )

# Normalize types
df["customer_id"] = df["customer_id"].astype(str).str.replace(r"\.0$", "", regex=True)
df["year_month"] = pd.PeriodIndex(df["year_month"], freq="M")
df["fee_internal_amount"] = pd.to_numeric(df["fee_internal_amount"], errors="coerce")

df = df.dropna(subset=["customer_id", "year_month", "fee_internal_amount"]).copy()
df = df[df["fee_internal_amount"] != 0].copy()  # optional: drop zero-fee transactions

# 2) Define cohort month (first transaction month) FROM year_month ONLY
# -------------------------------------------------------------------
df["cohort_month"] = df.groupby("customer_id")["year_month"].transform("min")

# 3) Cohort age in months (integer-safe; no timestamps needed)
# -------------------------------------------------------------------
df["cohort_index"] = (
    df["year_month"].astype("int64")
    - df["cohort_month"].astype("int64")
)

# 4) Cohort size (ONE value per cohort_month)
# -------------------------------------------------------------------
df_cohort_size = (
    df.groupby("cohort_month")["customer_id"]
      .nunique()
      .rename("cohort_size")
      .reset_index()
)

# 5) Revenue per cohort & age
# -------------------------------------------------------------------
df_cohort_rev = (
    df.groupby(["cohort_month", "cohort_index"], as_index=False)
      .agg(period_fee=("fee_internal_amount", "sum"))
)

# 5b) IMPORTANT FIX: add missing cohort_month x cohort_index cells with zeros
#     so the curve becomes FLAT when nobody is active that month.
# -------------------------------------------------------------------
max_month = df["year_month"].max()
max_month_ord = max_month.ordinal  # scalar Period -> integer

rows = []
for cohort_m in df_cohort_size["cohort_month"]:
    cohort_m_ord = cohort_m.ordinal
    max_age_for_cohort = int(max_month_ord - cohort_m_ord)

    full_age_index = pd.Index(range(0, max_age_for_cohort + 1), name="cohort_index")

    # reindex ONLY the numeric series (period_fee)
    srs_fee = (
        df_cohort_rev.loc[df_cohort_rev["cohort_month"] == cohort_m]
        .set_index("cohort_index")["period_fee"]
        .reindex(full_age_index)
        .fillna(0)
    )

    grp = srs_fee.reset_index()
    grp["cohort_month"] = cohort_m
    rows.append(grp)

df_cohort_rev_full = pd.concat(rows, ignore_index=True)

# Attach cohort size (constant per cohort)
df_cohort = df_cohort_rev_full.merge(df_cohort_size, on="cohort_month", how="left")

# 6) Cumulative revenue → Customer value per acquired customer (within dataset window)
# -------------------------------------------------------------------
df_cohort = df_cohort.sort_values(["cohort_month", "cohort_index"])

df_cohort["cumulative_fee"] = (
    df_cohort.groupby("cohort_month")["period_fee"].cumsum()
)

df_cohort["customer_value_per_customer"] = (
    df_cohort["cumulative_fee"] / df_cohort["cohort_size"]
)

# 7) Pivot for plotting
# -------------------------------------------------------------------
value_pivot = df_cohort.pivot(
    index="cohort_index",
    columns="cohort_month",
    values="customer_value_per_customer"
).sort_index()

# 8) Cohort quality snapshot (last observed month)
# -------------------------------------------------------------------
df_snapshot = (
    df_cohort.sort_values(["cohort_month", "cohort_index"])
             .groupby("cohort_month")
             .tail(1)
             .sort_values("customer_value_per_customer", ascending=False)
             [["cohort_month", "cohort_size", "cohort_index", "customer_value_per_customer"]]
             .rename(columns={"cohort_index": "months_observed"})
)

print("\n=== 09 - Customer Value Quality by Acquisition Period ===")
print("Customer value = cumulative internal fee / original cohort size (within dataset window)")
print("\nCohort quality snapshot:")
print(df_snapshot.to_string(index=False))

# -------------------------------------------------
# 9) Plot cohort value curves (exclude last cohort)
# -------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 6))

# Business rule: exclude most recent cohort (no runway)
cohorts_to_plot = value_pivot.columns.sort_values()[:-1]

for cohort_month in cohorts_to_plot:
    srs = value_pivot[cohort_month].dropna()
    ax.plot(
        srs.index,
        srs.values,
        marker="o",
        markersize=3,
        linewidth=2,
        label=str(cohort_month)
    )

ax.set_title("09 – Customer Value Quality by Acquisition Period", fontsize=14)
ax.set_xlabel("Cohort Age (Months Since Acquisition)")
ax.set_ylabel("Cumulative Customer Value per Customer (Internal Fee, IDR)")
ax.yaxis.set_major_formatter(FuncFormatter(idr))

ax.legend(
    title="Cohort Month",
    loc="lower right",
    frameon=False
)

plt.tight_layout()
plt.show()
