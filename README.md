# E-Commerce Sales Analytics Dashboard

A complete end-to-end data analytics and customer segmentation dashboard for e-commerce transactional data, utilizing the Online Retail dataset to derive actionable business metrics, segment customers via RFM analysis, perform cohort retention tracking, and cluster customer profiles using KMeans machine learning.

## Business Problem
How can an e-commerce company analyze its historical transaction log (500k+ rows) to track high-level sales KPIs, find seasonality, identify top products/customers, analyze customer retention trends, and target different customer segments with tailored marketing strategies?

---

## Folder Structure

```
ecommerce_dashboard/
├── charts/                 # Saved visualization charts (14 PNGs)
├── data/                   # Raw transaction dataset (OnlineRetail.csv)
├── models/                 # Serialized ML models, RFM tables, and KPI exports
├── app.py                  # Interactive Multi-Page Streamlit Dashboard
├── download_data.py        # Automated data downloader script
├── ecommerce_analysis.ipynb # Step-by-step Jupyter analysis notebook
├── generate_notebook.py    # Notebook generator script
├── requirements.txt        # Python libraries dependencies list
└── README.md               # Project documentation (this file)
```

---

## Tech Stack

| Component | Library/Tool | Description |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core language environment |
| **Storage & Prep** | Pandas, Numpy, Openpyxl | Data loading, parsing, cleaning, and preprocessing |
| **Visualizations** | Matplotlib, Seaborn, Plotly Express | Static notebook charts and interactive dashboard charts |
| **Machine Learning** | Scikit-Learn (KMeans, StandardScaler) | Unsupervised clustering of customer segments |
| **Model Persistence**| Joblib | Saving KMeans model and standard scaling transformer |
| **Web Dashboard** | Streamlit | Interactive 5-page dashboard application |

---

## Dataset Description

*   **Name:** Online Retail Dataset (UCI Machine Learning Repository)
*   **Period:** 01 Dec 2010 — 09 Dec 2011 (approx. 1 year)
*   **Rows:** 541,909 transactions (raw)
*   **Columns:** 8 attributes:
    1.  `InvoiceNo`: Transaction identifier (cancellations prefixed with 'C')
    2.  `StockCode`: Product code
    3.  `Description`: Product name
    4.  `Quantity`: Units sold per transaction
    5.  `InvoiceDate`: Transaction timestamp
    6.  `UnitPrice`: Price per unit in GBP (£)
    7.  `CustomerID`: Unique customer identifier
    8.  `Country`: Customer location

---

## How to Install and Run

### 1. Clone or Copy the Workspace files
Ensure you are in the project folder containing `requirements.txt`.

### 2. Install Dependencies
Install all required libraries using pip:
```bash
pip install -r requirements.txt
```

### 3. Download the Dataset
Run the data downloader script to fetch the Online Retail dataset automatically:
```bash
python download_data.py
```

### 4. Run the Analysis Notebook
Open and execute all cells of the Jupyter Notebook to compute metrics, train machine learning clustering, and save visualizations/models:
```bash
jupyter notebook ecommerce_analysis.ipynb
```
*(Alternatively, you can run all cells using VS Code or any standard Jupyter interface)*

### 5. Launch the Streamlit Dashboard
Run the interactive application:
```bash
python -m streamlit run app.py
```
Open the local URL (usually `http://localhost:8501`) in your browser to explore the dashboard.

---

## Key Business Metrics (KPIs)

*   **Total Revenue:** £9,747,747.93 (approx. £9.75M)
*   **Total Orders:** 22,064 orders
*   **Total Customers:** 4,338 unique customers
*   **Total Products:** 3,877 unique stock items
*   **Avg Order Value (AOV):** £419.00
*   **Top Country (by Revenue):** United Kingdom (represents ~84% of revenue)

---

## List of Generated Charts

During execution of the analysis notebook, the following 14 charts are auto-saved to `charts/`:

1.  `01_monthly_revenue.png`: Chronological monthly revenue trend line chart, highlighting the peak revenue month (November 2011).
2.  `02_day_hour_revenue.png`: Dual subplot showing revenue by day of the week (Thursdays peak) and revenue distribution by hour of day (peaks between 10 AM and 3 PM).
3.  `03_top_products.png`: Horizontal bar chart listing the top 10 products contributing the most to revenue.
4.  `04_country_revenue.png`: Dual visualization: bar chart of top 10 non-UK countries and a pie chart showing global revenue shares.
5.  `05_top_customers.png`: Bar chart of the top 10 highest-spending customers by ID.
6.  `06_orders_aov.png`: Chronological monthly orders count bar chart coupled with the monthly Average Order Value (AOV) trend.
7.  `07_order_distribution.png`: Histogram and boxplot showing the distribution of individual order values, excluding outliers (top 1%).
8.  `08_quarterly_revenue.png`: Chronological quarterly revenue comparison showcasing retail growth over time.
9.  `09_rfm_segments.png`: Subplots presenting customer count distribution and revenue contribution across RFM segments.
10. `10_rfm_scatter.png`: Scatter plot plotting Recency vs Monetary value, colored by RFM segment to show customer progression.
11. `11_cohort_analysis.png`: Heatmap of monthly customer cohort retention rates (relative percentage of returning customers index-by-month).
12. `12_elbow_method.png`: Elbow curve plotting K-means inertia to determine the optimal number of clusters ($k=4$).
13. `13_customer_clusters.png`: Scatter plots showing KMeans customer clusters across Recency vs Monetary and Frequency vs Monetary axes.
14. `14_product_analysis.png`: Subplots analyzing the top 10 products by quantity sold and the top 10 products by transaction count.

---

## RFM Customer Segments

Customers are scored on a scale of 1-5 for Recency (R), Frequency (F), and Monetary (M), then segmented by their total score:

*   **Champions (Score $\ge$ 13):** Bought recently, buy often, and spend the most. Reward them.
*   **Loyal Customers (Score 10 - 12):** Spend good money and buy regularly. Optimize upselling.
*   **Potential Loyalists (Score 7 - 9):** Recent customers with average frequency. Offer loyalty programs.
*   **At Risk (Score 5 - 6):** Spent big and bought often, but a long time ago. Run reactivation campaigns.
*   **Lost Customers (Score $<$ 5):** Lowest recency, frequency, and monetary scores. Avoid expensive targeting.

---

## Cohort Analysis Explanation

The cohort analysis groups customers based on the month of their very first transaction (Cohort Month). For each cohort, we track what percentage of those specific customers return to make a purchase in subsequent months (Cohort Index).
*   **Column 0** is always 100% (the activation month).
*   **Column 1** shows month-1 retention. E-commerce benchmarks target at least 20% retention here. Higher retention indicates strong customer loyalty and product-market fit.
