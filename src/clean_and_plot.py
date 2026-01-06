from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

df = pd.read_csv(DATA_DIR / "dirty_cafe_sales.csv")


# Normalize fake missing values
fake_missing = [
    "NA", "N/A", "null", "NULL", "None",
    "", " ", "-", "?",
    "Unknown", "UNKNOWN", "unknown",
    "ERROR", "Error", "error", "nan"
]
df.replace(fake_missing, pd.NA, inplace=True)

# Clean and convert Price Per Unit
df["Price Per Unit"] = df["Price Per Unit"].astype(str)
df["Price Per Unit"] = (
    df["Price Per Unit"]
    .str.replace(",", "")
    .str.replace("₹", "")
    .str.replace("$", "")
)
df["Price Per Unit"] = pd.to_numeric(df["Price Per Unit"], errors="coerce")

# Convert Quantity
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")

# Clean and convert Total Spent
df["Total Spent"] = df["Total Spent"].astype(str)
df["Total Spent"] = (
    df["Total Spent"]
    .str.replace(",", "")
    .str.replace("₹", "")
    .str.replace("$", "")
)
df["Total Spent"] = pd.to_numeric(df["Total Spent"], errors="coerce")

# Convert Transaction Date
df["Transaction Date"] = pd.to_datetime(
    df["Transaction Date"], errors="coerce"
)

# Standardize column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Fill price per unit within item groups (where possible)
df["price_per_unit"] = df["price_per_unit"].fillna(
    df.groupby("item")["price_per_unit"].transform("first")
)

# Fill categorical missing values
df["payment_method"] = df["payment_method"].fillna("unknown")
df["location"] = df["location"].fillna("unknown")

# Drop rows with critical missing values
df.dropna(subset=["transaction_date"], inplace=True)

# Compute total
df["computed_total"] = df["price_per_unit"] * df["quantity"]

df.dropna(subset=["price_per_unit"], inplace=True)
df["item"] = df["item"].fillna("unknown_item")
df.dropna(subset=["quantity"], inplace=True)

# Fill total_spent from computed_total
df["total_spent"] = df["total_spent"].fillna(df["computed_total"])

# Report percentage of unknowns
unk = ["item", "payment_method", "location"]
total_rows = len(df)

for col in unk:
    unknown_count = df[col].isin(["unknown", "unknown_item"]).sum()
    percent = (unknown_count / total_rows) * 100
    print(f"{col}: {percent:.2f}% unknown")

# Save cleaned data
df.to_csv("cleaned_cafe_sales.csv", index=False)

# =====================
# PLOTS
# =====================

df1 = pd.read_csv("cleaned_cafe_sales.csv")

# Bar chart: Top 10 items by revenue
revenue_by_item = (
    df1.groupby("item")["total_spent"]
       .sum()
       .sort_values(ascending=False)
       .head(10)
)

plt.figure()
revenue_by_item.plot(kind="bar")
plt.title("Top 10 Items by Revenue")
plt.ylabel("Total Revenue")
plt.xlabel("Item")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("plots/top_items_bar.png", bbox_inches="tight")
plt.show()

# Pie chart: Top 5 items revenue share
revenue_by_item = (
    df1.groupby("item")["total_spent"]
       .sum()
       .sort_values(ascending=False)
       .head(5)
)

plt.figure()
plt.pie(
    revenue_by_item,
    labels=revenue_by_item.index,
    autopct="%1.1f%%",
    startangle=90
)
plt.title("Revenue Share by Top 5 Items")
plt.axis("equal")
plt.savefig("plots/revenue_share_pie.png", bbox_inches="tight")
plt.show()