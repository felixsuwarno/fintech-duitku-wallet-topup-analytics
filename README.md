# FinTech “Duitku” Wallet Top-Up Analytics  
**Customer Behavior • Cohorts • LTV • Revenue Forecasting**

Python analysis of real **Duitku** digital wallet top-up transactions.  
This project extracts behavioral insights, builds customer cohorts, models LTV, and forecasts monthly revenue.  
An end-to-end FinTech analytics workflow built from raw transactions to business-ready insights.

**Dataset Coverage:**  
Transactions in this dataset span **July 18, 2024 → January 24, 2025**, representing ~6 months of real digital wallet top-up activity. This rolling-window time range mirrors how FinTech companies typically analyze recent user behavior, revenue trends, and cohort performance.


---

<br>

## Project Summary

This project analyzes real transaction-level data from a digital wallet system to understand:

- How users fund their accounts  
- How customer value evolves over time  
- How monthly revenue can be forecasted  

Using Python, the analysis covers:

- Behavioral insights  
- Cohort dynamics  
- Customer lifetime value (LTV) modeling  
- Time-series revenue forecasting  

The goal is to support real-world FinTech decision-making with clear, data-driven insights.

---

<br>

## Dataset

The original dataset can be downloaded here:

**[transactions.xlsx (Zenodo)](https://zenodo.org/records/17092322/files/transactions.xlsx?download=1)**

Full detailed data dictionary:  
**[Full Data Dictionary](docs/data_dictionary_full.md)**

<br>

Fields / Columns that are un-necessary were deleted, leaving these :

## 📊 Key Fields (Compact Data Dictionary)

These fields represent the core attributes used for cohort analysis, LTV modeling, customer segmentation, and revenue forecasting:
| Field                       | Description                                                                  |
|-----------------------------|------------------------------------------------------------------------------|
| **id**                      | Unique internal transaction ID (primary key).                               |
| **customer_id**             | Unique customer identifier for segmentation, cohorts, and LTV.              |
| **net_amount**              | Total top-up value credited to the wallet (transaction volume, not revenue).|
| **fee_internal_amount**     | Platform’s internal fee revenue per transaction (used for LTV).             |
| **fee_external_amount**     | Fee paid to banks/payment partners (reduces net revenue).                   |
| **category**                | Bank/payment category used (BRI, BNI, Mandiri).                             |
| **transaction_date**        | Timestamp of completed top-up transaction (used for recency, cohorts, forecasting). |
| **year_month**              | Derived monthly period (`YYYY-MM`) used for aggregation and trend analysis. |
| **cohort_month**            | Derived field indicating the customer’s first transaction month (used for cohorts). |
| **created_at**              | System timestamp for record creation.                                       |

<br>

From those, there are two helper columns generated : 

## 🔧 Derived Date Columns (Feature Engineering)

These analytical fields were engineered from the raw `paying_at` timestamp to enable monthly trend analysis, cohort grouping, and forecasting:

| Column           | Description                                                              |
|------------------|--------------------------------------------------------------------------|
| **year_month**   | `YYYY-MM` format used for monthly aggregation and time-series analysis.  |
| **cohort_month** | The customer’s first transaction month, used to assign cohort groups.    |

These features do not exist in the raw dataset—they were created to support cohort analysis, LTV modeling, revenue trends, and actionable business insights.

<br><br>

---

<br><br>

# Platform Scale and Momentum

### 01 — Monthly Platform Usage Volume  
**Business question:**  
*How much money flows through the platform each month, and is usage momentum sustained?*

#### Method
- Aggregate monthly wallet top-up volume (`net_amount`)
- Group transactions by `year_month`
- Measure total platform usage (not revenue)

<p align="center">
  <img src="images/Duitku_01_Monthly_Platform_Usage_Volume .png" width="85%">
</p>

#### Key Insights
- Platform usage **ramped rapidly** from August to October, peaking in October (~3.4B IDR)
- Usage **declined consistently** from November through January
- Indicates strong early adoption but **weak usage sustainability**
- Suggests growth driven by a short-term surge rather than durable retention
  
<br><br>
---
<br><br>

### 02 — Monthly Revenue and Performance Growth  
**Business question:**  
*Is platform revenue growing sustainably month-to-month, and where does momentum break?*

#### Method
- Aggregate monthly platform revenue using `fee_internal_amount`
- Group transactions by `year_month`
- Visualize:
  - **Bars:** total monthly revenue (IDR)
  - **Line:** month-over-month (MoM) revenue growth (capped to reduce distortion)

<p align="center">
  <img src="images/Duitku_02_Monthly_Revenue_Performance_and_Growth.png" width="85%">
</p>

#### Key Insights
- Early MoM growth is driven by launch effects, not durable momentum
- Growth rate declines almost immediately after onboarding phase
- Revenue peaks after momentum has already stalled
- Negative MoM growth post-October confirms structural slowdown

<br><br>
---
<br><br>

### 03 — Revenue vs Transaction Volume  
**Business question:**  
*Is revenue growth driven by higher transaction volume, or by improved monetization efficiency?*

#### Method
- Aggregate monthly **transaction volume** using `net_amount`
- Aggregate monthly **platform revenue** using `fee_internal_amount`
- Group data by `year_month`
- Visualize:
  - **Bars:** total customer load / transaction volume (IDR)
  - **Line:** platform revenue (IDR)

<p align="center">
  <img src="images/Duitku_03_Revenue_vs_Transaction_Volume.png" width="85%">
</p>

#### Key Insights
- Revenue closely tracks transaction volume across all months
- Both revenue and volume peak in October, then decline in tandem
- Post-October slowdown shows no monetization offset — revenue falls as usage falls
- Indicates revenue is **volume-dependent**, not efficiency-driven

<br><br>
---
<br><br>

# Growth Quality

### 04 — Growth Quality: Acquisition vs Retention  
**Business question:**  
*Is platform growth driven by new user acquisition, or by retaining existing users over time?*

#### Method
- Classify customers each month:
  - **New:** first-ever transaction occurs in that month
  - **Returning:** customer has transacted in a prior month
- Count distinct customers by classification per `year_month`
- Visualize:
  - **Bars:** new customers
  - **Stacked bars:** returning customers layered on top

<p align="center">
  <img src="images/Duitku_04_Growth_Quality_Acquisition_vs_Retention.png" width="85%">
</p>

#### Key Insights
- Early growth (August–October) is **primarily acquisition-driven**
- Returning customers increase into October but **never dominate total growth**
- After October, **both acquisition and retention decline simultaneously**
- Indicates weak growth quality: new users are **not converting into a stable returning base**

<br><br>
---
<br><br>

### 05 — Customer Retention Quality by Acquisition Period  
**Business question:**  
*How well do different acquisition cohorts retain customers over time, and how quickly does churn set in?*

#### Method
- Assign customers to a **cohort month** based on their first-ever transaction
- Track customer activity month-by-month after acquisition
- For each cohort and cohort age:
  - Calculate **retention rate (%)**
  - Count **active users**
  - Sum **internal fee revenue**
- Visualize results as a cohort heatmap:
  - **Color:** retention percentage
  - **Text:** users retained and revenue generated per cohort cell
    
<p align="center">
  <img src="images/Duitku_05_Customer_Retention_Quality_by_Acquisition_Period.png" width="100%">
</p>

#### Key Insights
- Retention drops **sharply after Month 0** across all cohorts
- Most cohorts retain **less than 20%** of users by Month 2–3
- Later-month activity is driven by **very small user counts**, not broad engagement
- Revenue persists briefly despite churn, indicating spend concentration among few survivors
- No cohort shows sustained long-term retention strength

<br><br>
---
<br><br>

### 06 — Customer Value and Usage Segmentation  
**Business question:**  
*Which customer segments drive platform value, and how concentrated is usage?*

<br>

#### Method

<br>

**Per-customer metrics**

| Metric | Definition |
|------|-----------|
| **Top-up frequency** | Count of transactions (`id`) |
| **Average top-up amount** | Mean of `net_amount` |
| **Total top-up volume** | Sum of `net_amount` |

<br>

**Customer segmentation (by total top-up volume percentiles)**

| Segment | Definition |
|-------|------------|
| **Whales** | Top 5% |
| **High Value** | Next 15% |
| **Mass Market** | Middle 60% |
| **Long Tail** | Bottom 20% |

<br>

**Visualization encoding**

| Element | Meaning |
|-------|--------|
| **X-axis** | Top-up frequency |
| **Y-axis** | Average top-up amount |
| **Bubble size + color** | Value segment |

<br>

<p align="center">
  <img src="images/Duitku_06_Customer_Value_and_Usage_Segmentation.png" width="85%">
</p>

#### Key Insights
- Value is **highly concentrated**: a small share of customers sits far from the main cluster
- **Whales (Top 5%)** show **both** higher frequency **and** higher average top-up size
- Most customers cluster in the **low-frequency / low-average-topup** region (Mass + Long Tail)
- High usage alone is not “whale” behavior — whales are **high usage + high ticket size**
- Indicates **whale dependency risk** if top users churn

<br><br>
---
<br><br>

### 07 — Revenue Concentration and Whale Dependency  
**Business question:**  
*How concentrated is platform revenue, and how dependent is the business on high-value (“whale”) customers?*

#### Method

**Revenue concentration analysis**

| Step | Description |
|-----|-------------|
| 1 | Aggregate **total internal fee revenue** per customer (`fee_internal_amount`) |
| 2 | Rank customers from **highest to lowest revenue contribution** |
| 3 | Compute **cumulative % of customers** and **cumulative % of revenue** |
| 4 | Plot a **Pareto (Lorenz) curve** to assess concentration |

**Visualization encoding**

| Element | Meaning |
|--------|---------|
| **X-axis** | Cumulative % of customers (sorted by revenue contribution) |
| **Y-axis** | Cumulative % of total internal fee revenue |
| **Curve** | Revenue concentration across the customer base |
| **Dashed lines** | Reference points for Pareto threshold (e.g. 80% revenue) |

<p align="center">
  <img src="images/Duitku_07_Revenue_Concentration_and_Whale_Dependency.png" width="85%">
</p>

#### Key Insights

| Observation | Implication |
|------------|-------------|
| ~**50.3% of customers generate 80% of revenue** | Revenue concentration is **moderate**, not extreme |
| Platform does **not** exhibit a classic 80/20 Pareto pattern | Dependency is spread beyond a small whale group |
| Top customers matter, but **mass + high-value users jointly drive revenue** | Business risk is lower than whale-heavy models |
| Revenue curve smooths gradually, not sharply | Indicates healthier distribution than fintechs with pure whale reliance |

<br><br>
---
<br><br>

### 08 — Observed Customer Value  
**Business question:**  
*How is customer value distributed across the user base, and how concentrated is platform revenue?*

#### Method

**Observed customer value definition**

| Metric | Definition |
|------|------------|
| **Observed LTV** | Sum of `fee_internal_amount` per customer |
| **Revenue basis** | Internal platform fee only |
| **Observation window** | July 2024 – January 2025 |

**Distribution analysis**

| Statistic | Meaning |
|----------|---------|
| **Mean LTV** | Average customer value (outlier-sensitive) |
| **Median LTV** | Typical customer value |
| **P90 LTV** | Threshold for top 10% highest-value customers |

**Visualization encoding**

| Element | Meaning |
|--------|---------|
| **X-axis** | Observed LTV per customer (IDR) |
| **Y-axis** | Number of customers |
| **Vertical lines** | Mean, Median, and P90 reference values |

<p align="center">
  <img src="images/Duitku_08_Observed_Customer_Value.png" width="85%">
</p>

#### Key Insights

| Observation | Implication |
|------------|-------------|
| LTV distribution is heavily right-skewed | Revenue is concentrated among few customers |
| Median LTV is far below mean LTV | Typical customers generate low value |
| Top 10% (P90) contribute disproportionately | High dependency on high-value users |

<br><br>
---
<br><br>

### 09 — Customer Value Quality by Acquisition Period  
**Business question:**  
*Do customers acquired in different months generate similar long-term value, or does value quality deteriorate across cohorts?*

#### Method
- Assign each customer to a **cohort month** based on their first-ever transaction
- For each cohort:
  - Track **cumulative internal fee revenue per customer** over time
  - Measure value progression by **cohort age (months since acquisition)**
- Visualize:
  - **X-axis:** cohort age (months since acquisition)
  - **Y-axis:** cumulative customer value (internal fee revenue)
  - **Lines:** acquisition cohorts (by cohort month)

<p align="center">
  <img src="images/Duitku_09_Customer_Value_Quality_by_Acquisition_Period.png" width="85%">
</p>

#### Key Insights
- Early cohorts (July–September) show **strong cumulative value growth over time**
- Later cohorts (November–January) exhibit **lower starting value and flatter growth curves**
- Value accumulation **slows meaningfully for newer cohorts**, even at comparable cohort ages
- Indicates **declining customer value quality at acquisition**, not just shorter observation windows

#### Interpretation
- Earlier growth periods acquired **higher-quality customers** with stronger long-term monetization
- Later cohorts generate **less value per customer**, even when they remain active
- Revenue weakness is driven by **both declining retention and declining per-customer value**
- Scaling acquisition without improving customer quality increases **long-term revenue fragility**

<br><br>
---
<br><br>

