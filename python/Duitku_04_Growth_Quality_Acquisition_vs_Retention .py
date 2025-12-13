import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 0. Setup paths and load CSV
# -------------------------------------------------------------------
script_directory    = os.path.dirname(os.path.abspath(__file__))
csv_file_path       = os.path.join(script_directory, "..", "data", "transactions_clean.csv")
csv_file_path       = os.path.normpath(csv_file_path)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

df = pd.read_csv(csv_file_path)



# 1c. Monthly New vs Returning Customers
# -------------------------------------------------------------------
# Unique customer appearances per month  (ONE LINE)
df_monthly_customer = df[["year_month", "customer_id"]].drop_duplicates()

# First month each customer appeared  (SERIES → srs_)
srs_first_month_per_customer = df_monthly_customer.groupby("customer_id")["year_month"].min().rename("first_year_month")


# Merge Series into monthly customer table  (ONE LINE)
df_monthly_customer = df_monthly_customer.merge(srs_first_month_per_customer, on="customer_id", how="left")

# Label New vs Returning  (ONE LINE)
df_monthly_customer["customer_type"] = np.where(df_monthly_customer["year_month"] == df_monthly_customer["first_year_month"],"New","Returning")

# Count by month & type (ONE LINE)
df_monthly_new_returning = df_monthly_customer.groupby(["year_month", "customer_type"])["customer_id"].nunique().unstack(fill_value=0).sort_index()

print("\n=== Monthly New vs Returning Customers ===")
print(df_monthly_new_returning)



# 2. Bar Chart — Monthly New vs Returning Customers
# -------------------------------------------------------------------
plt.figure(figsize=(10, 5))

ax = df_monthly_new_returning.plot(
    kind        = "bar",
    stacked     = True,
    edgecolor   = "black",
    rot         = 45,
    color=["tab:blue", "tab:orange"]   # New, Returning
)

fig = plt.gcf()
fig.canvas.manager.set_window_title("Figure 1c")

plt.title("Growth Quality: Acquisition vs Retention", fontsize=14)
plt.xlabel("Month")
plt.ylabel("Number of Customers")
plt.legend(title="Customer Type")
plt.tight_layout()

plt.show()
