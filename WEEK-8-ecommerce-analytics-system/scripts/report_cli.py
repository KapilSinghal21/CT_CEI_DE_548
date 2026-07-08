"""
report_cli.py
Command-line reporting tool for the e-commerce analytics system.
Uses sqlite3

Usage:
    python3 report_cli.py --type daily --start 2025-01-01 --end 2025-01-31
    python3 report_cli.py --type monthly --start 2025-01-01 --end 2025-03-31
    python3 report_cli.py            (interactive prompt mode)
"""

import sqlite3
import sys
import argparse
from datetime import datetime, timedelta

DB_PATH = "ecommerce.db"
VALID_TYPES = ["daily", "weekly", "monthly"]


def get_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        sys.exit(1)


def parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        print(f"Invalid date format: '{s}'. Expected YYYY-MM-DD.")
        sys.exit(1)


def previous_period(start, end):
    """Return the equivalent previous period of the same length."""
    delta = end - start
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - delta
    return prev_start, prev_end


def fetch_summary(conn, start, end):
    start_s = start.strftime("%Y-%m-%d")
    end_s = end.strftime("%Y-%m-%d 23:59:59")

    row = conn.execute("""
        SELECT
            COUNT(DISTINCT o.order_id) AS total_orders,
            COALESCE(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)), 0) AS revenue,
            COUNT(DISTINCT o.customer_id) AS unique_customers
        FROM orders o
        LEFT JOIN order_items oi ON oi.order_id = o.order_id AND oi.quantity > 0
        WHERE o.order_date BETWEEN ? AND ?
    """, (start_s, end_s)).fetchone()

    total_orders, revenue, unique_customers = row
    revenue = round(revenue or 0, 2)

    top_products = conn.execute("""
        SELECT p.product_name, SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent / 100.0)) AS rev
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        JOIN products p ON p.product_id = oi.product_id
        WHERE o.order_date BETWEEN ? AND ? AND oi.quantity > 0
        GROUP BY p.product_name
        ORDER BY rev DESC
        LIMIT 3
    """, (start_s, end_s)).fetchall()

    return {
        "total_orders": total_orders or 0,
        "revenue": revenue,
        "unique_customers": unique_customers or 0,
        "top_products": [(name, round(rev, 2)) for name, rev in top_products],
    }


def pct_change(current, previous):
    if previous == 0:
        return None
    return round((current - previous) * 100.0 / previous, 2)


def print_report(report_type, start, end, current, previous):
    print("=" * 55)
    print(f"  {report_type.upper()} REPORT: {start.date()} to {end.date()}")
    print("=" * 55)
    print(f"Total Orders     : {current['total_orders']}")
    print(f"Total Revenue    : {current['revenue']}")
    print(f"Unique Customers : {current['unique_customers']}")
    print("\nTop 3 Products:")
    if current["top_products"]:
        for name, rev in current["top_products"]:
            print(f"  - {name}: {rev}")
    else:
        print("  (no product sales in this period)")

    print("\nComparison with previous period:")
    for key, label in [("total_orders", "Orders"), ("revenue", "Revenue"), ("unique_customers", "Customers")]:
        change = pct_change(current[key], previous[key])
        change_str = f"{change}%" if change is not None else "N/A (no previous data)"
        print(f"  {label} change: {change_str}")
    print("=" * 55)


def run_report(report_type, start_str, end_str):
    if report_type not in VALID_TYPES:
        print(f"Invalid report type '{report_type}'. Must be one of {VALID_TYPES}.")
        sys.exit(1)

    start = parse_date(start_str)
    end = parse_date(end_str)
    if end < start:
        print("End date must not be before start date.")
        sys.exit(1)

    conn = get_connection()
    current = fetch_summary(conn, start, end)

    prev_start, prev_end = previous_period(start, end)
    previous = fetch_summary(conn, prev_start, prev_end)

    print_report(report_type, start, end, current, previous)
    conn.close()


def interactive_mode():
    report_type = input(f"Report type {VALID_TYPES}: ").strip().lower()
    start_str = input("Start date (YYYY-MM-DD): ").strip()
    end_str = input("End date (YYYY-MM-DD): ").strip()
    run_report(report_type, start_str, end_str)


def main():
    parser = argparse.ArgumentParser(description="E-commerce analytics report CLI")
    parser.add_argument("--type", choices=VALID_TYPES, help="Report type")
    parser.add_argument("--start", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", help="End date YYYY-MM-DD")
    args = parser.parse_args()

    if args.type and args.start and args.end:
        run_report(args.type, args.start, args.end)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
