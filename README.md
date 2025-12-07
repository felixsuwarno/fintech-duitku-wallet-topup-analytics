# fintech-duitku-wallet-topup-analytics
Python analysis of real Duitku digital wallet top-up data. Includes customer behavior insights, cohort analysis, LTV modeling, and revenue forecasting. End-to-end FinTech analytics workflow built from raw transactions to actionable business insights.

# FinTech "Duitku" Wallet Top-Up Analytics: Customer Behavior, Cohort Insights, LTV & Revenue Forecasting

A Python-powered analysis of real digital wallet transaction data from **Duitku**, an Indonesian payment gateway.

---

<br><br>

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

The goal is to support real-world FinTech decision-making with data-driven insights.

---

<br><br>

## Dataset

The original dataset can be downloaded here:

- [transactions.xlsx (Zenodo)](https://zenodo.org/records/17092322/files/transactions.xlsx?download=1)

---

<br><br>

## 📊 Key Fields (Compact Data Dictionary)

The full data dictionary can be seen here :
[Full Data Dictionary](docs/data_dictionary_full.md)

The followings are the core fields used in cohort analysis, LTV modeling, and revenue forecasting:

| Field | Description |
|-------|-------------|
| **id** | Unique internal transaction ID (primary key). |
| **customer_id** | Unique user identifier for segmentation, cohorts, and LTV. |
| **net_amount** | Total top-up value credited to the wallet (main revenue driver). |
| **fee_internal_amount** | Platform’s internal fee revenue per transaction (used for LTV). |
| **fee_external_amount** | Fee paid to banks/payment partners (reduces net revenue). |
| **category** | Bank/payment category used (BRI, BNI, Mandiri). |
| **status** | Transaction status (`00` = successful). |
| **paying_at** | Timestamp of payment completion (used for `year_month`, cohorts, and forecasting). |
| **channel** | Top-up channel (`DUITKU` payment gateway). |
| **reference_number** | Payment processor transaction ID. |
| **channel_reference_number** | Reference number from the payment gateway. |
| **created_at / updated_at** | System timestamps for record creation and updates. |

<br><br>

## 🔧 Derived Date Columns

From the `paying_at` timestamp, two key analytical fields were created to support monthly trends, cohort grouping, and revenue forecasting:

| Column           | Description                                                              |
|------------------|--------------------------------------------------------------------------|
| **year_month**   | `YYYY-MM` format used for monthly aggregation and time-series analysis.  |
| **cohort_month** | The customer’s first transaction month, used to assign cohort groups.    |

These engineered columns do not exist in the raw dataset—they are created to enable cohort analysis, customer value tracking, and month-over-month revenue insights.






| **type** | Transaction type (`TOP_UP` for all rows). |
| **journal_type** | Ledger classification (`CREDIT` for all top-ups). |
