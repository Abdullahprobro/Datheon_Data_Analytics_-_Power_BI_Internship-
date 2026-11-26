"""
Superstore Sales Analysis
=========================
Data Analytics & Business Intelligence project.

Pipeline
--------
1. Load & inspect the dataset (encoding-safe, column verification)
2. Clean data + engineer dates (Year, Month, Month_Name, Year-Month) and
   analytical fields (Profit_Margin, order/customer volume metrics)
3. Aggregate by Category / Region / Segment and by Year-Month
4. Export CSV summaries + high-resolution PNG charts
5. Print an executive summary of key findings

Author: DA/BI Project
Date  : 2026-11-26
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# --------------------------------------------------------------------------- #
# 0. CONFIGURATION                                                            #
# --------------------------------------------------------------------------- #
INPUT_FILE = "superstore_sales (2).csv"
OUTPUT_DIR = "superstore_analysis"



os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cohesive visual style
sns.set_theme(style="whitegrid", palette="tab10")
plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 300,           # high-resolution PNG output
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# Columns that are critical for the analysis -> rows missing these are dropped
CRITICAL_COLS = ["Order Date", "Sales", "Profit", "Discount"]
# Candidate encodings tried in order when reading the CSV
ENCODINGS = ["utf-8", "latin-1", "ISO-8859-1", "cp1252"]


# --------------------------------------------------------------------------- #
# 1. DATA LOADING & INSPECTION                                                #
# --------------------------------------------------------------------------- #
def load_data(filepath):
    """Load the CSV safely, trying common encodings; verify required columns."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Input file not found: {filepath}")

    df = None
    for enc in ENCODINGS:
        try:
            df = pd.read_csv(filepath, encoding=enc)
            print(f"[INFO] Loaded with encoding: {enc}")
            break
        except UnicodeDecodeError:
            print(f"[WARN] Encoding {enc} failed, trying next...")
            continue

    if df is None:
        raise ValueError("Could not decode the file with any known encoding.")

    df.columns = df.columns.str.strip()  # normalise stray whitespace
    return df


