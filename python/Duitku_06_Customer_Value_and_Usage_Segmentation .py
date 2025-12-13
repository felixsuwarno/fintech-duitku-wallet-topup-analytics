import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


# -------------------------------------------------
# Helper formatter (NO 0.xK)
# -------------------------------------------------
def thousands(x, pos):
    """
    < 1,000   -> 123
    < 1,000,000 -> 12K
    else      -> 1.2M (optional but nice)
    """
    x = float(x)
    if abs(x) < 1_000:
        return f"{int(round(x)):,}"
    if abs(x) < 1_000_000:
        return f"{int(round(x / 1_000)):,}K"
    s = f"{x/1_000_000:.1f}".rstrip("0").rstrip(".")
    return f"{s}M"


# -------------------------------------------------
# 0. Load data
# -------------------------------------------------
script_directory = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.normpath(
    os.path.join(script_directory, "..", "data", "transactions_clean.csv")
)

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

df = pd.read_csv(csv_file_path)

# Basic validation + type safety
required_cols = {"customer_id", "id", "net_amount"}
missing = required_cols - set(df.columns)
if missing:
    raise KeyError(f"Missing required columns: {missing}. Available: {df.columns.tolist()}")

df["net_amount"] = pd.to_numeric(df["net_amount"], errors="coerce")
df = df.dropna(subset=["customer_id", "id", "net_amount"]).copy()
df["customer_id"] = df["customer_id"].astype(str).str.replace(r"\.0$", "", regex=True)

# -------------------------------------------------
# 1. Build per-customer usage & value metrics
# -------------------------------------------------
df_customer = (
    df.groupby("customer_id", as_index=True)
      .agg(
          topup_count=("id", "count"),
          avg_topup_amount=("net_amount", "mean"),
          total_topup_amount=("net_amount", "sum")
      )
)

srs_topup_count = df_customer["topup_count"]
srs_avg_topup   = df_customer["avg_topup_amount"]
srs_total_value = df_customer["total_topup_amount"]

# -------------------------------------------------
# 2. Value-based customer segmentation (volume-based)
# -------------------------------------------------
p20 = srs_total_value.quantile(0.20)
p80 = srs_total_value.quantile(0.80)
p95 = srs_total_value.quantile(0.95)

def assign_segment(value):
    if value >= p95:
        return "Whale (Top 5%)"
    elif value >= p80:
        return "High Value (Next 15%)"
    elif value >= p20:
        return "Mass Market (Middle 60%)"
    else:
        return "Long Tail (Bottom 20%)"

df_customer["segment"] = srs_total_value.apply(assign_segment)

# -------------------------------------------------
# 3. Visual encoding (color + size = same meaning)
# -------------------------------------------------
segment_colors = {
    "Long Tail (Bottom 20%)":   "#1F77B4",
    "Mass Market (Middle 60%)": "#7FB3D5",
    "High Value (Next 15%)":    "#FF7F0E",
    "Whale (Top 5%)":           "#D62728",
}

segment_sizes = {
    "Long Tail (Bottom 20%)":   40,
    "Mass Market (Middle 60%)": 90,
    "High Value (Next 15%)":    180,
    "Whale (Top 5%)":           300,
}

df_customer["color"] = df_customer["segment"].map(segment_colors)
df_customer["size"]  = df_customer["segment"].map(segment_sizes)

# -------------------------------------------------
# 4. Scatter plot — Customer Value & Usage
# -------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))
fig.canvas.manager.set_window_title("Figure 06")

ax.scatter(
    srs_topup_count,
    srs_avg_topup,
    s=df_customer["size"],
    c=df_customer["color"],
    alpha=0.65,
    edgecolor="black",
    linewidth=0.5
)

ax.set_title("06 – Customer Value and Usage Segmentation (Volume-Based)", fontsize=14)
ax.set_xlabel("Top-Up Frequency (Number of Transactions)")
ax.set_ylabel("Average Top-Up Amount (IDR)")
ax.yaxis.set_major_formatter(FuncFormatter(thousands))

ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.4)

# -------------------------------------------------
# 5. Unified legend (color + size)
# -------------------------------------------------
legend_handles = []
legend_labels = []

for segment in segment_colors:
    handle = plt.scatter(
        [], [],
        s=segment_sizes[segment],
        color=segment_colors[segment],
        edgecolor="black",
        linewidth=0.7,
        alpha=0.8
    )
    legend_handles.append(handle)
    legend_labels.append(segment)

ax.legend(
    legend_handles,
    legend_labels,
    title="Customer Segment",
    loc="upper left",
    bbox_to_anchor=(1.02, 1),
    frameon=True
)

plt.tight_layout(rect=[0, 0, 0.80, 1])
plt.show()
