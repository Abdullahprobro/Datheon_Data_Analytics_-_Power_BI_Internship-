## 📊 Task 01: Superstore Sales & Profitability Insights (Completed ✅)

An end-to-end retail analytics solution combining an executive Power BI dashboard with a modular Python data pipeline (`pandas`, `matplotlib`, `seaborn`) to transform multi-year retail data (`2015–2018`) into actionable revenue, seasonality, discount sensitivity, and market intelligence across **$2.30M in sales** and **5,009 orders**.

### 🛠️ Tech Stack & Key Terminologies
* **BI & Visualization:** Power BI Desktop (16:9 Dark-Slate Executive Theme)
* **Data Analysis & Scripting:** Python (`pandas`, `numpy`, `matplotlib`, `seaborn`)
* **ETL & Data Engineering:** Power Query & Python Pipeline (Missing-Value Audit, Null Handling, `Order Date` Parsing, `Year-Month` Extraction, Schema Standardization)
* **Core KPIs & DAX Measures:** Total Sales (`$2,297,200.86`), Total Profit (`$286,397.02`), Profit Margin % (`12.47%`), Average Order Value (`$458.61`), Total Orders (`5,009`), Unique Customers (`793`)
* **Core Visuals:** KPI Cards, Dual-Axis Line & Clustered Column Chart, AI Decomposition Tree, Regional Profitability Matrix, Monthly Sales Velocity & Seasonality Plot, Discount vs. Profit Sensitivity Scatter Plot

### 🎯 Business Problem & Goal
* **Business Problem:** Leadership lacked a unified view to track multi-year revenue growth alongside category margin erosion, seasonal demand spikes, and profit losses caused by aggressive discounting.
* **Goal of Task 01:** Centralize core commercial KPIs in Power BI while executing programmatic data cleaning, multi-dimensional grouping (`Category`, `Region`, `Segment`), monthly velocity tracking, and discount sensitivity analysis in Python.

### 💡 5 Executive Takeaways
1. **Strong Revenue Scale vs. Order-Line Loss Rate:** The business generated **$2,297,200.86** in total sales and **$286,397.02** in profit (**12.47%** overall margin) across **5,009 orders** (`$458.61` AOV), though **18.7%** of order lines resulted in a net loss (`Profit < 0`).
2. **Technology Drives Profit; Furniture Suffers Margin Compression:** **Technology** leads in both sales (**$836,154**) and profit (**$145,455**, **17.40%** margin), followed by **Office Supplies** (**$719,047** sales; **$122,491** profit, **17.04%** margin). **Furniture** generates **$742,000** in sales but only **$18,451** in profit (**2.49%** margin).
3. **Aggressive Discounting Turns Margins Negative:** Order lines with discounts yield an overall **`-2.86%`** profit margin, demonstrating that heavy promotional discounting directly erodes profitability—most severely in Furniture.
4. **Sharp Q4 / November Seasonality:** Monthly sales velocity peaks in **November** (**$88,115** average monthly sales) compared to a seasonal low in **February** (**$14,938** average monthly sales), underscoring the need for Q4 inventory and fulfillment readiness.
5. **Consumer Segment & West Region Lead Demand:** The **Consumer** segment generates the largest share of revenue (**$1,161,401**), ahead of **Corporate** (**$706,146**) and **Home Office** (**$429,653**), while the **West** leads regional performance (**$725,458** sales; **14.94%** margin) and **Central** lags (**7.92%** margin).

---

## 📂 Deliverables & Repository Links

### 1. Executive Power BI Dashboard
* **Power BI Report:** [Super stores 12.pbix](https://github.com/Abdullahprobro/Datheon_Data_Analytics_-_Power_BI_Internship-/blob/main/Super%20stores%2012.pbix)

### 2. Python EDA Pipeline & Summary Datasets
* **Python Analysis Script:** [superstore.py](https://github.com/Abdullahprobro/Datheon_Data_Analytics_-_Power_BI_Internship-/blob/main/superstore.py)
* **Category × Region × Segment Summary:** [grouped_category_region_segment.csv](https://github.com/Abdullahprobro/Datheon_Data_Analytics_-_Power_BI_Internship-/blob/main/grouped_category_region_segment.csv)
* **Monthly Sales & Rolling Trend Summary:** [monthly_sales_summary.csv](https://github.com/Abdullahprobro/Datheon_Data_Analytics_-_Power_BI_Internship-/blob/main/monthly_sales_summary.csv)
* **Script Executive Summary:** [executive_summary.md](https://github.com/Abdullahprobro/Datheon_Data_Analytics_-_Power_BI_Internship-/blob/main/executive_summary.md)

### 3. Analytical Visualizations
* **Monthly Sales Velocity & Seasonality:** [monthly_sales_seasonality.png](https://github.com/Abdullahprobro/Datheon_Data_Analytics_-_Power_BI_Internship-/blob/main/monthly_sales_seasonality.png)
* **Discount vs. Profit Sensitivity:** [discount_vs_profit.png](https://github.com/Abdullahprobro/Datheon_Data_Analytics_-_Power_BI_Internship-/blob/main/discount_vs_profit.png)
* **Category Sales & Profit Comparison:** [category_sales_profit.png](https://github.com/Abdullahprobro/Datheon_Data_Analytics_-_Power_BI_Internship-/blob/main/category_sales_profit.png)
* **Customer Segment Sales & Margin:** [segment_sales_margin.png](https://github.com/Abdullahprobro/Datheon_Data_Analytics_-_Power_BI_Internship-/blob/main/segment_sales_margin.png)
* **Regional Sales Performance:** [region_sales.png](https://github.com/Abdullahprobro/Datheon_Data_Analytics_-_Power_BI_Internship-/blob/main/region_sales.png)
* **Calendar Month Seasonality Averages:** [monthly_seasonality_averages.png](https://github.com/Abdullahprobro/Datheon_Data_Analytics_-_Power_BI_Internship-/blob/main/monthly_seasonality_averages.png)

---

## 🗺️ Internship Roadmap
* **Task 01:** Superstore Sales & Profitability Analysis — **Completed ✅**