def inspect_data(df):
    """Print shape, columns, dtypes, summary stats and missing-value audit."""
    print("\n" + "=" * 70)
    print("1. DATA INSPECTION")
    print("=" * 70)
    print(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print("\nColumns:", list(df.columns))
    print("\nData types:\n", df.dtypes)

    print("\nSummary statistics (numeric):\n", df.describe().round(2))

    # Missing-value audit: absolute counts + percentage
    missing = pd.DataFrame({
        "Missing_Count": df.isnull().sum(),
        "Missing_Pct": (df.isnull().sum() / len(df) * 100).round(2),
    }).sort_values("Missing_Count", ascending=False)
    print("\nMissing-value audit:\n", missing)


# --------------------------------------------------------------------------- #
# 2. DATA CLEANING & DATE ENGINEERING                                         #
# --------------------------------------------------------------------------- #
def clean_data(df):
    """Handle missing values, duplicates, dtypes, and engineer date fields."""
    print("\n" + "=" * 70)
    print("2. DATA CLEANING & DATE ENGINEERING")
    print("=" * 70)
    n0 = len(df)

    # --- Numeric coercion ---------------------------------------------------
    for col in ["Sales", "Profit", "Discount", "Quantity"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # --- Drop rows missing critical fields ----------------------------------
    crit_missing = df[CRITICAL_COLS].isnull().any(axis=1).sum()
    df = df.dropna(subset=CRITICAL_COLS).copy()
    print(f"[CLEAN] Dropped {crit_missing} rows missing critical fields "
          f"({', '.join(CRITICAL_COLS)})")

    # --- Handle non-critical missing values ----------------------------------
    if "Postal Code" in df.columns:
        n_pc = df["Postal Code"].isnull().sum()
        if n_pc > 0:
            df["Postal Code"] = df["Postal Code"].fillna("Unknown")
            print(f"[CLEAN] Imputed {n_pc} missing 'Postal Code' -> 'Unknown'")

    # Generic imputation for remaining low-stakes text columns
    for col in df.select_dtypes(include="object").columns:
        n_miss = df[col].isnull().sum()
        if n_miss > 0:
            df[col] = df[col].fillna("Unknown")
            print(f"[CLEAN] Imputed {n_miss} missing '{col}' -> 'Unknown'")

    # --- Duplicates ----------------------------------------------------------
    n_dup = df.duplicated().sum()
    if n_dup > 0:
        df = df.drop_duplicates().copy()
    print(f"[CLEAN] Removed {n_dup} duplicate rows")

    # --- Date parsing ---------------------------------------------------------
    for dcol in ["Order Date", "Ship Date"]:
        if dcol in df.columns:
            df[dcol] = pd.to_datetime(df[dcol], errors="coerce")
            n_bad = df[dcol].isnull().sum()
            if n_bad > 0:
                print(f"[CLEAN] {dcol}: {n_bad} unparseable values dropped")
                df = df.dropna(subset=[dcol]).copy()

    # --- Date engineering -----------------------------------------------------
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month
    df["Month_Name"] = df["Order Date"].dt.month_name()
    df["Year-Month"] = df["Order Date"].dt.strftime("%Y-%m")  # clean YYYY-MM

    # --- Analytical fields ----------------------------------------------------
    # Profit margin (guard against zero-sales division)
    with np.errstate(divide="ignore", invalid="ignore"):
        df["Profit_Margin"] = np.where(df["Sales"] != 0,
                                       df["Profit"] / df["Sales"], np.nan)

    # Order-level volume metrics
    order_value = df.groupby("Order ID")["Sales"].transform("sum")
    df["Order_Total_Value"] = order_value
    n_orders = df["Order ID"].nunique()
    n_customers = df["Customer ID"].nunique() if "Customer ID" in df.columns else np.nan
    lines_per_order = df.groupby("Order ID").size()
    df["Lines_Per_Order"] = df["Order ID"].map(lines_per_order)

    # Customer lifetime purchase volume (total spend per customer)
    if "Customer ID" in df.columns:
        cust_spend = df.groupby("Customer ID")["Sales"].transform("sum")
        df["Customer_Total_Spend"] = cust_spend

    print(f"[CLEAN] Final shape: {df.shape[0]:,} rows x {df.shape[1]} columns "
          f"(removed {n0 - len(df):,} rows overall)")
    print(f"[INFO] Unique orders: {n_orders:,} | Unique customers: {n_customers:,}")
    return df


# --------------------------------------------------------------------------- #
# 3. AGGREGATIONS & GROUPINGS                                                 #
# --------------------------------------------------------------------------- #
def aggregate(df):
    """Build all summary tables and export them as CSV."""
    print("\n" + "=" * 70)
    print("3. AGGREGATIONS & GROUPINGS")
    print("=" * 70)

    def build_summary(frame, keys):
        g = frame.groupby(keys, observed=True).agg(
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Total_Quantity=("Quantity", "sum"),
            Order_Count=("Order ID", "nunique"),
        ).reset_index()
        g["Profit_Margin_Pct"] = np.where(
            g["Total_Sales"] != 0,
            (g["Total_Profit"] / g["Total_Sales"] * 100).round(2), np.nan)
        g = g.sort_values("Total_Sales", ascending=False)
        return g

    # Combined grouping: Category x Region x Segment
    grp_crs = build_summary(df, ["Category", "Region", "Segment"])
    grp_crs.to_csv(os.path.join(OUTPUT_DIR, "grouped_category_region_segment.csv"),
                   index=False)
    print("\n-- Category x Region x Segment --\n",
          grp_crs.head(15).to_string(index=False))

    # Standalone summaries
    summaries = {
        "category": build_summary(df, ["Category"]),
        "region": build_summary(df, ["Region"]),
        "segment": build_summary(df, ["Segment"]),
    }
    for name, tbl in summaries.items():
        print(f"\n-- {name.title()} summary --\n", tbl.to_string(index=False))

    # Monthly summary (for seasonality)
    monthly = df.groupby("Year-Month", observed=True).agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Total_Quantity=("Quantity", "sum"),
        Order_Count=("Order ID", "nunique"),
    ).reset_index().sort_values("Year-Month")
    monthly["Profit_Margin_Pct"] = np.where(
        monthly["Total_Sales"] != 0,
        (monthly["Total_Profit"] / monthly["Total_Sales"] * 100).round(2), np.nan)
    monthly["Sales_MA3"] = monthly["Total_Sales"].rolling(3).mean()
    monthly.to_csv(os.path.join(OUTPUT_DIR, "monthly_sales_summary.csv"),
                   index=False)
    print("\n-- Monthly sales summary (first 12) --\n",
          monthly.head(12).to_string(index=False))

    return grp_crs, summaries, monthly


# --------------------------------------------------------------------------- #
# 4. VISUALIZATIONS                                                           #
# --------------------------------------------------------------------------- #
def save_fig(fig, filename):
    """Save figure cleanly: tight layout, high-res PNG, then close."""
    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"[PLOT] Saved -> {path}")


