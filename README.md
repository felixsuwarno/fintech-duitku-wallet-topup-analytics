# FinTech “Duitku” Wallet Top-Up Analytics  
**Customer Behavior • Cohorts • LTV • Revenue Forecasting**

Python analysis of real **Duitku** digital wallet top-up transactions.  
This project extracts behavioral insights, builds customer cohorts, models LTV, and forecasts monthly revenue.  
An end-to-end FinTech analytics workflow built from raw transactions to business-ready insights.

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

---

<br>

## 📊 Key Fields (Compact Data Dictionary)

These fields represent the core attributes used for cohort analysis, LTV modeling, customer segmentation, and revenue forecasting:

| Field                       | Description                                                                  |
|-----------------------------|------------------------------------------------------------------------------|
| **id**                      | Unique internal transaction ID (primary key).                               |
| **customer_id**             | Unique user identifier for segmentation, cohorts, and LTV.                  |
| **reference_number**        | Payment processor transaction ID for each top-up.                           |
| **net_amount**              | Total top-up value credited to the wallet (main revenue driver).            |
| **fee_internal_amount**     | Platform’s internal fee revenue per transaction (used for LTV).             |
| **fee_external_amount**     | Fee paid to banks/payment partners (reduces net revenue).                   |
| **category**                | Bank/payment category used (BRI, BNI, Mandiri).                             |
| **paying_at**               | Timestamp of payment completion (used for `year_month`, cohorts, forecasting). |
| **channel**                 | Top-up channel (`DUITKU` payment gateway).                                  |
| **created_at / updated_at** | System timestamps for record creation and updates.                           |

---

<br>

## 🔧 Derived Date Columns (Feature Engineering)

These analytical fields were engineered from the raw `paying_at` timestamp to enable monthly trend analysis, cohort grouping, and forecasting:

| Column           | Description                                                              |
|------------------|--------------------------------------------------------------------------|
| **year_month**   | `YYYY-MM` format used for monthly aggregation and time-series analysis.  |
| **cohort_month** | The customer’s first transaction month, used to assign cohort groups.    |

These features do not exist in the raw dataset—they were created to support cohort analysis, LTV modeling, revenue trends, and actionable business insights.



