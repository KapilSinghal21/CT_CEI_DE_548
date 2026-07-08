"""
clean_data.py
Loads raw CSVs, cleans them, validates integrity, and writes cleaned CSVs
plus a text report of all issues found.

Functions:
- clean_orders(df)
- clean_products(df)
- validate_emails(df)
- check_referential_integrity(orders_df, order_items_df)
"""

import pandas as pd
import re
from datetime import datetime

RAW_DIR = "data/raw"
CLEAN_DIR = "data/cleaned"

ISSUES = [] 


def log_issue(msg):
    ISSUES.append(msg)
    print(msg)


def parse_order_date(value):
    """Try multiple formats and normalize to YYYY-MM-DD HH:MM:SS."""
    if pd.isna(value) or str(value).strip() == "":
        return None
    value = str(value).strip()
    formats = ["%Y-%m-%d %H:%M:%S", "%d-%m-%Y", "%Y-%m-%d"]
    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return None  # unparseable


def clean_orders(df):
    """Fix date formats, handle NULL/missing customer_ids."""
    df = df.copy()

    # Track missing customer_id before fixing
    missing_mask = df["customer_id"].isna() | (df["customer_id"].astype(str).str.strip() == "")
    n_missing = missing_mask.sum()
    if n_missing:
        log_issue(f"[orders] {n_missing} rows had missing customer_id -> set to NULL (kept as NaN)")
    df.loc[missing_mask, "customer_id"] = pd.NA

    # Normalize customer_id to nullable Int64 where possible
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").astype("Int64")

    # Fix date formats
    original_dates = df["order_date"].copy()
    df["order_date"] = df["order_date"].apply(parse_order_date)
    bad_dates = df["order_date"].isna().sum()
    if bad_dates:
        log_issue(f"[orders] {bad_dates} rows had unparseable order_date -> set to NULL")
    fixed_format = (original_dates.astype(str).str.match(r"^\d{2}-\d{2}-\d{4}$")).sum()
    if fixed_format:
        log_issue(f"[orders] {fixed_format} rows had DD-MM-YYYY date format -> normalized to YYYY-MM-DD HH:MM:SS")

    # Flag future dates
    now = datetime.now()
    future_mask = pd.to_datetime(df["order_date"], errors="coerce") > now
    n_future = future_mask.sum()
    if n_future:
        log_issue(f"[orders] {n_future} rows have order_date in the future (flagged, not removed)")

    # Validate status
    valid_statuses = {"PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"}
    invalid_status = ~df["status"].isin(valid_statuses)
    if invalid_status.sum():
        log_issue(f"[orders] {invalid_status.sum()} rows had invalid status values")

    return df


def clean_products(df):
    """Normalize product names (trim spaces, title case)."""
    df = df.copy()
    messy_mask = df["product_name"] != df["product_name"].str.strip().str.title()
    n_messy = messy_mask.sum()
    if n_messy:
        log_issue(f"[products] {n_messy} rows had messy product_name (extra spaces/mixed case) -> normalized")
    df["product_name"] = df["product_name"].str.strip().str.title()

    # De-duplicate whitespace inside name
    df["product_name"] = df["product_name"].apply(lambda x: re.sub(r"\s+", " ", x) if isinstance(x, str) else x)

    return df


def validate_emails(df):
    """Return list of customer_ids with invalid emails."""
    email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    invalid_ids = []
    for _, row in df.iterrows():
        email = str(row["email"])
        if not email_pattern.match(email):
            invalid_ids.append(row["customer_id"])
    if invalid_ids:
        log_issue(f"[customers] {len(invalid_ids)} customer_ids have invalid emails: {invalid_ids[:10]}{'...' if len(invalid_ids) > 10 else ''}")
    return invalid_ids


def check_referential_integrity(orders_df, order_items_df):
    """Find order_items that reference non-existent orders."""
    valid_order_ids = set(orders_df["order_id"])
    orphan_mask = ~order_items_df["order_id"].isin(valid_order_ids)
    orphans = order_items_df.loc[orphan_mask, "item_id"].tolist()
    if orphans:
        log_issue(f"[order_items] {len(orphans)} items reference non-existent order_id: {orphans[:10]}{'...' if len(orphans) > 10 else ''}")
    else:
        log_issue("[order_items] No orphan order_items found (referential integrity OK)")
    return orphans


def clean_order_items(df):
    """Flag negative quantities (returns) and out-of-range discounts, but keep rows."""
    df = df.copy()
    neg_qty = (df["quantity"] < 0).sum()
    if neg_qty:
        log_issue(f"[order_items] {neg_qty} rows have negative quantity (treated as returns, kept)")

    zero_qty = (df["quantity"] == 0).sum()
    if zero_qty:
        log_issue(f"[order_items] {zero_qty} rows have quantity = 0 (flagged as invalid)")

    bad_discount = ((df["discount_percent"] < 0) | (df["discount_percent"] > 100)).sum()
    if bad_discount:
        log_issue(f"[order_items] {bad_discount} rows have discount_percent outside 0-100 (flagged)")
        df["discount_percent"] = df["discount_percent"].clip(lower=0, upper=100)

    return df


def main():
    customers = pd.read_csv(f"{RAW_DIR}/customers.csv", dtype={"customer_id": "Int64"})
    products = pd.read_csv(f"{RAW_DIR}/products.csv")
    orders = pd.read_csv(f"{RAW_DIR}/orders.csv", dtype={"customer_id": "object"})
    order_items = pd.read_csv(f"{RAW_DIR}/order_items.csv")

    log_issue("=== DATA CLEANING REPORT ===")

    orders_clean = clean_orders(orders)
    products_clean = clean_products(products)
    order_items_clean = clean_order_items(order_items)

    invalid_email_ids = validate_emails(customers)
    orphan_items = check_referential_integrity(orders_clean, order_items_clean)

    # Drop orphan order_items (no matching order) from cleaned output
    if orphan_items:
        order_items_clean = order_items_clean[~order_items_clean["item_id"].isin(orphan_items)]

    # Remove duplicate rows across all tables
    for name, df in [("customers", customers), ("products", products_clean),
                      ("orders", orders_clean), ("order_items", order_items_clean)]:
        dupes = df.duplicated().sum()
        if dupes:
            log_issue(f"[{name}] {dupes} duplicate rows found -> removed")

    customers = customers.drop_duplicates()
    products_clean = products_clean.drop_duplicates()
    orders_clean = orders_clean.drop_duplicates()
    order_items_clean = order_items_clean.drop_duplicates()

    customers.to_csv(f"{CLEAN_DIR}/customers_clean.csv", index=False)
    products_clean.to_csv(f"{CLEAN_DIR}/products_clean.csv", index=False)
    orders_clean.to_csv(f"{CLEAN_DIR}/orders_clean.csv", index=False)
    order_items_clean.to_csv(f"{CLEAN_DIR}/order_items_clean.csv", index=False)

    with open("output/data_quality_report.txt", "w") as f:
        f.write("\n".join(ISSUES))

    print("\nCleaned files written to data/cleaned/")
    print("Report written to output/data_quality_report.txt")


if __name__ == "__main__":
    main()