def plot_monthly_sales(monthly):
    """Monthly sales velocity & seasonality with peaks highlighted."""
    fig, ax = plt.subplots(figsize=(14, 6))
    x = pd.to_datetime(monthly["Year-Month"], format="%Y-%m")

    ax.plot(x, monthly["Total_Sales"], marker="o", lw=2, color="#1f77b4",
            label="Monthly Sales")
    ax.plot(x, monthly["Sales_MA3"], lw=2, ls="--", color="#ff7f0e",
            label="3-Month Rolling Avg")
    ax.bar(x, monthly["Total_Profit"], width=18, color="#2ca02c",
           alpha=0.35, label="Monthly Profit")

    # Highlight seasonal peaks (top-3 sales months)
    top_idx = monthly["Total_Sales"].nlargest(3).index
    for i in top_idx:
        ax.annotate(f"{monthly.loc[i, 'Year-Month']}\n"
                    f"${monthly.loc[i, 'Total_Sales']:,.0f}",
                    xy=(x.loc[i], monthly.loc[i, "Total_Sales"]),
                    xytext=(0, 22), textcoords="offset points",
                    ha="center", fontsize=9, fontweight="bold",
                    color="#d62728",
                    arrowprops=dict(arrowstyle="->", color="#d62728"))

    ax.set_title("Monthly Sales Velocity & Seasonality")
    ax.set_xlabel("Month")
    ax.set_ylabel("USD")
    ax.yaxis.set_major_formatter(lambda v, _: f"${v/1000:,.0f}K")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    ax.legend(loc="upper left")
    save_fig(fig, "monthly_sales_seasonality.png")


def plot_discount_vs_profit(df):
    """Discount sensitivity scatter, coloured by Category, zero-profit line."""
    fig, ax = plt.subplots(figsize=(11, 7))
    cats = sorted(df["Category"].dropna().unique())
    palette = sns.color_palette("tab10", len(cats))

    for cat, color in zip(cats, palette):
        sub = df[df["Category"] == cat]
        ax.scatter(sub["Discount"], sub["Profit"], s=28, alpha=0.55,
                   color=color, edgecolors="white", linewidths=0.3, label=cat)

    ax.axhline(0, color="black", lw=1.2, ls="--")
    ax.text(0.01, ax.get_ylim()[1] * 0.02, "Break-even (Profit = 0)",
            fontsize=9, style="italic")

    # Annotate the loss-heavy discount band if visible in the data
    loss_df = df[df["Profit"] < 0]
    if len(loss_df):
        med = loss_df["Discount"].median()
        ax.axvline(med, color="#d62728", lw=1, ls=":",
                   label=f"Median loss discount = {med:.0%}")

    ax.set_title("Discount vs. Profit by Category (Discount Sensitivity)")
    ax.set_xlabel("Discount")
    ax.set_ylabel("Profit (USD)")
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0%}")
    ax.legend(title="Category", loc="best")
    save_fig(fig, "discount_vs_profit.png")


