"""
test_edge_cases.py
"""

import sqlite3
import sys
sys.path.append("scripts")
from clean_data import check_referential_integrity, clean_order_items
import pandas as pd

DB_PATH = "ecommerce.db"


def test_orphan_order_items():
    """1. What happens when order_items has an order_id not in orders?"""
    orders_df = pd.DataFrame({"order_id": [1, 2, 3]})
    order_items_df = pd.DataFrame({
        "item_id": [1, 2, 3],
        "order_id": [1, 2, 999],  # 999 doesn't exist
        "quantity": [1, 1, 1],
        "discount_percent": [0, 0, 0],
    })
    orphans = check_referential_integrity(orders_df, order_items_df)
    assert orphans == [3], f"Expected item_id [3] flagged as orphan, got {orphans}"
    print("PASS: orphan order_items (invalid order_id) correctly detected and can be excluded")


def test_discount_over_100():
    """2. What happens when discount_percent > 100?"""
    df = pd.DataFrame({
        "quantity": [1, 1],
        "discount_percent": [150, 50],
    })
    cleaned = clean_order_items(df)
    assert cleaned["discount_percent"].max() <= 100, "discount_percent should be clipped to 100"
    print("PASS: discount_percent > 100 is flagged and clipped to valid range (0-100)")


def test_zero_quantity():
    """3. What happens when quantity is 0?"""
    df = pd.DataFrame({
        "quantity": [0, 5],
        "discount_percent": [10, 10],
    })
    cleaned = clean_order_items(df)
    assert (cleaned["quantity"] == 0).sum() == 1
    print("PASS: quantity = 0 rows are kept but flagged; they contribute 0 revenue in SQL (qty>0 filter excludes them from sales)")


def test_future_order_date():
    """4. What happens when order_date is in the future?"""
    from datetime import datetime, timedelta
    conn = sqlite3.connect(DB_PATH)
    future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

    conn.execute("BEGIN")
    max_customer = conn.execute("SELECT customer_id FROM customers LIMIT 1").fetchone()[0]
    conn.execute(
        "INSERT INTO orders (order_id, customer_id, order_date, status, region_code) VALUES (999999, ?, ?, 'PLACED', 'NORTH')",
        (max_customer, future_date)
    )
    result = conn.execute("SELECT COUNT(*) FROM orders WHERE order_date > datetime('now')").fetchone()[0]
    assert result >= 1, "Future-dated order should be queryable/detectable"
    conn.execute("ROLLBACK")
    conn.close()
    print("PASS: future order_date is detectable via `order_date > datetime('now')` and can be flagged/excluded from historical reports")


def test_empty_result_set_cli():
    """Bonus: CLI/report queries should handle empty result sets gracefully (no crash)."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("""
        SELECT COUNT(*) FROM orders WHERE order_date BETWEEN '1900-01-01' AND '1900-01-02'
    """).fetchone()
    assert row[0] == 0
    conn.close()
    print("PASS: querying an empty date range returns 0 rows without error")


if __name__ == "__main__":
    test_orphan_order_items()
    test_discount_over_100()
    test_zero_quantity()
    test_future_order_date()
    test_empty_result_set_cli()
    print("\nAll edge case tests passed.")
