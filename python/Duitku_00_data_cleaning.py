import os
import sys
import numpy as np
import pandas as pd


# 0. Setup paths and load CSV
# -------------------------------------------------------------------
script_directory = os.path.dirname(os.path.abspath(__file__))
csv_file_path    = os.path.join(script_directory, "..", "data", "transactions.csv")
csv_file_path    = os.path.normpath(csv_file_path)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

df = pd.read_csv(csv_file_path)

print("=== Raw Data Preview ===")
print(df.head())


# 1. Convert datetime fields (ONE LINE EACH)
# -------------------------------------------------------------------
df["paying_at"]  = pd.to_datetime(df["paying_at"],  errors="coerce")
df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

print("\n=== Datetime Conversion Complete ===")
print(df[["paying_at", "created_at"]].dtypes)


# 2. Create helper / analytical columns (ONE LINE EACH)
# -------------------------------------------------------------------
df["transaction_date"] = df["paying_at"].dt.date
df["year_month"]       = df["paying_at"].dt.to_period("M").astype(str)
df["cohort_month"]     = df.groupby("customer_id")["paying_at"].transform("min").dt.to_period("M").astype(str)

print("\n=== Derived Columns Added ===")
print(df[["paying_at", "created_at", "transaction_date", "year_month", "cohort_month"]].head())


# 3. Keep only needed columns (ONE LINE)
# -------------------------------------------------------------------
df_clean = df[[
    "id",
    "customer_id",
    "net_amount",
    "fee_internal_amount",
    "fee_external_amount",
    "category",
    "transaction_date",
    "year_month",
    "cohort_month",
    "created_at"
]].copy()

print("\n=== Final Clean Columns ===")
print(df_clean.columns.tolist())

print("\n=== Final Clean DataFrame Preview ===")
print(df_clean.head())


# 4. Save cleaned dataset (ONE LINE)
# -------------------------------------------------------------------
clean_csv_path = os.path.join(script_directory, "..", "table", "transactions_clean.csv")
clean_csv_path = os.path.normpath(clean_csv_path)

df_clean.to_csv(clean_csv_path, index=False)

print(f"\n=== Saved Cleaned Dataset to {clean_csv_path} ===")
