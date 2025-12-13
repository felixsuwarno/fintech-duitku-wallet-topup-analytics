import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

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
# 1. Validate required fields (year_month is REQUIRED)
# -------------------------------------------------------------------
required_cols = {"customer_id", "year_month", "fee_internal_amount"}
missing = required_cols - set(df.columns)
if missing:
    raise KeyError(
        f"Missing required columns: {missing}. "
        f"`year_month` must already exist in transactions_clean.csv"
    )

# Normalize dtypes
df["year_month"] = pd.PeriodIndex(df["year_month"], freq="M")
df["fee_internal_amount"] = pd.to_numeric(df["fee_internal_amount"], errors="coerce").fillna(0)

df["customer_id"] = (
    df["customer_id"]
    .astype(str)
    .str.replace(r"\.0$", "", regex=True)
)

# -------------------------------------------------------------------
# 2. Cohort construction (FROM year_month ONLY)
# -------------------------------------------------------------------
df["cohort_month"] = df.groupby("customer_id")["year_month"].transform("min")

# Cohort age in months (integer-safe)
df["cohort_age"] = (
    df["year_month"].astype("int64")
    - df["cohort_month"].astype("int64")
)

# -------------------------------------------------------------------
# 3. Aggregate per cohort cell
# -------------------------------------------------------------------
df_cohort = (
    df.groupby(["cohort_month", "cohort_age"], as_index=False)
      .agg(
          users=("customer_id", "nunique"),
          revenue=("fee_internal_amount", "sum")
      )
)

df_cohort["users"] = pd.to_numeric(df_cohort["users"], errors="coerce")
df_cohort["revenue"] = pd.to_numeric(df_cohort["revenue"], errors="coerce").fillna(0)

# -------------------------------------------------------------------
# 4. Retention percentage (Month 0 baseline)
# -------------------------------------------------------------------
srs_cohort_size = (
    df_cohort[df_cohort["cohort_age"] == 0]
    .set_index("cohort_month")["users"]
)

df_cohort["cohort_size"] = df_cohort["cohort_month"].map(srs_cohort_size)
df_cohort["retention_pct"] = (df_cohort["users"] / df_cohort["cohort_size"]) * 100

# -------------------------------------------------------------------
# 5. Pivot matrices
# -------------------------------------------------------------------
p_ret = df_cohort.pivot(index="cohort_month", columns="cohort_age", values="retention_pct")
p_usr = df_cohort.pivot(index="cohort_month", columns="cohort_age", values="users")
p_rev = df_cohort.pivot(index="cohort_month", columns="cohort_age", values="revenue")

# Enforce numeric
p_ret = p_ret.apply(pd.to_numeric, errors="coerce").astype("float64")
p_usr = p_usr.apply(pd.to_numeric, errors="coerce").astype("float64")
p_rev = p_rev.apply(pd.to_numeric, errors="coerce").astype("float64")

# Sort by cohort age
p_ret = p_ret.reindex(sorted(p_ret.columns), axis=1)
p_usr = p_usr.reindex(p_ret.columns, axis=1)
p_rev = p_rev.reindex(p_ret.columns, axis=1)

# -------------------------------------------------------------------
# 6. Heatmap with dynamic annotation colors
# -------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(14, 6))

cmap = plt.get_cmap("viridis")
vmin = np.nanmin(p_ret.values)
vmax = np.nanmax(p_ret.values)
norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

im = ax.imshow(p_ret.values, aspect="auto", cmap=cmap, norm=norm)

cbar = plt.colorbar(im, ax=ax)
cbar.set_label("Retention (%)")

ax.set_title(
    "05 – Customer Retention Quality by Acquisition Period\n"
    "Retention (%) with Users and Revenue per Cohort Cell",
    fontsize=14
)
ax.set_xlabel("Cohort Age (Months Since First Transaction)")
ax.set_ylabel("Cohort Month")

ax.set_xticks(np.arange(p_ret.shape[1]))
ax.set_xticklabels([str(c) for c in p_ret.columns])
ax.set_yticks(np.arange(p_ret.shape[0]))
ax.set_yticklabels([str(i) for i in p_ret.index])

def text_color_for_cell(retention_value: float) -> str:
    rgba = cmap(norm(retention_value))
    r, g, b, _ = rgba
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "black" if luminance > 0.6 else "white"

# Cell annotations
for i in range(p_ret.shape[0]):
    for j in range(p_ret.shape[1]):
        r = p_ret.iat[i, j]
        u = p_usr.iat[i, j]
        rev = p_rev.iat[i, j]

        if np.isnan(r) or np.isnan(u) or np.isnan(rev):
            continue

        ax.text(
            j, i,
            f"{r:.0f}%\nUsers={int(u)}\nRev={rev:,.0f}",
            ha="center",
            va="center",
            fontsize=8,
            color=text_color_for_cell(r)
        )

plt.tight_layout()
plt.show()