def plot_category_segment_charts(summaries):
    """Supporting comparisons: category & segment sales/profit bars."""
    # --- Category: Sales & Profit side-by-side ---------------------------
    cat = summaries["category"].sort_values("Total_Sales", ascending=False)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    sns.barplot(data=cat, x="Category", y="Total_Sales", ax=axes[0],
                hue="Category", palette="Blues_d", legend=False)
    sns.barplot(data=cat, x="Category", y="Total_Profit", ax=axes[1],
                hue="Category", palette="Greens_d", legend=False)
    axes[0].set_title("Total Sales by Category")
    axes[1].set_title("Total Profit by Category")
    for ax in axes:
        ax.set_ylabel("USD")
        ax.yaxis.set_major_formatter(lambda v, _: f"${v/1000:,.0f}K")
        for p in ax.patches:
            ax.annotate(f"{p.get_height()/1000:,.0f}K",
                        (p.get_x() + p.get_width() / 2, p.get_height()),
                        ha="center", va="bottom", fontsize=9)
    save_fig(fig, "category_sales_profit.png")

    # --- Segment: Sales & Profit margin -----------------------------------
    seg = summaries["segment"].sort_values("Total_Sales", ascending=False)
    fig, ax1 = plt.subplots(figsize=(9, 5))
    sns.barplot(data=seg, x="Segment", y="Total_Sales", ax=ax1,
                hue="Segment", palette="rocket", legend=False)
    ax1.set_ylabel("Total Sales (USD)")
    ax1.yaxis.set_major_formatter(lambda v, _: f"${v/1000:,.0f}K")
    ax2 = ax1.twinx()
    ax2.plot(seg["Segment"], seg["Profit_Margin_Pct"], color="black",
             marker="D", lw=2, ls="--", label="Profit Margin %")
    ax2.set_ylabel("Profit Margin (%)")
    ax1.set_title("Segment: Sales Volume vs. Profitability")
    ax2.legend(loc="upper right")
    save_fig(fig, "segment_sales_margin.png")

    # --- Region: Sales -----------------------------------------------------
    reg = summaries["region"].sort_values("Total_Sales", ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=reg, x="Region", y="Total_Sales", ax=ax,
                hue="Region", palette="viridis", legend=False)
    ax.set_title("Total Sales by Region")
    ax.set_ylabel("USD")
    ax.yaxis.set_major_formatter(lambda v, _: f"${v/1000:,.0f}K")
    save_fig(fig, "region_sales.png")


def plot_seasonality_averages(df):
    """Average sales by calendar month across all years (seasonal pattern)."""
    m = df.groupby("Month", observed=True).agg(
        Avg_Sales=("Sales", "mean"),
        Total_Sales=("Sales", "sum"),
    ).reset_index()
    m["Month_Name"] = pd.to_datetime(m["Month"], format="%m").dt.month_name()

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=m, x="Month_Name", y="Avg_Sales", ax=ax,
                hue="Month_Name", palette="coolwarm", legend=False)
    ax.set_title("Average Order-Line Sales by Calendar Month "
                 "(Seasonal Pattern)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Avg Sales per Line (USD)")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    save_fig(fig, "monthly_seasonality_averages.png")


# --------------------------------------------------------------------------- #
# 5. EXECUTIVE SUMMARY                                                        #
# --------------------------------------------------------------------------- #
def executive_summary(df, summaries, monthly):
    """Print key numeric findings for direct use in README.md."""
    print("\n" + "=" * 70)
    print("5. EXECUTIVE SUMMARY")
    print("=" * 70)

    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    overall_margin = total_profit / total_sales * 100 if total_sales else np.nan
    aov = df.groupby("Order ID")["Sales"].sum().mean()

    cat = summaries["category"].sort_values("Total_Sales", ascending=False)
    top_cat_sales = cat.iloc[0]
    bot_cat_sales = cat.iloc[-1]
    cat_p = summaries["category"].sort_values("Total_Profit", ascending=False)
    top_cat_profit, bot_cat_profit = cat_p.iloc[0], cat_p.iloc[-1]

    reg = summaries["region"].sort_values("Total_Sales", ascending=False)
    seg = summaries["segment"].sort_values("Total_Sales", ascending=False)

    monthly["Month_Num"] = pd.to_datetime(
        monthly["Year-Month"], format="%Y-%m").dt.month
    season = monthly.groupby("Month_Num")["Total_Sales"].mean()
    peak_month = season.idxmax()
    low_month = season.idxmin()
    peak_name = pd.Timestamp(2000, peak_month, 1).month_name()
    low_name = pd.Timestamp(2000, low_month, 1).month_name()

    # Discount impact
    loss = df[df["Profit"] < 0]
    loss_share = len(loss) / len(df) * 100
    no_disc = df[df["Discount"] == 0]
    with_disc = df[df["Discount"] > 0]
    margin_no = no_disc["Profit"].sum() / no_disc["Sales"].sum() * 100
    margin_yes = (with_disc["Profit"].sum() / with_disc["Sales"].sum() * 100
                  if len(with_disc) else np.nan)

    print(f"""
- Total Sales        : ${total_sales:,.2f}
- Total Profit       : ${total_profit:,.2f}
- Overall Margin     : {overall_margin:.2f}%
- Avg Order Value    : ${aov:,.2f}
- Orders / Customers : {df['Order ID'].nunique():,} / {df['Customer ID'].nunique():,}

- Top category by sales    : {top_cat_sales['Category']} (${top_cat_sales['Total_Sales']:,.0f})
- Bottom category by sales : {bot_cat_sales['Category']} (${bot_cat_sales['Total_Sales']:,.0f})
- Top category by profit   : {top_cat_profit['Category']} (${top_cat_profit['Total_Profit']:,.0f})
- Weakest category profit  : {bot_cat_profit['Category']} (${bot_cat_profit['Total_Profit']:,.0f})

- Best region  : {reg.iloc[0]['Region']} (${reg.iloc[0]['Total_Sales']:,.0f})
- Best segment : {seg.iloc[0]['Segment']} (${seg.iloc[0]['Total_Sales']:,.0f})

- Peak seasonality month   : {peak_name} (avg ${season.max():,.0f}/month)
- Weakest seasonality month: {low_name} (avg ${season.min():,.0f}/month)

- Discount impact:
    * {loss_share:.1f}% of order lines are loss-making (Profit < 0)
    * Profit margin with NO discount : {margin_no:.2f}%
    * Profit margin WITH discounts   : {margin_yes:.2f}%
""")

    # Also persist the summary as Markdown-ready text
    md_path = os.path.join(OUTPUT_DIR, "executive_summary.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"""# Superstore Sales - Executive Summary

- **Total Sales**: ${total_sales:,.2f}
- **Total Profit**: ${total_profit:,.2f}
- **Overall Profit Margin**: {overall_margin:.2f}%
- **Average Order Value**: ${aov:,.2f}
- **Orders / Customers**: {df['Order ID'].nunique():,} / {df['Customer ID'].nunique():,}

| Dimension | Leader | Value |
|-----------|--------|-------|
| Category (sales) | {top_cat_sales['Category']} | ${top_cat_sales['Total_Sales']:,.0f} |
| Category (profit) | {top_cat_profit['Category']} | ${top_cat_profit['Total_Profit']:,.0f} |
| Region | {reg.iloc[0]['Region']} | ${reg.iloc[0]['Total_Sales']:,.0f} |
| Segment | {seg.iloc[0]['Segment']} | ${seg.iloc[0]['Total_Sales']:,.0f} |

- **Peak season**: {peak_name} | **Weakest month**: {low_name}
- **Discount impact**: {loss_share:.1f}% of lines are loss-making;
  margin {margin_no:.2f}% (no discount) vs {margin_yes:.2f}% (discounted).
""")
    print(f"[INFO] Markdown summary saved -> {md_path}")


# --------------------------------------------------------------------------- #
# MAIN                                                                        #
# --------------------------------------------------------------------------- #
def main():
    try:
        df = load_data(INPUT_FILE)
        inspect_data(df)
        df = clean_data(df)
        grp_crs, summaries, monthly = aggregate(df)

        print("\n" + "=" * 70)
        print("4. VISUALIZATIONS")
        print("=" * 70)
        plot_monthly_sales(monthly)
        plot_discount_vs_profit(df)
        plot_category_segment_charts(summaries)
        plot_seasonality_averages(df)

        executive_summary(df, summaries, monthly)
        print("\n[DONE] All outputs written to:", OUTPUT_DIR)
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()